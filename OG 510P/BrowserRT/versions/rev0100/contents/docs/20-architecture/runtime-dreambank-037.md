# Runtime dreambank 037 — inspectable demos

Current revision: rev0055

The dream is that BrowserRT demos become self-diagnosing workbenches. A user should not just see "passed". They should see:

- what lanes participated;
- what object refs moved;
- what got admitted or rejected;
- what storage provider was touched;
- what trace events support each claim;
- what the demo still refuses to claim;
- what artifact can be exported for future sessions.

Rev0044 adds the smallest earned version: `createKernelKitTraceExport()` turns the Kernel Kit demo report into a BrowserRT receipt and a Chrome-trace-shaped JSON envelope. This keeps the demo tool-like without pretending to be Chrome DevTools, Perfetto, or OpenTelemetry.

Future dream rungs:

1. Native User Timing marks around each stage.
2. Downloadable trace files from the human page.
3. A tiny trace table with filters by lane/kind.
4. Side-by-side comparison of two Kernel Kit runs.
5. Import a previous trace receipt and show drift.
6. Add a timeline flamechart only after the event model has earned stable timestamps.

Boundary: trace export is evidence packaging, not a performance claim.
