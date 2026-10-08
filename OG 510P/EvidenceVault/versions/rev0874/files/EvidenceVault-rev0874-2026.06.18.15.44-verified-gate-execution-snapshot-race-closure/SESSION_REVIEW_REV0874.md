# Session review — rev0874

## What materially changed

The exact rev0873 gate was proven able to verify legitimate validator bytes at preflight, execute substituted bytes by reopening the source path, restore the original, pass postflight, and report success. rev0874 now verifies the complete bundle before other in-tree imports, executes coverage and all checks from one private verified snapshot under isolated Python, and revalidates both snapshot and source before returning success.

The regression exercises the exact parent defect and the corrected source-swap sequence. It also rejects ambient `PYTHONPATH` poisoning and an in-bundle standard-library shadow.

## Recovery work

Twelve retained sibling ZIPs and 7,305 file members yielded 113 unique exact canonical paths, all already available. No duplicate or guessed bytes were admitted, and this search lane is retired until genuinely new input appears.

## Still at risk

Rights closure, the 17 selected StreamFold payloads, canonical `README.md`, and 4,461 unavailable canonical files remain unresolved. The private snapshot is an execution-correctness boundary for ordinary runs, not a sandbox against hostile same-UID processes or an external authenticity proof.
