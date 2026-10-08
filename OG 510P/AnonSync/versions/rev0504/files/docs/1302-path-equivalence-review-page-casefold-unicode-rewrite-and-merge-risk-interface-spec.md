## Path-equivalence review

### Question this page answers
When two peers appear to talk about `the same path`, are they really talking about one stable subject, or about **different byte-distinct names that collapse, rewrite, or conflict on arrival**?

### Review branches

#### 1) Case-only distinction branch
Use this branch when names differ only by letter case.
Render:
- whether the current seat preserves case distinction or collapses it
- whether a receiving seat can hold both names at once
- explicit conflict risk if any cohort member is case-collapsing

#### 2) Unicode-normalization branch
Use this branch when glyphs look the same but codepoint representation may differ.
Render:
- composed vs decomposed witness if known
- whether the cohort shares one normalization posture
- warning that human-equal glyphs can still be path-distinct or path-colliding

#### 3) Symbol-rewrite / forbidden-symbol branch
Use this branch when a name contains platform-sensitive symbols.
Render:
- preserve vs rewrite vs block expectation
- exact rewrite class if known
- whether rewrite could collapse two previously distinct names into one destination slot

#### 4) Length-ceiling branch
Use this branch when any cohort member has a tighter path or filename ceiling.
Render:
- local visible length
- tight cohort ceiling if known
- whether the risk is warn-only, block-on-arrival, or currently unproven

#### 5) Link-object branch
Use this branch when the subject is a soft link, hard link, junction, or symbolic link.
Render:
- object kind
- whether this seat syncs the link object, blocks it, or collapses it into conflict behavior
- explicit note that syncing a symbolic-link object is weaker than syncing the referenced target tree

### Equivalence ladder
- **same visible glyphs** is weaker than **same byte sequence**
- **same byte sequence** is weaker than **same canonical identity through this cohort**
- **same canonical identity** is weaker than **same safe arrival outcome**
- **same safe arrival outcome** is weaker than **no rewrite or conflict risk through future moves**

### Forbidden overclaims
Do not let the UI say:
- `same filename everywhere` when the cohort is normalization-mixed
- `supported path` when only the current seat proved it
- `symlink synced` when target coverage is absent
- `rename safe` when the destination cohort still has rewrite or collapse risk
