# Finish forecast proof page: ETA window, finishability grade, and claim ceiling interface spec

## Purpose

After forecast review, the product needs one durable proof page that answers:

> what is the strongest finish claim we can still make, what proves the remaining work and finishability posture, what ETA window survives honest scrutiny, and what stronger sentence is still blocked?

## Core decision

AnonSync must expose one first-class **Finish forecast proof** page for every work item that has entered forecast review, deadline review, no-honest-forecast territory, reroute-after-forecast, or external publication of finish expectations.

## Fixed page order

1. **Forecast verdict banner**
2. **Remaining-work basis card**
3. **Finishability basis card**
4. **ETA-window card**
5. **Forecast fragility card**
6. **Blocked stronger claim card**

### 1) Forecast verdict banner

Show:

- current forecast verdict
- current finishability grade
- strongest allowed finish sentence
- strongest allowed ETA sentence
- current confidence grade
- deadline posture if any
- forecast owner

Supported `forecast_verdict` values:

- `finishable-with-bounded-window`
- `finishable-with-wide-window`
- `finishable-after-checkpoint`
- `finishable-no-honest-eta`
- `deadline-risk-material`
- `forecast-broken-reroute-needed`
- `no-honest-forecast-proved`

Hard rule:

A verdict may not claim any ETA window unless both the remaining-work basis and the window-widening factors are explicitly published.

### 2) Remaining-work basis card

Required rows:

- strongest current remaining-work basis
- freshness of that basis
- whether it is direct or inferred
- hidden preparation still outstanding
- external dependency still outstanding
- reviewer who accepted the basis

### 3) Finishability basis card

Required rows:

- strongest basis that work can finish
- strongest live blocker against finish
- whether current route is sufficient
- whether reroute would reset or preserve the estimate
- smallest claimed finish scope

### 4) ETA-window card

Required rows:

- ETA claim class
- earliest honest finish
- latest honest finish
- time basis for the lower bound
- time basis for the upper bound
- checkpoint dependencies if any
- publication audience if already shared

### 5) Forecast fragility card

Required rows:

- confidence grade
- leading fragility source
- whether recent speed is representative
- whether schedule/pause windows widen the estimate
- whether hidden preprocessing widens the estimate
- whether interruption restart risk widens the estimate
- whether source absence or lock risk blocks tighter claims

### 6) Blocked stronger claim card

Required rows:

- strongest blocked stronger finish sentence
- strongest blocked stronger ETA sentence
- missing event or fact that would unlock each one
- whether the stronger claim is impossible or merely premature

Examples:

- `Current evidence supports a broad finish window, but not a narrow ETA, because schedule pauses and rescan-triggered discovery still dominate.`
- `Work remains finishable after the locked-file barrier clears, but any time-bound finish claim is blocked until access returns.`
- `A bounded window survives for the current scope only; a whole-estate finish claim remains blocked by unresolved ghost-file risk.`
