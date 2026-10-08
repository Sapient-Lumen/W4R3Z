# rev0049 trace capture roundtrip notes

The riskiest unfinished lane was public/pretrained traces. rev0048 made an importer, but the default run was still surrogate-only and an external NPZ load could be confused with public/pretrained evidence. rev0049 fixes that boundary and tests the importer with actual NPZ bundles.

Key invariant: `external_trace_loaded == true` is not sufficient for `public_pretrained_trace_loaded == true`. The latter requires explicit declaration and provenance review.

The roundtrip fixture is synthetic. Its value is harness validity, not model prevalence evidence.
