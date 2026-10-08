# Successor-safe ceremony receipt assessments should collapse to explicit archive dispositions

The archive now has a compact successor-safe ceremony receipt, a stable locator, and a fail-closed assessment report.
That is already enough to say **what** ceremony facts were retained and whether the retained object is structurally or semantically weak.
But it still leaves one handoff gap: **what should the next steward do with that verdict?**

Two source facts justify one tighter step:

- `RS-GR-514` says risk response is an intentional and informed decision to accept, avoid, mitigate, share, or transfer identified risk.
- `RS-GR-515` says a POA&M exists to record remediation plans for unacceptable risks identified in assessment findings.

So a successor-safe ceremony receipt assessment should not remain a floating status blob.
It should collapse to one **tiny archive disposition** that states at least:

1. whether the receipt is **claim-ready citable**, **provisional locator-only**, or **held for remediation**;
2. whether the residual-risk response is currently **accept** or **mitigate**;
3. which finding codes remain open at fail or warning severity;
4. which required actions still stand before inheritor-facing reliance;
5. and what concrete review trigger should cause reassessment.

This is still the right kind of archive growth.
It adds one tiny object, but it prevents a more expensive future failure: inheritors seeing a warning-laden assessment without knowing whether the prior steward meant to rely on it, cite it only as context, or hold it out of the durable claim surface until remediation landed.
