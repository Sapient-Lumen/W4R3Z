# Console recipe declared but runtime not instrumented

Use this fixture family to express:
- tokio-console or console-subscriber guidance that is documented as official,
- a runtime that does **not** actually emit the compatible events the console path needs,
- and the need to downgrade the triage path to partial support or manual review until instrumentation is real.

Example artifact: `diagnosis-check.report.example.json` shows how the lane should fail loudly when console guidance is documented but runtime compatibility is not witnessed.
