# Successor-safe ceremony receipt package heads should ship compact status cards

A package head solves discovery, but it does not yet solve the inheritor's cheapest operational question: **may I still cite this package head right now, until when, and what would reopen it?**

The surrounding standards point toward a small explicit answer.

- RFC 8631 says the `status` link relation can point to a status resource that service consumers retrieve to learn the current state of a service or key resource.
- NIST's [RMF Monitor Step FAQ](https://csrc.nist.gov/CSRC/media/Projects/risk-management/documents/07-Monitor%20Step/NIST%20RMF%20Monitor%20Step-FAQs.pdf) says ongoing monitoring supports ongoing authorization decisions and that authorization-package updates need to stay current enough to support those decisions.
- NIST's [RMF Roles and Responsibilities Crosswalk](https://csrc.nist.gov/csrc/media/Projects/risk-management/documents/Additional%20Resources/NIST%20RMF%20Roles%20and%20Responsibilities%20Crosswalk.pdf) says authorizing officials review posture information at the defined authorization frequency and determine whether continued operation remains acceptable.

So a successor-safe ceremony receipt package head should not point only at a manifest, lineage object, and raw live-status ingredients.
It should also point at **one compact status card** that collapses the live review window, the as-of review verdict, and the current citation advisory into one machine-checkable stewarding object.

That status card should stay small and explicit:

1. the authoritative package manifest path and fixity;
2. the active receipt-locator digest;
3. the current review window (`reviewed_on`, `review_due_on`, `max_review_interval_days`, `watch_status`);
4. the current as-of review state (`review_decision`, observed triggers, matched reopen triggers, failed basis codes);
5. the current citation guidance for existing citations and new citations;
6. whether the package is currently citable;
7. the exact regeneration sequence only when citation is suspended.

With that one small object, the inheritor no longer needs to open a package head, review watch, review verdict, and citation advisory just to answer the live custody question.
The head can use `status` to point at the status card, while the status card preserves the review/verdict/advisory inputs by path and fixity.
