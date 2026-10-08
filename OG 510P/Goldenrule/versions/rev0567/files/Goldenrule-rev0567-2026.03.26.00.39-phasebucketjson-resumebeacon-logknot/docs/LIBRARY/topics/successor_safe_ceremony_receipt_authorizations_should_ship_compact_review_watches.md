# Successor-safe ceremony receipt authorizations should ship compact review watches

Once the archive already has a compact successor-safe ceremony receipt package — receipt, locator, assessment, disposition, remediation plan, authorization decision, and promotion record — the next easy failure mode is **silent staleness**.

A future steward can inherit a package that was claim-ready when first assembled, cite it months later, and never notice that the triggering protocol surface, retained evidence, or retention policy changed in the meantime. That is not a provenance failure of content; it is a custody failure of **freshness**.

The archive should therefore keep one further tiny artifact: a **review watch**.

For any successor-safe ceremony receipt package that is currently treated as claim-ready:

1. keep the current receipt locator;
2. preserve the current authorization decision and promotion decision;
3. record the date the package was last reviewed plus one archive-local maximum review interval;
4. enumerate the event triggers that force a reopen even before the calendar interval elapses; and
5. publish the exact regeneration sequence that a future steward should rerun once the watch opens.

The point is not to turn the archive into a ticket system.
The point is to keep one machine-checkable answer to a simple inheritor question:

> **Is this receipt package still safe to cite, or has it crossed a freshness boundary that should reopen the whole claim-ready package?**

NIST's RMF Assess and Monitor guidance supports that move: ongoing assessments support continued authorization decisions, and remediated controls are reassessed to verify that they still operate as intended. A compact review watch translates that pressure into archive practice without retaining bulky surrounding evidence.

The watch should stay narrow:

- one locator;
- one authorization state;
- one promotion state;
- one reviewed-on date;
- one no-later-than review interval;
- a short trigger-code list; and
- one required regeneration sequence.

That is enough to keep freshness from living only in chat history.
