# Scenario — GitLab route or TP-only posture change requires authorization drift review

A GitLab-based release path still mints an ID token, but changes the `ci_config_ref_uri`, `aud`, and TP-only posture between two releases.
That should not be treated as a cosmetic diff; it changes the release-authorization story.
