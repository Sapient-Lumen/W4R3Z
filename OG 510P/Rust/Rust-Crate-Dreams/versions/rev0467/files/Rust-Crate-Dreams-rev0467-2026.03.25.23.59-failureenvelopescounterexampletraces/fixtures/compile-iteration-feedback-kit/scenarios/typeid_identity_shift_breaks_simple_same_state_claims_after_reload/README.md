# Scenario — `TypeId` identity drift breaks simple same-state claims after reload

`hot-lib-reloader` docs explicitly note that `TypeId`-sensitive systems can become harder to serialize/deserialize because types receive different ids after reload.

So a compile-iteration bundle should not flatten:
- “some state was carried forward”,
- “same identities still hold”,
- and “no rebinding or migration is needed”.
