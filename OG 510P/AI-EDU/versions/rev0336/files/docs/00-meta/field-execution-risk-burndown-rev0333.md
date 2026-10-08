# Field execution risk burndown — rev0333

| Risk | Prior state | rev0333 change | Remaining test |
|---|---|---|---|
| Owner review predates session rows | owner review checked readiness and hash scope but not event dates | owner-review recorder now refuses review dates before the latest dated session row | a real packet must pass only after the local cycle rows actually exist |
| Result receipt predates review or cycle | result recorder checked review date before result date but not latest session date | result recorder now checks session chronology and result-date ordering | a real result receipt must fail if chronology is impossible |
| Partial post-cycle rows masquerade as entry readiness | any post-cycle failure after entry checks could fall back to cycle-entry-ready | partially filled post-cycle payloads now become `NOT_READY` for repair | operators must repair or clear bad rows instead of restarting the cycle path |
| Dates are free text | readiness did not require ISO dates or phase order | added `session-log-dates-valid-and-ordered` with baseline <= coach-use <= transfer | a real local owner must use only aggregate ISO dates, not raw schedules or identifying details |
| Control growth displaces field work | the defect could have spawned a new chronology registry | reused readiness, owner-review, and result-recorder path; no new validator family | next change should follow a real field event or another reproducible defect |

## Current unblocker

Hold one real discovery conversation, complete one local owner plan, run at most one feasibility cycle,
and record only aggregate dated rows. Do not treat a chronology-valid packet as evidence that learning
improved or that `FT-0181` can close.
