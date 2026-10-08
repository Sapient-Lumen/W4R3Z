# Connection-pool client scenario

Focus: spawned maintenance work, in-flight request cancellation, explicit close/drain ordering, and what dropping the public client handle actually leaves alive.


Concrete example artifacts added in this pass:
- `drain-recipe.manifest.example.json`
- `lifecycle-check.report.example.json`
