# Scenario — emoji ZWJ backspace breaks grapheme-cluster selection

This scenario models a text field where naïve scalar deletion corrupts a user-visible emoji sequence.
The point is to keep **selection truth** honest:

- backspace should respect grapheme-cluster boundaries,
- replacement ranges should not split a visible emoji sequence mid-cluster,
- and the report should clearly say whether the engine is cluster-safe or only scalar-safe.
