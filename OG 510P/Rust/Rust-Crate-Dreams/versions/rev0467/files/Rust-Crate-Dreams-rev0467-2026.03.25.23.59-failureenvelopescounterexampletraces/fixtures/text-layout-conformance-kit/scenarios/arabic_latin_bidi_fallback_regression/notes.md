# Scenario: Arabic + Latin bidi fallback regression

An Arabic sentence with embedded Latin text and numerals is laid out under constrained width.
The purpose is to catch regressions where bidi resolution, fallback family choice, or width measurement changes the chosen line breaks or glyph-run families.
