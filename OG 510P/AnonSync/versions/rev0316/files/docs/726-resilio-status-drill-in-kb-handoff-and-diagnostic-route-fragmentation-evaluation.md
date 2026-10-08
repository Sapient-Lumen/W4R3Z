# Resilio status drill-in, KB handoff, and diagnostic-route fragmentation evaluation

## Why this pass exists

The archive already had strong pages for warnings, blocker scope, recovery rung, status-row proof, route evidence, queue explanation, and several receipts.
What it still did not own tightly enough was one ordinary operator question that sits earlier than all of them:

- when a row looks wrong, what should clicking it do
- will that click explain the current claim, show affected items, open a queue, or throw the operator into external prose
- which adjacent surface is the strongest next diagnostic route
- how does the product preserve continuity across those hops
- what later receipt proves which path was actually taken

Current official Resilio docs still make that seam materially real.
They still define the main view as a mix of status rows, peers counts, and history; they still tell operators to click warnings, peers, and queues from different places; and the live v3 line still records that one ordinary error status had to be fixed to be clickable at all.

That candor is useful.
The problem is that the click contract is still article-shaped.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Rows are admitted to be diagnostic entry points.** The current desktop main-view article still says statuses show current activity and that clicking `X of Y` opens the peers list.
- **Different clicks are allowed to reveal different slices.** The same main-view article still says History is a distinct 30-day activity surface, not just another row badge.
- **Troubleshooting still starts from the product surface.** The current `My files don't sync` article still tells operators to inspect the Status column, click warnings, inspect Sync History, and open peers lists to see upload/download queues.
- **Item-level detail is sometimes exposed.** The current `Locked files` article still says the error message is clickable and opens the list of locked files, and that clicking a listed file takes the operator to it.
- **Clickability itself is treated as product behavior.** The current v3 change log still records a fix for a non-clickable `Can't download file` error status, while the same log still shows the live Sync v3 line through `3.1.2.1076`.

That is good candor.
Resilio is not pretending a warning row, peers list, history stream, and item list are the same object.

## Where current Resilio still stays too article-shaped

### 1. The first click does not have one stable contract

A serious row click can still mean several materially different things:

- open a KB explanation
- open a peer list
- open a file list
- open history elsewhere
- reveal nothing because the status is not clickable yet or not clickable here

Those are all real routes.
They just should not be inferred from folklore.

### 2. Meaning and affected items are still separable but not explicitly partitioned

Current troubleshooting still lets the operator learn warning meaning in one place and concrete affected items in another.
That means `what is happening` and `which files are implicated` can still require different hops without one owned router explaining the split.

### 3. Diagnostic routes still require support-memory sequencing

The ordinary operator answer to `what do I open next?` can still depend on remembering that:

- peers count helps with route/source questions
- history helps with recent event traces
- queue views help with transfer backlog
- status-click sometimes opens KB prose
- special warnings such as locked files may open item lists instead

That is support knowledge, not a first-class product contract.

### 4. Later continuity can still be weak

After several hops, the product still risks leaving the operator without one durable statement of:

- where the investigation started
- which routes were opened
- which evidence each route contributed
- what conclusion was actually earned
- what stronger conclusion remained unsupported

## What AnonSync should do instead

AnonSync should make **diagnostic route ownership** a first-class reviewed object.

The product should own four page families:

1. **Status drilldown**
   - current token meaning
   - subject scope
   - strongest safe sentence
   - next best routes
   - local claim boundary

2. **Diagnostic router**
   - best next surfaces for the current question
   - route comparison
   - evidence coverage by route
   - preserved context across hops

3. **Affected items**
   - concrete files/items implicated now
   - grouped cause slices
   - action-safe item navigation
   - exact non-inference boundary

4. **Diagnostic route receipt**
   - entry row
   - routes visited
   - evidence gained
   - approved conclusion
   - unresolved gaps

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that rows should be clickable, that different diagnostic surfaces answer different questions, and that item-level lists matter. But it is not worth cloning the way current operators still have to reconstruct from several docs whether a row click will open local proof, a KB article, a peers/queue detour, or an item list — and what final answer those hops actually earned.

## New replacement pages added in this revision

- `727` Status drilldown
- `728` Diagnostic router
- `729` Affected items
- `730` Diagnostic route receipt
