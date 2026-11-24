"""Tests for the audited money module (Doc 3.1, Doc 10.2)."""

import ast
import re
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.core import money
from app.core.money import ensure_paise, format_inr, from_rupees, parse_inr

# Far beyond any personal amount, and far beyond float's exact-integer range (2**53).
BIG = 10**18
paise_values = st.integers(min_value=-BIG, max_value=BIG)

INDIAN_GROUPED = re.compile(r"^-?\d{1,2}(,\d{2})*,\d{3}\.\d{2}$|^-?\d{1,3}\.\d{2}$")


# ---------------------------------------------------------------- parse_inr
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1,23,456.78", 12_345_678),
        ("123,456.78", 12_345_678),  # Western grouping (some bank statements)
        ("123456.78", 12_345_678),
        ("300", 30_000),
        ("300.5", 30_050),  # one decimal means tens of paise
        ("300.05", 30_005),
        ("0.01", 1),
        ("0", 0),
        ("-1,000.00", -100_000),
        ("+50.00", 5_000),
        ("  1,000.00  ", 100_000),
        ("1,00,00,000.00", 1_000_000_000),
    ],
)
def test_parse_inr_valid(text: str, expected: int) -> None:
    assert parse_inr(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "abc",
        "1.234",  # more than 2 decimals: refuse rather than round
        "1,,000",
        ",100",
        "100,",
        "1.",
        ".50",
        "1e5",
        "Rs 100",  # callers strip currency symbols
        "₹100",
        "--1",
        "1 000",
        "١٢٣",  # Arabic-Indic digits are not ASCII digits
        "NaN",
        "inf",
    ],
)
def test_parse_inr_rejects_invalid(text: str) -> None:
    with pytest.raises(ValueError):
        parse_inr(text)


@pytest.mark.parametrize("value", [100, 1.5, None, b"100"])
def test_parse_inr_rejects_non_strings(value: object) -> None:
    with pytest.raises(TypeError):
        parse_inr(value)  # type: ignore[arg-type]


def test_parse_inr_is_exact_beyond_float_precision() -> None:
    # 2**53 + 1 paise cannot be represented exactly as a float.
    assert parse_inr("9,00,71,99,25,47,409.93") == 2**53 + 1
    assert format_inr(2**53 + 1) == "9,00,71,99,25,47,409.93"


# ---------------------------------------------------------------- format_inr
@pytest.mark.parametrize(
    ("paise", "expected"),
    [
        (0, "0.00"),
        (1, "0.01"),
        (10, "0.10"),
        (100, "1.00"),
        (99_999, "999.99"),
        (100_000, "1,000.00"),
        (12_345_678, "1,23,456.78"),
        (1_000_000_000, "1,00,00,000.00"),
        (-15_000, "-150.00"),
        (-12_345_678, "-1,23,456.78"),
    ],
)
def test_format_inr(paise: int, expected: str) -> None:
    assert format_inr(paise) == expected


def test_format_inr_without_grouping() -> None:
    assert format_inr(12_345_678, grouping=False) == "123456.78"
    assert format_inr(30_000, grouping=False) == "300.00"


@pytest.mark.parametrize("value", [1.0, Decimal("1"), True, "100", None])
def test_format_inr_rejects_non_int(value: object) -> None:
    with pytest.raises(TypeError):
        format_inr(value)  # type: ignore[arg-type]


# ---------------------------------------------------------------- helpers
def test_from_rupees() -> None:
    assert from_rupees(300) == 30_000
    with pytest.raises(TypeError):
        from_rupees(3.5)  # type: ignore[arg-type]


def test_ensure_paise_rejects_bool_and_float() -> None:
    assert ensure_paise(5) == 5
    for bad in (True, 5.0, Decimal("5")):
        with pytest.raises(TypeError):
            ensure_paise(bad)


# ---------------------------------------------------------------- properties
@given(paise_values)
def test_format_then_parse_round_trips(paise: int) -> None:
    assert parse_inr(format_inr(paise)) == paise
    assert parse_inr(format_inr(paise, grouping=False)) == paise


@given(paise_values)
def test_format_uses_indian_grouping(paise: int) -> None:
    assert INDIAN_GROUPED.fullmatch(format_inr(paise))


@given(paise_values)
def test_grouping_only_adds_commas(paise: int) -> None:
    assert format_inr(paise).replace(",", "") == format_inr(paise, grouping=False)


@given(
    st.integers(min_value=0, max_value=BIG),
    st.integers(min_value=0, max_value=99),
)
def test_parse_matches_decimal_reference(rupees: int, paise: int) -> None:
    # Independent reference implementation using Decimal (Doc 10.2 differential check).
    text = f"{rupees}.{paise:02d}"
    assert parse_inr(text) == int(Decimal(text) * 100)


@given(paise_values, paise_values)
def test_sum_of_parsed_equals_parse_of_sum(a: int, b: int) -> None:
    assert parse_inr(format_inr(a)) + parse_inr(format_inr(b)) == parse_inr(format_inr(a + b))


# ---------------------------------------------------------------- no floats (Doc 10.2)
def test_money_module_contains_no_floating_point() -> None:
    source = Path(money.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            assert not isinstance(node.value, float), f"float literal at line {node.lineno}"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "float", f"float() call at line {node.lineno}"
        if isinstance(node, ast.BinOp):
            assert not isinstance(node.op, ast.Div), f"true division at line {node.lineno}"
