/// The single audited money type for the app (BLUEPRINT Doc 3.1, Doc 9.6).
///
/// Money is always integer paise. This file never uses `double`: parsing works
/// on the decimal string and formatting uses integer division only.
library;

final RegExp _amountPattern =
    RegExp(r'^([+-]?)([0-9]+(?:,[0-9]+)*)(?:\.([0-9]{1,2}))?$');

/// An amount of money in integer paise (1 rupee = 100 paise).
final class Paise implements Comparable<Paise> {
  const Paise(this.value);

  /// Whole rupees. Fractional rupees must go through [Paise.parse].
  const Paise.fromRupees(int rupees) : value = rupees * paisePerRupee;

  static const int paisePerRupee = 100;
  static const Paise zero = Paise(0);

  final int value;

  /// Parses "1,23,456.78" (Indian or Western grouping) into 12345678 paise.
  ///
  /// At most two decimal places; more is an error, never a silent rounding.
  /// Currency symbols are not accepted; strip them first.
  static Paise parse(String text) {
    final match = _amountPattern.firstMatch(text.trim());
    if (match == null) {
      throw FormatException('Not a valid amount', text);
    }
    final sign = match.group(1)!;
    final rupees = int.parse(match.group(2)!.replaceAll(',', ''));
    final paise = int.parse((match.group(3) ?? '').padRight(2, '0'));
    final total = rupees * paisePerRupee + paise;
    return Paise(sign == '-' ? -total : total);
  }

  /// Like [parse] but returns null instead of throwing.
  static Paise? tryParse(String text) {
    try {
      return parse(text);
    } on FormatException {
      return null;
    }
  }

  /// "1,23,456.78" (Indian grouping), or "123456.78" with `grouping: false`.
  String format({bool grouping = true}) {
    final sign = value < 0 ? '-' : '';
    final absolute = value.abs();
    final rupees = absolute ~/ paisePerRupee;
    final rem = absolute % paisePerRupee;
    final whole = grouping ? _groupIndian(rupees.toString()) : rupees.toString();
    return '$sign$whole.${rem.toString().padLeft(2, '0')}';
  }

  /// Display string with the rupee sign, e.g. "₹1,23,456.78".
  String display() => value < 0 ? '-₹${(-this).format()}' : '₹${format()}';

  Paise operator +(Paise other) => Paise(value + other.value);
  Paise operator -(Paise other) => Paise(value - other.value);
  Paise operator -() => Paise(-value);
  bool operator <(Paise other) => value < other.value;
  bool operator <=(Paise other) => value <= other.value;
  bool operator >(Paise other) => value > other.value;
  bool operator >=(Paise other) => value >= other.value;

  bool get isNegative => value < 0;

  @override
  int compareTo(Paise other) => value.compareTo(other.value);

  @override
  bool operator ==(Object other) => other is Paise && other.value == value;

  @override
  int get hashCode => value.hashCode;

  @override
  String toString() => 'Paise($value)';
}

/// "12345678" -> "1,23,45,678": last three digits, then pairs.
String _groupIndian(String digits) {
  if (digits.length <= 3) return digits;
  var head = digits.substring(0, digits.length - 3);
  final tail = digits.substring(digits.length - 3);
  final parts = <String>[];
  while (head.length > 2) {
    parts.insert(0, head.substring(head.length - 2));
    head = head.substring(0, head.length - 2);
  }
  parts.insert(0, head);
  return '${parts.join(',')},$tail';
}
