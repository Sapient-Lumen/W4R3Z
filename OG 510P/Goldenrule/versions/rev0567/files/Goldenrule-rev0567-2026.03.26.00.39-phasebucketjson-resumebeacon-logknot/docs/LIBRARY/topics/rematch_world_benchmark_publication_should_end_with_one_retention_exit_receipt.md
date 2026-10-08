# Rematch-world benchmark publication should end with one retention-exit receipt

The archive now distinguishes durable publication objects from the things that may leave once publication is stable.

For the first endogenous rematch-world benchmark, the durable set is:

- the evidence packet,
- the evidence receipt,
- the compiled benchmark artifact,
- the preflight receipt,
- the publication-bundle receipt,
- and the publication-spine audit receipt.

After those are retained and the retained receipts still agree, the compiled fill patch and hashed scratch sources should be treated as exit-ready rather than as default long-term archive residents.

This matters because the archive’s growth risk is now mostly internal fanout and operational residue, not external PDFs. The inheritor should not have to remember an informal cleanup ritual. One compact receipt should say exactly what must stay and exactly what may leave.
