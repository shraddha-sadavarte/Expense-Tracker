import 'dart:io';
import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:hisaab/core/money/paise.dart';

void main() {
  group('Paise.parse', () {
    const valid = <String, int>{
      '1,23,456.78': 12345678,
      '123,456.78': 12345678,
      '123456.78': 12345678,
      '300': 30000,
      '300.5': 30050,
      '300.05': 30005,
      '0.01': 1,
      '0': 0,
      '-1,000.00': -100000,
      '+50.00': 5000,
      '  1,000.00  ': 100000,
      '1,00,00,000.00': 1000000000,
    };
    valid.forEach((text, expected) {
      test('parses "$text"', () {
        expect(Paise.parse(text), Paise(expected));
      });
    });

    const invalid = [
      '', ' ', 'abc', '1.234', '1,,000', ',100', '100,', '1.', '.50',
      '1e5', 'Rs 100', '₹100', '--1', '1 000', '١٢٣', 'NaN',
    ];
    for (final text in invalid) {
      test('rejects "$text"', () {
        expect(() => Paise.parse(text), throwsFormatException);
        expect(Paise.tryParse(text), isNull);
      });
    }

    test('is exact beyond double precision (2^53 + 1)', () {
      const big = 9007199254740993;
      expect(Paise.parse('9,00,71,99,25,47,409.93'), const Paise(big));
      expect(const Paise(big).format(), '9,00,71,99,25,47,409.93');
    });
  });

  group('Paise.format', () {
    const cases = <int, String>{
      0: '0.00',
      1: '0.01',
      10: '0.10',
      100: '1.00',
      99999: '999.99',
      100000: '1,000.00',
      12345678: '1,23,456.78',
      1000000000: '1,00,00,000.00',
      -15000: '-150.00',
    };
    cases.forEach((paise, expected) {
      test('formats $paise', () => expect(Paise(paise).format(), expected));
    });

    test('without grouping', () {
      expect(const Paise(12345678).format(grouping: false), '123456.78');
    });

    test('display adds rupee sign', () {
      expect(const Paise(30000).display(), '₹300.00');
      expect(const Paise(-15000).display(), '-₹150.00');
    });
  });

  group('arithmetic', () {
    test('add, subtract, compare', () {
      const a = Paise(85000);
      const b = Paise(30000);
      expect(a + b, const Paise(115000));
      expect((a + b) - const Paise(100000), const Paise(15000));
      expect(a > b, isTrue);
      expect(const Paise.fromRupees(1000), const Paise(100000));
    });
  });

  group('properties (randomised, fixed seed)', () {
    final random = Random(42);
    int nextAmount() {
      // Up to ~10^15 paise, both signs.
      final high = random.nextInt(1 << 30);
      final low = random.nextInt(1 << 20);
      final v = high * (1 << 20) + low;
      return random.nextBool() ? v : -v;
    }

    test('format then parse round-trips', () {
      for (var i = 0; i < 5000; i++) {
        final p = Paise(nextAmount());
        expect(Paise.parse(p.format()), p);
        expect(Paise.parse(p.format(grouping: false)), p);
      }
    });

    test('grouping only adds commas', () {
      for (var i = 0; i < 5000; i++) {
        final p = Paise(nextAmount());
        expect(p.format().replaceAll(',', ''), p.format(grouping: false));
      }
    });
  });

  test('money module contains no double', () {
    final source = File('lib/core/money/paise.dart').readAsStringSync();
    final code = source
        .split('\n')
        .where((line) => !line.trimLeft().startsWith('//'))
        .join('\n');
    expect(code.contains(RegExp(r'\bdouble\b')), isFalse);
    expect(code.contains(RegExp(r'\bnum\b')), isFalse);
    expect(code.contains('toDouble'), isFalse);
  });
}
