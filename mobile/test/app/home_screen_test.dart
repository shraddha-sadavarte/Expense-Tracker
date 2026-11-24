import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hisaab/app/app.dart';

void main() {
  testWidgets('app starts on the placeholder home screen', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: HisaabApp()));
    await tester.pumpAndSettle();
    expect(find.text('Foundation ready. Features coming soon.'), findsOneWidget);
  });
}
