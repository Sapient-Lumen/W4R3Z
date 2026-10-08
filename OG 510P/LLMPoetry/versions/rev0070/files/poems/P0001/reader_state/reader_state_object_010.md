# P0001-D010 reader-facing state object — Applied Patch / PATCHED

Built: `2026-06-14T19:47:00-04:00` / `rev0024` / turn `16`

## Status before reading

D010 remains **cold-reviewed `revise_not_promote`**. This file is not D011 and not an admission. It is the missing reader-facing surface promised by the form notes: one place where the closed, open, traversal, and patched states can be read without spelunking seven receipts first.

Core receipts: [`branch_packet`](../branches/branch_packet_010.json), [`selector_map`](../verification/selector_map_010.json), [`selector_vector`](../verification/selector_vector_010.json), [`loss_budget`](../verification/loss_budget_010.json), [`state_switch`](../verification/state_switch_010.json), [`ergodic_traversal`](../verification/ergodic_traversal_010.json), [`return_diff`](../verification/return_diff_010.json), [`patch_application`](../verification/patch_application_010.json), [`cold_review`](../judgments/cold_review_010_on_D010.json)

## How to read the object

Read downward. Each line is the same selected layer passing through four visible states: closed line, opened loss phrase, traversal route, and patched line. The poem's machine act is not hidden in a footnote; it is the transition itself.

## 1. Closed state

P4 Pinhole logic keeps a borrowed zero.
A4 At sleep-depth, voltage braids the coil.
T4 Tiny motors listen before the button.
C4 Coded air subtracts the spare module.
H4 Hushed parity bites through the latch.
E4 Each vowel rents one foreign glyph.
D4 Darker syntax molts beside a spool.

## 2. Open state

P4 Pinhole logic keeps a borrowed zero. ⇢ failed splice begins
A4 At sleep-depth, voltage braids the coil. ⇢ old vowel waits
T4 Tiny motors listen before the button. ⇢ until inside markup
C4 Coded air subtracts the spare module. ⇢ syntax crosses dusk
H4 Hushed parity bites through the latch. ⇢ the reader learns
E4 Each vowel rents one foreign glyph. ⇢ an index another
D4 Darker syntax molts beside a spool. ⇢ branch becomes surface

Shadow sentence: `failed splice begins old vowel waits until inside markup syntax crosses dusk the reader learns an index another branch becomes surface`

## 3. Traversal state

Rule: final selected word length modulo three omitted candidates chooses one omitted candidate from the same layer.

| Layer | Closed final word | Route | Omitted candidate | Route word |
|---|---:|---|---|---|
| P4 | zero | `len(zero)=4; 4%3=1` → index `1` | P2 Port solder names the splice. | **splice** |
| A4 | coil | `len(coil)=4; 4%3=1` → index `1` | A2 After noon, the socket learns vowel. | **vowel** |
| T4 | button | `len(button)=6; 6%3=0` → index `0` | T1 Toggle the mark and call it until. | **until** |
| C4 | module | `len(module)=6; 6%3=0` → index `0` | C1 Carry the splice back as syntax. | **syntax** |
| H4 | latch | `len(latch)=5; 5%3=2` → index `2` | H3 Haptic grammar fails but learns. | **learns** |
| E4 | glyph | `len(glyph)=5; 5%3=2` → index `2` | E3 Error-silk tastes almost another. | **another** |
| D4 | spool | `len(spool)=5; 5%3=2` → index `2` | D3 Distant pressure names the surface. | **surface** |

Traversal sentence: **splice vowel until syntax learns another surface**

## 4. Patched state

| Layer | Replacement | Patched line |
|---|---|---|
| P4 | `borrowed` → **splice** | P4 Pinhole logic keeps a splice zero. |
| A4 | `voltage` → **vowel** | A4 At sleep-depth, vowel braids the coil. |
| T4 | `before` → **until** | T4 Tiny motors listen until the button. |
| C4 | `Coded` → **Syntax** | C4 Syntax air subtracts the spare module. |
| H4 | `bites` → **learns** | H4 Hushed parity learns through the latch. |
| E4 | `one` → **another** | E4 Each vowel rents another foreign glyph. |
| D4 | `syntax` → **surface** | D4 Darker surface molts beside a spool. |

Patched surface:

P4 Pinhole logic keeps a splice zero.
A4 At sleep-depth, vowel braids the coil.
T4 Tiny motors listen until the button.
C4 Syntax air subtracts the spare module.
H4 Hushed parity learns through the latch.
E4 Each vowel rents another foreign glyph.
D4 Darker surface molts beside a spool.

## One-line layer walk

| Layer | Closed | Open addition | Traversal | Patch |
|---|---|---|---|---|
| P4 | P4 Pinhole logic keeps a borrowed zero. | ⇢ failed splice begins | P2 → **splice** | `borrowed` → `splice` |
| A4 | A4 At sleep-depth, voltage braids the coil. | ⇢ old vowel waits | A2 → **vowel** | `voltage` → `vowel` |
| T4 | T4 Tiny motors listen before the button. | ⇢ until inside markup | T1 → **until** | `before` → `until` |
| C4 | C4 Coded air subtracts the spare module. | ⇢ syntax crosses dusk | C1 → **syntax** | `Coded` → `Syntax` |
| H4 | H4 Hushed parity bites through the latch. | ⇢ the reader learns | H3 → **learns** | `bites` → `learns` |
| E4 | E4 Each vowel rents one foreign glyph. | ⇢ an index another | E3 → **another** | `one` → `another` |
| D4 | D4 Darker syntax molts beside a spool. | ⇢ branch becomes surface | D3 → **surface** | `syntax` → `surface` |

## Receipt matrix

Every visible transition above is authorized by local receipts. These links are bookkeeping evidence only.

| State | Authorizing receipts |
|---|---|
| closed | [`branch_packet_010.json`](../branches/branch_packet_010.json), [`selector_map_010.json`](../verification/selector_map_010.json), [`state_switch_010.json`](../verification/state_switch_010.json) |
| open | [`state_switch_010.json`](../verification/state_switch_010.json), [`selector_vector_010.json`](../verification/selector_vector_010.json), [`branch_packet_010.json`](../branches/branch_packet_010.json) |
| traversal | [`ergodic_traversal_010.json`](../verification/ergodic_traversal_010.json), [`branch_packet_010.json`](../branches/branch_packet_010.json) |
| patched | [`patch_application_010.json`](../verification/patch_application_010.json), [`ergodic_traversal_010.json`](../verification/ergodic_traversal_010.json) |

## Risk read

The earlier risk was that `patch` stayed a procedural promise. This object corrects that surface risk by showing the route words becoming replacements. The larger risk remains: the diction still leans on a narrow codework fog. If this readable state object is still inert to a human reader, the next honest move is not another receipt layer; it is freezing P0001 as a laboratory failure or forking P0002 under external material pressure.

## Machine-readable non-claim

This reader-state object makes D010's state transitions readable. It verifies no literary quality claim and does not admit the poem.
