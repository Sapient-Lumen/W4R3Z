# Related-work research pass 037 — trace/export workbench

Current revision: rev0055

Rev0044 focuses the Kernel Kit demo on inspectability. A demo that proves a runtime path but cannot produce an artifact a future session can inspect is too easy to hand-wave. The new direction steals ideas from browser performance tooling and observability systems without claiming compatibility.

Research pressure points:

- Chrome trace event style: a trace can be represented as event objects with categories, timestamps, process/thread ids, and args. BrowserRT should be able to export a Chrome-trace-shaped envelope because it gives future sessions a familiar mental model for timelines. This is a shape, not a compatibility claim.
- Perfetto: trace tooling should help developers understand behavior in complex systems. BrowserRT should eventually have exportable traces and queryable receipts, but the cube should not claim Perfetto support until directly tested.
- OpenTelemetry traces/spans: the demo should distinguish events, spans, links, and receipts. Rev0044 adds an `otelSketch` only to preserve vocabulary; it explicitly does not claim OpenTelemetry compatibility.
- User Timing / PerformanceObserver: a future browser page could add native `performance.mark()` and `performance.measure()` evidence. Rev0044 does not add that yet; it shelves it as a next page improvement.

Stolen idea for BrowserRT: every user-facing demo should emit a proof receipt that is useful both to humans and tooling. The receipt should contain staged evidence, trace summaries, explicit non-claims, and at least one export format future sessions can inspect.

Do not overclaim this. Rev0044 is an inspectability rung, not production observability.
