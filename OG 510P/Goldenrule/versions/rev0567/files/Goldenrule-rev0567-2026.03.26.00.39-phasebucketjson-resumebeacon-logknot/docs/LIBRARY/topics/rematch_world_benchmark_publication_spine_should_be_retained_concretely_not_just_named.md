# Rematch-world benchmark publication spine should be retained concretely, not just named

Once the archive has a tiny evidence packet, a provenance receipt, a compiled benchmark artifact, and a preflight receipt, the publication problem changes. The risk is no longer missing analysis; it is leaving the durable publication spine implicit and trusting future sessions to regenerate it correctly from memory.

That is unnecessary ambiguity. The publication bundle receipt is valuable as a compact handoff index, but it should not be the only retained publication surface. A future inheritor should be able to open the retained compiled artifact and the retained preflight receipt directly, verify that the artifact is publication-ready, and only then consult the bundle receipt for the compact path summary.

So the compact rule is:

1. retain the four durable objects explicitly: packet, evidence receipt, compiled artifact, preflight receipt;
2. retain the bundle receipt as a convenience index over those four objects; and
3. keep the compiled fill patch scratch-only unless debugging actually needs it.

That keeps the archive compact while making the final publication state concrete rather than implied.
