# Successor-safe ceremony receipt review watches should collapse to explicit review verdicts

Once the archive already has a compact review watch, the next easy failure mode is **latent freshness state**.

A future steward can inherit a watch that says when a package should be reopened, but still be forced to manually decide whether today is late enough, whether any reopen trigger actually fired, and whether claim-ready citation should stay live or be suspended. That leaves the decisive freshness verdict in chat history or operator intuition rather than in the archive.

The archive should therefore keep one further tiny artifact: a **review verdict**.

For any successor-safe ceremony receipt package under watch, the verdict should:

1. cite the watched receipt locator;
2. preserve the watch's reviewed-on and due-on dates;
3. state the review date being evaluated;
4. list any observed reopen-trigger codes and which ones matched the watch;
5. decide whether claim-ready citation continues or must be suspended pending regeneration; and
6. carry the exact regeneration sequence only when reopening is required.

This is deliberately smaller than a full reassessment. It does not replay the whole package. It simply turns a latent freshness boundary into one explicit inheritor answer:

> **As of this date, may this package still be cited, or must it reopen now?**

NIST's RMF Monitor guidance says authorization decisions and risk acceptance need to be revisited regularly and adjusted based on continuous-monitoring results, while the RMF roles-and-responsibilities guidance says the authorizing official reviews information at the defined authorization frequency, determines whether continued operation remains acceptable, and reauthorizes when required. A compact review verdict translates that pressure into archive practice without widening the retained package.

The verdict should stay narrow:

- one watched locator;
- one as-of date;
- one trigger-match set;
- one timeliness state;
- one keep-citing versus reopen-now decision; and
- one regeneration sequence only if reopening is required.

That is enough to keep freshness decisions from drifting back into oral tradition.
