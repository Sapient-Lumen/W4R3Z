# Scenario — unstable libtest JSON must not masquerade as a stable portable contract

A project imported a machine-readable test result stream that looks close to libtest JSON.
The import is still useful, but the bundle must not claim permanent stable replay exactness just because JSON exists.
