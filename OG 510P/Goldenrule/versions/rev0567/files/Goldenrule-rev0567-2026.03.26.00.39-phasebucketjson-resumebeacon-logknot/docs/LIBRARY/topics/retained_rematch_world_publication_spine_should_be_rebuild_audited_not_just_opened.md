# Retained rematch-world publication spine should be rebuild-audited, not just opened

Once the archive retains the concrete four-object publication spine, a new risk appears: future sessions may visually inspect those objects, see that they look plausible, and still miss subtle drift between the retained packet, the retained compiled artifact, the retained preflight receipt, and the retained bundle receipt.

That is avoidable. The archive already knows how to regenerate the compiled artifact and both receipts from the retained packet, evidence receipt, seed, and compact decision contract. So the durable publication state should not be trusted merely because the files are present. It should be trusted because the retained files survive a deterministic rebuild audit.

The compact rule is:

1. retain the packet, evidence receipt, compiled artifact, preflight receipt, and bundle receipt;
2. rerun one audit that rebuilds the artifact and both receipts from the retained packet path; and
3. treat the fill patch as scratch-only unless drift debugging actually needs it.

That keeps the archive compact while making the publication state *provably consistent* rather than merely concrete.
