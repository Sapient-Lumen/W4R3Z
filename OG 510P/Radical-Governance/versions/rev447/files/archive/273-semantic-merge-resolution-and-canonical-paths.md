# Semantic Merge Resolution & Canonical Paths

**Purpose:** make the rev380 ↔ rev438 merge *semantically navigable*: preserve both lines where they genuinely add value, while naming which memo is the canonical starting point for each overlapping cluster.

**Merge stance:** prefer **canonical path + explicit sibling roles** over destructive deletion. In this archive, overlaps often hide a real distinction between:
- a **system / theory / architecture** memo,
- a **rails / artifact / implementation** memo,
- a **worked-example / operator** layer.

This memo tells readers which is which so the archive keeps salience without becoming a maze.

---

## How to use this memo

When two files feel duplicative:
1. start with the **canonical entry** named below,
2. use the **paired memo** only if you need the adjacent layer (architecture, implementation, or examples),
3. do **not** collapse the pair unless the distinction has disappeared in substance.

A future hard-delete is justified only when the surviving memo fully absorbs the other’s role *and* preserves its best retrieval hooks.

---

## Canonical overlap map

| Cluster | Canonical entry | Paired / supporting memo(s) | Resolution |
|---|---|---|---|
| whistleblowing / protected disclosure | `121-whistleblowing-and-protected-disclosure.md` | `83-whistleblowing-and-protected-disclosures.md` | `121` is the tighter implementation-facing interface spec; `83` remains the broader safety-and-integrity frame. |
| digital public infrastructure (DPI) | `164-digital-public-infrastructure-governance.md` | `188-digital-public-infrastructure-governance.md`, `212-dpi-trust-framework-and-interop-governance.md`, `213-digital-public-goods-intake-and-certification-rails.md` | `164` is the architectural anchor; `188` is the shorter rails/operating layer; `212`/`213` handle trust and intake. |
| emergency powers / derogations | `165-emergency-powers-derogation-sunsets-rails.md` | `186-emergency-powers-derogations-and-sunset-discipline.md`, `112-exception-control-and-emergency-powers.md`, `23-emergency-governance-and-exceptions.md` | `165` is the main modern emergency-powers rail; `186` is a narrower companion focused on ledger discipline and renewal handling. |
| constitutional change / amendment | `206-constitutional-change-and-amendment-rails.md` | `171-constitutional-maintenance-and-amendment-ops.md`, `124-constitutional-amendment-and-entrenchment.md`, `205-constitutional-review-observability-and-precedent-ledgers.md` | `206` is the canonical change-packet and threshold memo; `171` covers periodic maintenance/review operations rather than one amendment event. |
| deliberation / sortition / assemblies | `143-deliberative-systems-and-citizens-assemblies.md` | `159-civic-lottery-and-deliberation-infrastructure.md`, `180-legitimacy-engines-elections-sortition-deliberation-recall.md`, `224-deliberative-processes-and-citizens-assemblies-rails.md`, `119-selection-and-sortition-integrity.md` | `143` is the theory/system front door; `159` is the reusable civic-lottery subsystem; `224` is the concrete process rails layer; `180` is the legitimacy-stack umbrella; `119` handles draw integrity. |
| public health governance | `57-public-health-and-biosecurity-governance.md` | `234-public-health-preparedness-and-response-rails.md`, `165-emergency-powers-derogation-sunsets-rails.md` | `57` is the full cross-scope governance spine; `234` is the artifact-led preparedness/response operating pack. |
| public integrity system | `226-public-integrity-system-architecture.md` | `187-public-integrity-system-blueprint.md`, `227-prosecutorial-and-disciplinary-integrity-rails.md`, `179-open-contracting-and-procurement-rails.md`, `181-influence-lobbying-transparency-and-integrity-rails.md` | `226` is the current architecture anchor; `187` remains a useful compact blueprint and quick orientation memo. |
| identity / credential / federation | `160-digital-identity-credentials-privacy-utility.md` | `210-digital-identity-and-credentialing-rails.md`, `211-privacy-preserving-federation-and-consent-ledgers.md`, `212-dpi-trust-framework-and-interop-governance.md` | `160` frames the governed-person utility and risk model; `210` and `211` provide the implementable rails. |
| worked examples ↔ domain memos | `235-worked-examples-and-trace-walkthroughs.md` | `244-worked-example-atlas-and-retrieval-index.md`, `274-worked-example-to-domain-crosswalk.md` | The worked-example layer is preserved as its own retrieval and training subsystem rather than being flattened into theory memos. |

---

## Merge decisions taken in rev441

### 1) Preserve overlaps when they encode different layers
Several apparent duplicates turned out not to be duplicates at all:
- **architecture vs rails** (`164` vs `188`, `57` vs `234`, `143` vs `224`);
- **maintenance ops vs change-event discipline** (`171` vs `206`);
- **broad moral/organizational framing vs operator spec** (`83` vs `121`).

These are now explicitly named as sibling layers.

### 2) Prefer modern canonical paths, but keep older salience
Where both lines cover similar ground, the newer or tighter memo becomes the default entry point, but the older memo is retained when it:
- explains the stakes more vividly,
- contains a stronger failure-mode framing,
- or serves a better retrieval role for non-expert readers.

### 3) Keep the worked-example graft intact
The rev380 worked-example block (`235..270`) remains a distinct casebook layer because flattening it into thematic memos would lose:
- example-first onboarding,
- audit and tabletop use,
- symptom-based retrieval,
- and the archive’s concrete “show your work” advantage.

Use `274-worked-example-to-domain-crosswalk.md` when moving from a case trace back into thematic governance design.

---

## Editorial follow-through still worth doing later

High-value future cleanup:
1. fold the strongest parts of `83` into `121` once the tone/coverage distinction can be preserved in a shorter structure;
2. decide whether `188` should eventually become a thin implementation addendum inside `164`;
3. eventually bundle `143 + 159 + 224` into a cleaner three-part deliberation stack with explicit shared glossary;
4. continue wiring worked examples into the domain memos where the examples sharpen the design argument.

Until then, this memo is the anti-regret rule: **name the relationship before deleting anything.**
