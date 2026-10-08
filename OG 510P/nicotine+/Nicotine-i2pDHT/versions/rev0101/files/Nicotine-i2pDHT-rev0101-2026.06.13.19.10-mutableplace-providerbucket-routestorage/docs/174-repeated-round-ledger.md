# rev0019 — repeated-round evidence ledger

A single round can look green by accident. Liveness can be bounded while witnesses are stale; a provider can give a useful refusal without proving availability; a false-provider proof can arrive alongside otherwise healthy evidence.

`roundledger.py` joins liveness budget reports, provider-proof verdicts, and witness-cache summaries across repeated rounds. It accepts only when the newest round has bounded liveness, a true provider proof, and diverse witness evidence. It stops on metadata budget pressure, quarantines semantic provider lies and witness contradictions, and continues when provider or witness pressure is incomplete.

This is still local evidence algebra. It is not consensus and not a witness quorum.
