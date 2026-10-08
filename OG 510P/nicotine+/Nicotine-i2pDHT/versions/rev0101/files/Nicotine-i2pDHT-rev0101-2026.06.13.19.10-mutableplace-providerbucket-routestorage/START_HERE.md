# START HERE — rev0101 mutableplace-providerbucket-routestorage

Read `docs/1048-rev0101-mutableplace-providerbucket-routestorage.md` first.

Useful local checks:

```bash
pytest tests/test_rev0100_recordingress_providersemantics_routingspine.py tests/test_rev0101_mutableplace_providerbucket_routestorage.py
python scripts/evidence/run_micro_simulation.py
python scripts/evidence/run_cube_audit.py
```

rev0101 extends the Python-owned generic I2P DHT substrate with three placement gates:

- `mutableplacement`: signed mutable-head observations are placed locally without claiming latestness.
- `providerbucket`: semantic provider claims enter bounded provider-index buckets without storing content or claiming truth.
- `routestorage`: I2P-bound contacts enter local route storage or replacement cache without garden/introducer authority.

Audit spine: `substratespine` and `substrateplacementfold` preserve rev0100 `substratecenturyfold` history while making rev0101 visible as the current substrate-placement branch.

Historical anchors retained: rev0080 rev0081 rev0082 rev0083 rev0084 rev0085 rev0086 rev0087 rev0088 rev0089 rev0090 rev0091 rev0092 rev0093 rev0094 rev0095 rev0096 rev0097 rev0098 rev0099 rev0100 rev0101 importsettlementfold nativeboundaryfold nativeparityfold nativedispatchfold nativebudgetfold nativeprovenancefold nativeselectionfold nativelifecyclefold nativecontrolfold nativecoldfold nativehandofffold nativereentryfold nativeloadreentryfold nativeloadloopfold nativeshadowfold nativesettlementfold nativearchivefold nativearchivereplayfold nativebranchclosefold substratereturnfold recordplaneoracle substratereentry recordingress providersemantics routinganchor mutableplacement providerbucket routestorage substratespine substratecenturyfold substrateplacementfold nativefoldspine.

Full revision anchors retained: rev0024 rev0025 rev0026 rev0027 rev0028 rev0029 rev0030 rev0031 rev0032 rev0033 rev0034 rev0035 rev0036 rev0037 rev0038 rev0039 rev0040 rev0041 rev0042 rev0043 rev0044 rev0045 rev0046 rev0047 rev0048 rev0049 rev0050 rev0051 rev0052 rev0053 rev0054 rev0055 rev0056 rev0057 rev0058 rev0059 rev0060 rev0061 rev0062 rev0063 rev0064 rev0065 rev0066 rev0067 rev0068 rev0069 rev0070 rev0071 rev0072 rev0073 rev0074 rev0075 rev0076 rev0077 rev0078 rev0079 rev0080 rev0081 rev0082 rev0083 rev0084 rev0085 rev0086 rev0087 rev0088 rev0089 rev0090 rev0091 rev0092 rev0093 rev0094 rev0095 rev0096 rev0097 rev0098 rev0099 rev0100 rev0101.

Fold needles retained: summarydeliveryfold summaryackfold summaryreplayfold summaryexportreceiptfold importsettlementfold nativeboundaryfold nativeparityfold nativedispatchfold nativebudgetfold nativeprovenancefold nativeselectionfold nativelifecyclefold nativecontrolfold nativecoldfold nativehandofffold nativereentryfold nativeloadreentryfold nativeloadloopfold nativeshadowfold nativesettlementfold nativearchivefold nativearchivereplayfold nativebranchclosefold substratereturnfold substratecenturyfold substrateplacementfold nativefoldspine substratespine.

rev0100 predecessor anchors retained: recordingress providersemantics routinganchor substratecenturyfold substratespine.

rev0099 predecessor anchors retained again: recordplaneoracle substratereentry substratereturnfold nativebranchclosefold nativefoldspine.
