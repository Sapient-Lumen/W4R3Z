# Decision: add a compact installed-lane ticket for the i3/X11 flagship stack

## Status
Accepted for the flagship i3/X11 resident-runtime lane.

## Problem
The flagship stack already exposes:
- install-time helpers (`install_user_session.sh`, `smoke_install.sh`)
- post-install verification (`verify_user_session_json.sh`)
- day-2 repair (`repair_user_session.sh`)

But the resident control plane still lacks one bounded installed-lane answer that says:
- not deployed yet, keep using ad hoc/generated-stack paths
- partially installed or drifted, repair the installed lane first
- installed and session-fit, start it
- already active, observe it instead of restarting blindly

That forces a private LLM or operator to reopen the larger install verdict and restitch intent by hand.

## Decision
Add a small composition module that standardizes an installed-lane ticket with four statuses:
- `install_not_deployed`
- `repair_required`
- `start_recommended`
- `active`

The ticket remains explicitly subordinate to the flagship i3/X11 product cut:
- X11 + i3 is primary
- long-lived user service is primary
- ad hoc CLI runs remain available
- broader Linux breadth stays secondary unless it sharpens the resident lane

## Consequences
Good:
- makes install-day2 reasoning smaller and more LLM-friendly
- separates install-lane triage from the noisier full install verdict
- gives the next generator integration a safer seam than editing the giant CLI blob first

Tradeoff:
- this revision adds the ticket module and tests first, but does not yet wire the ticket into `gen-i3-busd-stack`
- that generator threading remains the next obvious implementation cut
