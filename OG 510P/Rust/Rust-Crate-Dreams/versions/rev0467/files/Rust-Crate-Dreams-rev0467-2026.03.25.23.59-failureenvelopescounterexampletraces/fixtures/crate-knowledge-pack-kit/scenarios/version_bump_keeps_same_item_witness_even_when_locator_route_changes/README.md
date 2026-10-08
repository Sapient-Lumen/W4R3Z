# Scenario: version bump keeps the same item witness even when the locator route changes

Problem:
A pack was generated once using a docs.rs `latest` browsing route and later regenerated with an exact version route.
A downstream consumer wants to know whether the claim is still about the same conceptual item.

What this scenario proves:
Identity fidelity should be evaluated from witnesses and recheck rules, not only from whether the rendered locator string stayed identical.

Good outcome:
The bundle says the witness pair is reusable across versions only after rechecking exact version, path, kind, and any target-sensitive context.
