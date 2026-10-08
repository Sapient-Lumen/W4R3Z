# Nicotine i2pDHT rev0101 — mutableplace-providerbucket-routestorage

Current artifact: `Nicotine-i2pDHT-rev0101-2026.06.13.19.10-mutableplace-providerbucket-routestorage`.

rev0101 continues the post-native-return substrate path. rev0100 admitted records through Python-owned record ingress, provider semantics, and I2P routing anchors; rev0101 decides whether those accepted records may become local placement state.

Read first: `docs/1048-rev0101-mutableplace-providerbucket-routestorage.md`.

Current code:

- `src/i2p_dht_lab/mutableplacement.py`
- `src/i2p_dht_lab/providerbucket.py`
- `src/i2p_dht_lab/routestorage.py`
- `src/i2p_dht_lab/substratespine.py`
- `src/i2p_dht_lab/substrateplacementfold.py`

Current tests: `tests/test_rev0101_mutableplace_providerbucket_routestorage.py`.

Strong rule: an accepted DHT record is not local state until placement, bucket admission, or route storage preserves hard-negative memory at the exact boundary.

Native/GCC posture retained: Python owns protocol truth, parsing, crypto, transport, persistence finality, policy, moderation, mutability, provider semantics, routing semantics, and exact-boundary joins. GCC-native remains shadow-only unless a future explicit branch is opened.

Substrate spine anchors: rev0099 rev0100 rev0101 recordplaneoracle substratereentry substratereturnfold recordingress providersemantics routinganchor mutableplacement providerbucket routestorage substratespine substratecenturyfold substrateplacementfold nativefoldspine.

Historical native fold anchors: rev0080 rev0081 rev0082 rev0083 rev0084 rev0085 rev0086 rev0087 rev0088 rev0089 rev0090 rev0091 rev0092 rev0093 rev0094 rev0095 rev0096 rev0097 rev0098 rev0099 importsettlementfold nativeboundaryfold nativeparityfold nativedispatchfold nativebudgetfold nativeprovenancefold nativeselectionfold nativelifecyclefold nativecontrolfold nativecoldfold nativehandofffold nativereentryfold nativeloadreentryfold nativeloadloopfold nativeshadowfold nativesettlementfold nativearchivefold nativearchivereplayfold nativebranchclosefold substratereturnfold nativefoldspine.

Full historical revision anchors: rev0024 rev0025 rev0026 rev0027 rev0028 rev0029 rev0030 rev0031 rev0032 rev0033 rev0034 rev0035 rev0036 rev0037 rev0038 rev0039 rev0040 rev0041 rev0042 rev0043 rev0044 rev0045 rev0046 rev0047 rev0048 rev0049 rev0050 rev0051 rev0052 rev0053 rev0054 rev0055 rev0056 rev0057 rev0058 rev0059 rev0060 rev0061 rev0062 rev0063 rev0064 rev0065 rev0066 rev0067 rev0068 rev0069 rev0070 rev0071 rev0072 rev0073 rev0074 rev0075 rev0076 rev0077 rev0078 rev0079 rev0080 rev0081 rev0082 rev0083 rev0084 rev0085 rev0086 rev0087 rev0088 rev0089 rev0090 rev0091 rev0092 rev0093 rev0094 rev0095 rev0096 rev0097 rev0098 rev0099 rev0100 rev0101.
