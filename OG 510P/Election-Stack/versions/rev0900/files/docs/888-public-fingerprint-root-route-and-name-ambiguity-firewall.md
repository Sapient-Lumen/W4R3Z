# 888 — Public-fingerprint root-route and name-ambiguity firewall

**Track:** Shared / Verifier / Release gate

rev0860 advances the bounded public-fingerprint helper to profile `1.2` so standalone fingerprint reports cannot hide route ambiguity that strict policy verification already treats as fail-closed.

Executable behavior:

- packet-root symlink routes emit `packet_root_symlink_rejected_for_hash:.` and hash no target entries;
- included public-file and included-directory symlinks remain warning surfaces;
- public relpaths must be NFC-normalized and distinct under Unicode casefolding;
- strict verification-policy authentication remains fail-closed on any public-fingerprint warning.

Audit: `artifacts/reports/public-fingerprint-root-route-and-name-ambiguity-audit-rev0860.json`.

Boundary: this is route-safety for a bounded public fingerprint, not a filesystem sandbox, legal authority claim, certification result, or production trust-root proof.
