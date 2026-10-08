# Remedy-hardening-attestation successor beneficiary-adherence contract sheet page — governed horizon, relapse budget, and compliance ceiling

## Purpose

This page is the operator-facing sheet for deciding whether a beneficiary who once adopted a later canonical correction actually stayed switched for the governed horizon.
It exists to stop `adopted once`, `currently looks corrected`, `sync resumed`, or `no new contradiction observed` from being mistaken for `the named beneficiary maintained corrected working behavior through the governed horizon`.

## Core question

The page must answer:

**for this named beneficiary, governed slice, and governed horizon, what is the strongest honest sentence about uninterrupted adherence, relapse, recovery, and horizon-bounded compliance now?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source beneficiary-adoption receipt identifier
- named beneficiary identifier
- governed slice identifier
- canonical correction identifier
- governed horizon identifier
- horizon start
- horizon end or still-open rule
- lapse-budget class (`zero`, `narrow`, `metered`, `manual-exception-only`)
- relapse channel set summary
- expected corrected working-pointer state
- current corrected working-pointer state
- last confirmed aligned checkpoint
- open relapse incident count
- recovered relapse incident count
- unresolved relapse risk class
- strongest honest adherence sentence now
- blocked stronger uninterrupted-compliance sentence now

## Standing ladder

The page must support at least these distinct standings:

- adopted once, horizon adherence still unproven
- currently corrected, past interruption still unresolved
- likely adhered, but relapse channels remain under-observed
- relapsed and not yet recovered
- relapsed and later recovered
- uninterrupted adherence proven for current horizon
- horizon still open, stronger sentence deferred
- horizon closed with narrow slice-level compliance only
- later contradiction narrowed prior adherence confidence
- receipt superseded

## Required comparisons

The sheet must compare:

- single switch event versus interval adherence
- current snapshot versus whole-horizon behavior
- relapse with recovery versus uninterrupted adherence
- allowed maintenance window versus unbudgeted lapse
- beneficiary-local adherence versus governed-slice compliance
- desired strongest sentence versus blocked stronger sentence

## Required layout

### Header

Show:

- correction name
- beneficiary name
- governed horizon
- current adherence standing
- strongest honest sentence now

### Left column — intended adherence contract

Show:

- governed slice
- horizon start and end rule
- lapse budget
- protected relapse channels
- disallowed interruption classes
- closure condition for the horizon claim

### Center column — observed horizon facts

Show:

- last confirmed aligned checkpoint
- relapse incidents
- recovery incidents
- pause or scheduler hold intervals
- archive-restore incidents
- offline stale-comeback incidents
- read-only divergence incidents
- delayed-detection windows

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens uninterrupted-adherence confidence

### Right column — consequence for beneficiary truth

Show:

- whether the beneficiary merely adopted, merely looks correct now, relapsed, recovered, or stayed aligned throughout the horizon
- whether any interruption fell within the declared lapse budget
- whether the governed-slice compliance sentence is current, narrow, contradicted, or still blocked
- what stronger uninterrupted sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- adopted once, horizon unproven
- currently corrected, past gap unresolved
- relapsed and unresolved
- relapsed and recovered
- uninterrupted adherence proven
- broader compliance sentence still blocked

## Interaction requirements

The interface must support:

- clicking the horizon badge to open the exact interval and closure rule being claimed
- clicking any relapse chip to open a drawer showing incident time, channel, duration, affected artifacts, and recovery status
- clicking the lapse-budget badge to reveal whether a given interruption was tolerated, tolerated-but-narrowing, or disqualifying
- pinning one beneficiary while comparing several horizons so the operator can see whether confidence rose, decayed, or got reset

## Hard rules

The page must never allow:

- `adopted` to silently become `adhered for the whole horizon`
- `currently corrected` to silently become `never relapsed`
- `recovered` to silently become `uninterrupted`
- `no contradiction observed` to silently become `positive adherence proof`
