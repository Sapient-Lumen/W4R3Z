# rev0044 attention frontier notes

rev0044 moves from a single sparse-output comparison to a frontier question: how many value reads are structurally required to retain enough dense attention mass and output quality?

The key scientific change is that fixed exact Top-K can no longer be treated as the objective. The frontier records minimum K for 0.90/0.95/0.98 mass, fixed Top-K mass, output cosine, relative L2 error, and byte estimates. This gives the cube a veto before kernel work: if 0.95 mass requires hundreds of values, a K=32 certifier is not a deployable attention-output solution.

The tiny transformer trace probe is intentionally modest. It trains a CPU toy model and extracts real Q/K/V attention rows from the learned layers and heads. This is not public-model evidence, but it is stronger than synthetic-only rows and should prevent synthetic artifacts from becoming doctrine.
