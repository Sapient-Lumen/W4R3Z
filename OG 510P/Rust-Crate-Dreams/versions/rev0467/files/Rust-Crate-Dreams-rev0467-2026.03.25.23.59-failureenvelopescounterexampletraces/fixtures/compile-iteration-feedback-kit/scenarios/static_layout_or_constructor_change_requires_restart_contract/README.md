# Scenario — static layout or constructor changes require a restart contract

This scenario exists because some edits can keep a process alive while others alter globals, constructors, or layout-sensitive assumptions enough that a clean restart is the honest path.

The point of this fixture is to keep **state continuity** explicit instead of flattening every successful patch attempt into “state was preserved”.
