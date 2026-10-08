# Queue growth worker

Use this fixture family to express:
- backlog growth versus consumer starvation distinctions,
- gauges, runtime metrics, and concurrency-tuning guidance,
- support bundles that remain reviewable and low-risk.

Example artifact: `signal-map.report.example.json` keeps queue depth, runtime delay, and external-broker ambiguity separate instead of calling everything “backpressure”.
