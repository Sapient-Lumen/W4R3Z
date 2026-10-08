# Native fold spine audit/refactor

The native line now spans many revisions. rev0090 adds `nativefoldspine.py` so the branch is auditable as one visible chain rather than only through one-off fold modules.

The spine checks the native sequence:

```text
rev0081 nativeboundaryfold
rev0082 nativeparityfold
rev0083 nativedispatchfold
rev0084 nativebudgetfold
rev0085 nativeprovenancefold
rev0086 nativeselectionfold
rev0087 nativelifecyclefold
rev0088 nativecontrolfold
rev0089 nativecoldfold
rev0090 nativehandofffold
```

This does not replace the detailed fold modules. It gives the cube a current native branch map and catches missing anchors in README, START_HERE, and docs index surfaces.
