# Test Run Artifact Standard Kit fixtures

These fixtures support **P-0106 Test Run Artifact Standard Kit**.

They exist to keep four receiver-facing truths separate:

1. **run identity** — which runner/harness/import route actually produced the artifact;
2. **selection basis** — which workspace/package/target/filter/profile/platform basis defined the run;
3. **attempt topology** — whether retries, fail-fast, stress loops, or process model changed the verdict meaning;
4. **bundle sensitivity** — whether the artifact is portable only, internal-shareable, or export-safe.

The scenarios are deliberately small and comparative.
They are designed to stop future passes from flattening “has logs / has JUnit / has JSON / has nextest recording” into one fake portable test-run story.
