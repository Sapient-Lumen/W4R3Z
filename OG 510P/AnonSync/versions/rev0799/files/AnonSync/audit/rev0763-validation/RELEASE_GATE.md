# rev0763 validation gate

Implementation mode: `FALLBACK_APPLIED`

Required gate passed: **false**

## Required checks

|check|exit|
|---|---:|
|`guard_configure`|missing|
|`guard_build`|missing|
|`guard_test`|missing|
|`guard_direct`|missing|
|`guard_asan_configure`|missing|
|`guard_asan_build`|missing|
|`guard_asan_test`|missing|
|`main_configure`|missing|
|`main_build`|missing|
|`main_ctest`|missing|

## Structural audit signal

Unreviewed direct SQLite extraction locations: `76`. This is not relabeled as a test failure or silently ignored; it is the remaining integration checklist.
