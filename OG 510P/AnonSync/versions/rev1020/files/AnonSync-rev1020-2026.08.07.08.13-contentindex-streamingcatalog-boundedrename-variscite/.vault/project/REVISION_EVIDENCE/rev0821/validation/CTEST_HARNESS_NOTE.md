# CTest harness note

A normal complete invocation repeatedly stopped after printing the next
`Start` line even though the just-completed test had passed and no test child
remained. The revision therefore does not claim one uninterrupted 99-test
invocation. `ctest-complete-prefix-1-36.log` explicitly records every index
1 through 36 passing, and `ctest-range-37-99.log` records 63/63 for every
remaining index. `ctest-range-coverage.json` parses both logs and rejects any
missing index.
