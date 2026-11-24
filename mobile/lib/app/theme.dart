import 'package:material_ui/material_ui.dart';

/// Material 3 theme. Seed colour is a placeholder until the design is ready.
abstract final class AppTheme {
  static const Color _seed = Color(0xFF1B6E5A);

  static ThemeData light() => _build(Brightness.light);
  static ThemeData dark() => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final scheme = ColorScheme.fromSeed(seedColor: _seed, brightness: brightness);
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      // Doc 10.8: touch targets at least 48 dp.
      materialTapTargetSize: MaterialTapTargetSize.padded,
      visualDensity: VisualDensity.standard,
    );
  }
}
