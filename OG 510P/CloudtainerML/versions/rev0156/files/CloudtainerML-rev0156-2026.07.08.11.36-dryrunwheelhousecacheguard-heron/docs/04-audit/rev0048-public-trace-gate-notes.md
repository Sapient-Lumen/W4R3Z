# rev0048 public/pretrained trace gate notes

rev0048 addresses the riskiest incomplete lane by turning the public/pretrained
attention-trace blocker into an executable interface.  The new probe can ingest
external NPZ trace bundles in either `scores + values` form or `q + k + v` form,
then evaluates the same guarded sparse-attention compiler panel used by the
surrogate suite.

The default artifact is deliberately **surrogate-only**.  It is useful for
stress testing the gate and selector semantics, but it is not public/pretrained
model evidence and cannot promote the mechanism.

Key surrogate findings:

- broad high-entropy rows force mass histogram to near-dense reads;
- value-tail rows make mass-only selection fail output quality despite retained
  probability mass;
- value-norm exception metadata repairs the constructed tail failure without
  reading V vectors or dense outputs during selection;
- peaked/local rows are where a sparse compiler might plausibly win, but real
  prevalence is unknown until external traces are loaded.
