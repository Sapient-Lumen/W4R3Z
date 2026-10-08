# GLOSSARY (EARLY)

These definitions are provisional.

## time estimate
A system's current belief about time.

## uncertainty
A bounded admission that the true time may differ from the estimate by some interval or error envelope.

## authenticity
Whether a message or source identity is cryptographically or procedurally validated.

## trustworthiness
Whether a timing signal or estimate deserves use in a given regime and profile.

## regime
The current operational condition under which time is being produced or consumed (e.g. normal, degraded, holdover, partitioned).

## holdover
Operating without fresh external synchronization, relying on local oscillator behavior and prior state.

## provenance
Information about which sources, paths, and trust anchors contributed to the current timing belief.

## confidence
A downstream-facing summary of how consequentially the current time estimate should be trusted.

## timing mechanism
A concrete means of obtaining or disseminating time, such as NTP, NTS, PTP, GNSS, or a local oscillator.

## time state
A richer object than a timestamp, potentially including estimate, uncertainty, provenance, and regime.
