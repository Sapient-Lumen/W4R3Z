# Peer identity view page: user aggregate, seat rows, and class-dependent grouping interface spec

The archive already had constellation and member-observation doctrine.
What it still lacked was one ordinary page for the question:

> when the peer view shows one row, several rows, a grouped person entry, or only device rows, what is the grouping basis and how much identity / authority meaning can the operator honestly read from that shape?

Current Resilio docs still make this seam sharp.
They still say Advanced folders can recognize that two devices belong to one user identity and show the user with descendant devices underneath, while Standard folders cannot prove that grouping and therefore show peer/device rows separately.
That is not a cosmetic detail.
It changes what the list means.

## Page promise

The Peer identity view page should make five answers adjacent:

1. current row model now
2. grouping evidence now
3. authority meaning now
4. class dependence now
5. strongest honest next action

The page exists so the operator stops reading too much or too little into row shape alone.

## Fixed page order

Every peer-identity view page should render the same sections in the same order:

1. **Subject snapshot**
2. **Row model**
3. **Grouping evidence**
4. **Authority interpretation**
5. **Class dependence and ambiguity**
6. **Receipt promise**

### 1) Subject snapshot

This section should show:

- subject label and class
- current peer count and seat count
- whether the page is rendering live, remembered, hidden, or mixed participants
- whether the current class can represent family/group identity at all

The operator should be able to answer: **what subject and class is this list for?**

### 2) Row model

This section should show:

- whether the visible list is grouped by `member family`, `seat`, `device`, `anonymous capability holder`, or mixed classes
- which rows are aggregates and which are leaves
- whether totals count groups, seats, or both

The operator should be able to answer: **what kind of things are the rows on this page?**

### 3) Grouping evidence

This section should show:

- why specific rows are grouped (`verified family`, `same reviewed member`, `shared certificate lineage`, `manual alias only`, `cannot prove grouping`)
- what evidence is absent when rows remain separate
- whether the current subject class prevents stronger grouping even if the operator suspects the rows belong together

The operator should be able to answer: **why does this list collapse or split exactly here?**

### 4) Authority interpretation

This section should show:

- what rights attach to the aggregate versus the leaf seats
- whether one row implies shared approval memory or merely presentational grouping
- whether mutating a grouped row affects all descendant seats or only the inspected leaf
- whether row shape changes under another class even when the underlying remote person is the same

The operator should be able to answer: **what authority meaning is safe to infer from this grouping, and what is not?**

### 5) Class dependence and ambiguity

This section should show:

- which parts of the peer view are direct consequences of subject class
- what a stronger class might reveal that the current class cannot
- whether suspected same-person rows remain separate because proof is absent, not because the system knows they differ
- any current ambiguity the operator should not over-read

The operator should be able to answer: **is this list split because the people are different, or because this class cannot prove more?**

### 6) Receipt promise

A peer-identity view receipt should preserve:

- subject and class
- row model in force
- grouping evidence basis
- authority interpretation summary
- ambiguity warnings shown

The operator should be able to answer: **what exactly did the peer view claim at this moment?**

## What this page must never imply

The page must never imply that:

- grouped rows and device rows mean the same thing
- a separate device row proves a separate person
- a grouped member row automatically means rights mutate identically across all descendants
- class-dependent grouping is merely a visual preference
- a later richer class reveals no new semantics, only nicer UI

## Result

This page is how AnonSync borrows Resilio's honesty that peer views depend on deeper identity structure, while refusing the weaker page contract that leaves operators to infer row meaning from screenshots and support prose.
