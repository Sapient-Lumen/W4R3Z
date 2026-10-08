# Rev1017 research note

A single process snapshot cannot expose a sampled workload peak, while retaining every full process response at every point would scale as processes multiplied by samples. The retained design instead keeps compact aggregate points and per-process envelopes. The next experiment should apply this observer to real sparse multi-terabyte share services before AnonSync commits to a global chunk index, resource governor, or multi-share daemon.
