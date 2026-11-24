import 'package:material_ui/material_ui.dart';

/// Placeholder home screen. No features yet.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Hisaab')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.account_balance_wallet_outlined,
                  size: 64, color: theme.colorScheme.primary),
              const SizedBox(height: 16),
              Text('Hisaab', style: theme.textTheme.headlineMedium),
              const SizedBox(height: 8),
              Text(
                'Foundation ready. Features coming soon.',
                style: theme.textTheme.bodyLarge,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
