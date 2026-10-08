# 859. Verification-policy lockfile surface audit and hidden-route refactor

**Track:** Shared / Verification / Policy lockfile
**Status:** v855/v856 release-gate coherence repair

**Revision:** v849

The v849 audit reduces hidden policy-route risk by checking that the strict example policy has a matching sidecar digest, requires caller-side policy pinning, remains packet-external, is selector-complete, is validity-bounded, and is assembled from the expected trust inputs. See `artifacts/reports/verification-policy-lockfile-scope-rev0849.json`.
