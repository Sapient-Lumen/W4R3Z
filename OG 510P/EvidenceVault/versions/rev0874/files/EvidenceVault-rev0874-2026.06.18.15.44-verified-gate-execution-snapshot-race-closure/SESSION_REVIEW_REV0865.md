# Session review — rev0865

This revision recovered one exact 356,744-byte canonical source payload rather than another proof/search abstraction. It also made the upstream README's narrow `CC-BY-4.0` file-level evidence and unchanged attribution explicit without broadening PACT or archive rights.

The refactor closes a serious operational defect: rev0864 encouraged reports inside an immutable bundle, which immediately invalidated its overlay manifest. rev0865 permits reports only outside the bundle, forces integrity into selected runs, repeats integrity after other checks, and labels partial runs honestly.

The measured boundary is now unavoidable: 19 exact / 17 mismatched / 4,550 missing canonical index paths. The next high-value work requires real bytes, a full canonical tree, or rights-owner decisions.
