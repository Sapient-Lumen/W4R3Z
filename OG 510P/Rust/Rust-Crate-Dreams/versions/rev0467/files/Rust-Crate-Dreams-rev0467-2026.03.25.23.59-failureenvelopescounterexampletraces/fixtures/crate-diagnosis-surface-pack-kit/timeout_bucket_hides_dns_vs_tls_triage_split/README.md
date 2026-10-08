# Timeout bucket hides DNS vs TLS triage split

Use this fixture family to express:
- one vague `timeout` symptom bucket that collapses too many failure modes,
- separate first-inspection paths for DNS, TLS, endpoint, or transport classes,
- and the need for symptom-class policy to keep diagnosis support from pretending a root cause too early.
