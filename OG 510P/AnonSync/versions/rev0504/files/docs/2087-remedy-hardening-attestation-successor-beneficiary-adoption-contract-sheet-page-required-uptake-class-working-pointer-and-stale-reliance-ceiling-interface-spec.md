# Remedy-hardening-attestation successor beneficiary-adoption contract sheet page — required uptake class, working pointer, and stale-reliance ceiling

## Purpose

This page is the operator-facing sheet for deciding whether a later canonical correction did more than get seen or acknowledged.
It exists to stop `correction seen`, `acknowledgement completed`, `file downloaded`, or `file opened` from being mistaken for `the named beneficiary actually switched to the corrected working state and retired stale reliance`.

## Core question

The page must answer:

**for this named beneficiary and later canonical correction, what is the strongest honest sentence about acknowledgement, adoption, stale-state retirement, and governed-slice uptake now?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source beneficiary-notice receipt identifier
- named beneficiary identifier
- governed slice identifier
- canonical correction identifier
- correction class
- required uptake class (`notice-only`, `acknowledge`, `open`, `adopt`, `retire-stale`, `attest-compliant`)
- corrected working-artifact identifier
- expected working pointer or reference
- current working-pointer state
- stale artifact set summary
- stale-reliance risk class
- downstream pointer-switch evidence state
- stale-retirement evidence state
- relapse or reversion state
- strongest honest adoption sentence now
- blocked stronger compliance sentence now

## Standing ladder

The page must support at least these distinct standings:

- correction seen, adoption still unproven
- correction acknowledged, active working state still unproven
- corrected artifact downloaded, adoption still unproven
- corrected artifact opened, active switch still unproven
- beneficiary likely adopted corrected working state
- stale artifacts remain, so stronger uptake sentence stays blocked
- stale artifacts retired for governed slice
- compliance attested for named slice only
- later contradiction narrowed prior adoption confidence
- receipt superseded

## Required comparisons

The sheet must compare:

- acknowledgement evidence versus adoption evidence
- fetched or opened artifact versus active working artifact
- corrected working pointer versus stale working pointer
- stale artifact presence versus stale artifact active use
- named-slice adoption versus broader compliance claim
- desired uptake sentence versus currently blocked stronger sentence

## Required layout

### Header

Show:

- correction name
- beneficiary name
- required uptake class
- current working-pointer state
- strongest honest sentence now

### Left column — intended uptake contract

Show:

- governed slice
- correction class
- required uptake class
- corrected working artifact
- stale-state retirement rule
- forbidden substitute states

### Center column — observed uptake facts

Show:

- acknowledgement state
- download / hydration evidence
- open or view evidence
- active working-pointer evidence
- stale artifact set summary
- stale-retirement evidence
- relapse evidence

Every row in this column must have:

- current value
- evidence source
- whether it strengthens or weakens the adoption sentence

### Right column — consequence for beneficiary truth

Show:

- whether the correction was merely noticed, merely acknowledged, merely fetched, merely opened, likely adopted, or demonstrably switched into active use
- whether stale artifacts still exist and whether they still matter
- whether the governed-slice uptake sentence is current, narrow, contradicted, or still blocked
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- seen only, adoption unproven
- acknowledged, adoption unproven
- opened, working switch unproven
- active working pointer switched
- stale reliance still open
- stale reliance retired for governed slice
- stronger compliance sentence still blocked

## Interaction requirements

The interface must support:

- clicking any uptake chip to open a drawer showing `seen / acknowledged / downloaded / opened / switched / stale-retired / relapsed`
- clicking the working-pointer badge to reveal every artifact or path still competing to be the beneficiary's real working reference
- clicking the stale-reliance chip to reveal exactly which stale artifacts, exports, local derivatives, or remembered paths keep the stronger sentence blocked
- pinning one beneficiary while comparing several corrections so the required uptake class stays stable across the list

## Hard rules

The page must never allow:

- `acknowledged` to silently become `adopted`
- `downloaded` to silently become `working-copy switched`
- `opened` to silently become `stale reliance retired`
- `latest bytes present somewhere` to silently become `governed-slice compliance achieved`
