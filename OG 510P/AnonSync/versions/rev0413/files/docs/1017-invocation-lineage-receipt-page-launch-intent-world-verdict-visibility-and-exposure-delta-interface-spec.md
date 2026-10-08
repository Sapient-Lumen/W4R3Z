# Invocation lineage receipt page — launch intent, world verdict, visibility, and exposure delta

## Purpose

Preserve durable proof of what launch was reviewed, what world actually opened, and what stronger sentence remained blocked.

## Receipt fields

Must preserve:

- receipt id
- reviewed invocation profile id
- launch origin surface and actor
- requested intent
- chosen world locator / authority class
- world-lineage verdict
- visibility posture before and after, if there was a prior world
- control-exposure posture before and after
- whether the world was reopened, forked, created fresh, narrowed to inspect-only, or blocked
- strongest safe sentence
- blocked stronger sentence
- follow-up obligations
- recorded time

## Required sections

### 1. What was reviewed

Show:

- launch request summary
- reviewed world candidate
- key deltas the operator saw before apply

### 2. What actually opened

Show:

- actual world handle
- actual visibility class
- actual control exposure class
- whether launch used the expected state root

### 3. Continuity ceiling

Show:

- same-world continuity proven
- same-world but quieter projection
- sibling world created
- clean world created
- launch blocked / not applied
- proof weakened by missing or stale observations

### 4. Residue and follow-up

Show:

- pending rebind or relink obligations
- pending exposure hardening or narrowing
- stop-proof or quiet-runtime proof links where relevant
- any receipts this one superseded or reopened

## Example summary lines

- `Reviewed same-world minimized reopen; same world opened; exposure unchanged.`
- `Reviewed LAN-exposed headless start; same root reused; control widened from loopback-only to reviewed LAN.`
- `Reviewed state-root override; sibling world created; prior continuity receipts remain local to the earlier world.`
- `Launch blocked due to overlap risk; no new world opened.`

## Interaction rules

- receipts must be exportable as text without losing world-lineage verdict
- later start/stop/exposure reviews must be able to cite this receipt directly
- a later launch may supersede this receipt, but must not rewrite it

## Non-clone conclusion

Resilio's present docs still require remembered launch ritual to explain later state continuity.
AnonSync should instead make every materially meaningful start produce a durable invocation receipt.
