# Starvation and suspension warning page — priority preemption, queue cap, and hidden exceptions

## Purpose

Warn when some work can be suspended, stranded, or repeatedly postponed even though the system is still generally active.

This page exists to answer:

- `what exactly is starved?`
- `why is it not running now?`
- `is it merely slow, or can it miss the active queue entirely?`
- `what hidden exceptions make the simple story false?`

## Required sections

### 1. Affected work set

Must show:

- starved item or cohort id
- scope (`single item`, `selection`, `share subset`, `low-priority class`, `background lane`)
- time in suspended state
- whether work ever entered the active queue

### 2. Starvation basis

Must distinguish at minimum:

- preempted by higher priority
- excluded because active queue is full
- displaced by queue rebuild
- deferred behind stronger safety stop
- hidden runtime exception / unsupported strict priority
- unknown; proof insufficient

### 3. Recovery conditions

Must show what must become true for work to resume:

- free queue slot
- higher-priority cohort completion
- schedule window change
- budget edit
- source reappearance
- manual reclassification

### 4. User-visible versus scheduler truth

Must show, side by side:

- what the list ordering suggests
- what the actual scheduler is currently doing
- whether the UI view is alphabetical, grouped, or true execution order

### 5. Strongest safe sentence

Examples:

- `These items are suspended behind higher-priority downloads and may remain so until an active queue slot opens.`
- `This cohort is visible in the queue view but is not currently eligible to enter the active download set.`

### 6. Blocked stronger sentence

Examples:

- `Everything visible in this queue is progressing fairly.`
- `Lower-priority work will eventually make steady progress without intervention.`

## Minimum interactions

The page must expose actions to:

- raise priority
- relax competing budget
- open bottleneck proof
- export starvation receipt