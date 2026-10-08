# Scenario: release adds a new safe constructor and requires review

The old release only allowed one private constructor to establish a length invariant.
The new release adds a public safe constructor that claims to validate inputs.
The important diff is not “new API added” in the abstract; it is that **trusted constructor** and possibly **mutation authority** changed.
