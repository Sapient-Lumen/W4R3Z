# Promise reservation lineage receipt page: hold basis, expiry, and blocked stronger sentences interface spec

## Purpose

The operator needs one compact receipt that can travel with the case and still preserve the essential truth about future-room ownership.

## Core decision

AnonSync must expose one **Promise reservation lineage receipt** for every hold that materially changes what promises may be issued.

## Receipt fields

### Required identity fields

- reservation id
- linked capacity object id
- hold owner
- hold class
- current status
- reserved scope class

### Required basis fields

- hold basis class
- strongest supporting fact
- strongest weakening fact
- linked future work object if any
- protected reserve interaction posture

### Required timing fields

- opened at
- expires at or review gate
- last renewed at
- release trigger
- reclaim owner
- current expiry confidence grade

### Required consequence fields

- strongest blocked promise class
- strongest blocked scope
- weaker promise classes still allowed
- ghost-hold guard status
- next event needed to restore freer room

## Supported receipt footer sentences

The receipt must end with one strongest truthful footer sentence, for example:

- `One narrowed deadline-class slot remains hard-reserved for the named dependency until Thursday 09:00; weaker checkpoint promises remain admissible, but broader delivery commitments stay blocked.`
- `This former reservation is no longer valid future-room ownership; it crossed expiry without renewal and now survives only as ghost-hold lineage until reclaimed.`

## Hard rules

- receipts may not omit expiry or review terms
- receipts may not treat soft hold and hard reservation as the same state
- receipts must preserve the blocked stronger sentence
- receipts must remain durable after release or reclaim so that hidden capacity theft cannot recur through memory loss
