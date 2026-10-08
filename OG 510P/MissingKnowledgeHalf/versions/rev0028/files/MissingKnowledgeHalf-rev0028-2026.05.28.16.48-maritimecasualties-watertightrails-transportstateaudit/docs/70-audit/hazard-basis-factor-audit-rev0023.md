# Hazard-basis factor audit — rev0023

This audit/refactor pass introduces factor axes that should eventually apply across the engineering lane:

- hazard basis;
- state legibility;
- common-mode exposure;
- operating-experience memory;
- emergency information rail;
- correction infusion.

The immediate purpose is to prevent a category error: treating “nuclear accident” as if the domain label were the causal explanation. TMI, Chornobyl/Chernobyl, and Fukushima sit in the same domain, but their dominant axes differ.

Open debt:

- apply the same axes to aerospace, chemical, software, civil, and medical-device engineering records;
- add formal graph edges for factor-axis assignments;
- decide whether these axes should become schema fields or remain ledger overlays;
- add positive and negative controls for the new pattern candidate.
