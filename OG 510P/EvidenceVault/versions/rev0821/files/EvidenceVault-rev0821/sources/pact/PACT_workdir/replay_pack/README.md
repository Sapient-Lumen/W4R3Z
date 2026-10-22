# PACT replay pack (demo)

This directory contains a tiny, self-contained artifact pack intended to be
verified offline.

Files:
- `manifest.json`, `transcript.json`, `store/*.json`: a minimal bundle-like run.
- `ppp_run_root.dsse.json`: DSSE-wrapped in-toto Statement carrying a PPP predicate.
- `abom_view_one_object.json`: selective disclosure of one store object + Merkle proof.
- `policy_decision.dsse.json`: DSSE-wrapped policy decision receipt bound to the run root.
- `keys.json`: Ed25519 public key material for demo verification.

Run verifier:
```bash
python PACT_workdir/demos/verify_replay_pack.py PACT_workdir/replay_pack
```

