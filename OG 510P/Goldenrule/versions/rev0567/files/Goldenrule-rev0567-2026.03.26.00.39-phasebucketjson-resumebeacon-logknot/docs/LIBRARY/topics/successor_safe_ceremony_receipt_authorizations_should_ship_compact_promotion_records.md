# Successor-safe ceremony receipt authorizations should ship compact promotion records

Once the archive already has a successor-safe ceremony receipt, a locator, an assessment, a disposition, a remediation plan, and an authorization decision, one compact custody gap still remains: **why did a package that used to be weak become claim-ready now?**

A future steward should not have to infer that promotion from chat history, timestamps, or a vague sense that the latest package looks better. The archive should keep one tiny promotion record that compares a prior package to the current one, names which findings closed, names any findings that stayed open or reopened, and states whether the receipt truly moved into claim-ready citation.

That shape matches the surrounding governance literature. NIST's [RMF Assess Step FAQ](https://csrc.nist.gov/csrc/media/projects/risk-management/documents/05-assess%20step/nist%20rmf%20assess%20step-faqs.pdf) says reassessments verify that deficiencies were corrected and that controls now produce the desired outcome. NIST's [RMF Monitor Step FAQ](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf) says corrected weaknesses are reassessed after remediation. NIST's [OSCAL POA&M model overview](https://pages.nist.gov/OSCAL/learn/concepts/layer/assessment/poam/) says POA&M structures support remediation planning/tracking and disposition status.

So the archive should not stop at "authorization is green." It should also keep one **compact promotion companion** beside any materially changed successor-safe ceremony receipt package:

- prior locator
- current locator
- prior versus current assessment / authorization status
- closed, carried, and newly opened finding codes
- one promotion decision
- one next-step / review trigger

That is enough for a future inheritor to prove *why* the package became claim-ready without re-copying old receipts or re-reading bulky remediation history.
