# Archived rev0073 active PB-01 files

These files were active before the rev0074 role split. They are retained for provenance and are not the current test surface.

```text
probe_rev0010_pb01_peer_binding.py
  sha256 9c8ca117d9b485407bb6e5f0fc113cf5065df974672dbb26ff35f9e6563be0da

test_peer_connection_primary_election_reproducer.py
  sha256 278003b1cab84e79f8a86ef89d09104871f6fc5c0fde4fbd2e91636cc0c93f5a

test_peer_connection_primary_election_fixed_regression.py
  sha256 5b02cbcab457fb964319dc57d5078d8be9444ca72ae71fe04893f633232fc8bb
```

The old fixed regression encoded the rev0038 established-primary policy. Rev0074 demonstrates a simultaneous-race counterexample to that policy and therefore treats the file as historical evidence, not a selected regression.
