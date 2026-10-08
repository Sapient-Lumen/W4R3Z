# rev0068 patch semantic/minimality gate

rev0068 continues from rev0067 and keeps the strict/front lane frozen. It adds a reviewer-facing semantic/minimality audit over the exported rev0059 split filing-bundle patches while continuing to use the uploaded `Nicotine-source(1).zip` as archived-source input.

This is not a new private packet and not a live-current upstream proof. It is an archived-source patch-review layer that answers: “Do the exported split patches stay inside their intended source files and edit only the semantic surface claimed by each filing bundle?”

## Scope

The gate audits twelve patch files:

```text
3 archived lanes × 4 filing-bundle patches = 12 patch files
```

Filing bundles:

```text
U-123
PB-01
SEARCH-RESP-SOURCE-ADMISSION
SEARCH-RESP-PARSER-BUDGET
```

The seven production-gated packets remain mapped to those bundles:

```text
U-123 -> U-123
PB-01 -> PB-01
SEARCH-RESP-01A -> SEARCH-RESP-SOURCE-ADMISSION
SEARCH-RESP-01B-BUDDY -> SEARCH-RESP-SOURCE-ADMISSION
SEARCH-RESP-01C-ROOM -> SEARCH-RESP-SOURCE-ADMISSION
SEARCH-RESP-PARSE-BUDGET-A -> SEARCH-RESP-PARSER-BUDGET
SEARCH-RESP-PARSE-BUDGET-B -> SEARCH-RESP-PARSER-BUDGET
```

## Results

```text
source bundle SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
source ZIP entries: 3551
source lanes found: 3/3
patch bundle files: 12
semantic inventory rows: 470
file-scope rows: 12/12 pass
marker-contract rows: 48/48 pass
bundle-summary rows: 12/12 pass
source touched-file rows: 15/15 pass
forbidden semantic findings: 0
negative controls: 5/5 pass
package hygiene: 5/5 pass
inherited rev0067 fixture-contract rerun: pass
coherence linter: no structural coherence-map errors detected
```

## What the helper checks

`tools/probe_rev0068_patch_semantic_minimality.py` checks:

```text
- uploaded source bundle identity and lane set
- rev0059 split patch file presence
- bundle-specific source file scope
- patch semantic inventory for add/delete lines
- required invariant markers for each bundle
- absence of new import dependencies or dynamic execution patterns
- absence of broad config/UI/network-message-ID edits
- touched source-file hashes against rev0065 Git provenance rows
- fail-closed negative controls
- package hygiene
```

## Bundle file-scope contract

```text
U-123:
  pynicotine/downloads.py
  pynicotine/transfers.py

PB-01:
  pynicotine/slskproto.py

SEARCH-RESP-SOURCE-ADMISSION:
  pynicotine/search.py

SEARCH-RESP-PARSER-BUDGET:
  pynicotine/slskmessages.py
```

## Required marker contract

The marker contract is intentionally narrow. It does not re-prove behavior; prior regression gates already do that. It proves that the reviewer-facing patch files still contain the intended invariant hooks.

```text
U-123:
  Rejected duplicate download request
  active_download is not download
  active_transfer is transfer
  deactivated = True

PB-01:
  Rejecting replacement connection
  keeping established primary connection
  return False
  return True

SEARCH-RESP-SOURCE-ADMISSION:
  joined_rooms
  tuple(core.buddies.users)
  expected_users
  username not in search.users

SEARCH-RESP-PARSER-BUDGET:
  MAX_SEARCH_RESPONSE_USERNAME_LENGTH
  MAX_SEARCH_RESPONSE_RESULT_COUNT
  accepted_result_count
  max_results
```

## Interpretation

rev0068 adds a semantic review layer between hunk-level applicability and maintainer-facing filing text:

```text
rev0066: hunk preimage / file scope / patch applicability
rev0067: clean-room regression fixture and runner hygiene
rev0068: semantic/minimality inventory of the split patches
```

This means the cube now has an explicit record that the archived-source patches are not only applicable and regression-backed, but also constrained to the source files and semantic edit classes claimed by the four filing bundles.

## Boundaries retained

rev0068 does not claim any of the following:

```text
- fresh current upstream checkout was completed;
- selected patches apply unchanged to current upstream;
- current upstream is unfixed;
- public path traversal work is a new private packet;
- broad 3.3.11 release-note language retires any strict/front packet.
```

The next external-filing gate remains a fresh current checkout or current source tarball with commit identity, followed by the current-source seven fixed-regression rerun.
