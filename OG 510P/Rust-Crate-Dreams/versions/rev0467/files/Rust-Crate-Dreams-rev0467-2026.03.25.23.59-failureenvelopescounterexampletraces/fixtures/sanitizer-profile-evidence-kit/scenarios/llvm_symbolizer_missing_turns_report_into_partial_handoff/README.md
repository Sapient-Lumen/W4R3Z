# Missing `llvm-symbolizer` turns a finding into a weaker handoff artifact

This scenario keeps one operational truth visible:
the finding may still be real, but the report quality is worse if symbolization is missing.

The receipt should distinguish raw-PC output from a portable, symbolized handoff.
