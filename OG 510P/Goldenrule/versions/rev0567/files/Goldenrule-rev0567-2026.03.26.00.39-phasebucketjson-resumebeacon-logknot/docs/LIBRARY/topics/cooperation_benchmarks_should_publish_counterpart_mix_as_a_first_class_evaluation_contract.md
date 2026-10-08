# Cooperation benchmarks should publish counterpart mix as a first-class evaluation contract

A cooperation score is underspecified unless the archive also says **who the policy was cooperating with**.
A system can look strong in self-play, fragile against unfamiliar model partners, stable against fixed scripted partners, or unexpectedly good with humans.
Those are not interchangeable stories.

Recent external work makes the split hard to ignore.
`RS-GR-049` explicitly evaluates language models in finitely repeated games against **other models**, **human-like strategies**, and **actual human players**.
`RS-GR-037` shows that cross-environment training can improve collaboration with **real people**, which means counterpart mix and environment mix jointly shape the final claim.

## Minimum contract

Any inheritor-facing cooperation benchmark summary should publish counterpart lanes separately rather than collapsing them into one scalar:

1. **self-play / same-family play**,
2. **unfamiliar model-partner play**,
3. **scripted or hand-coded partner play**,
4. **human or human-proxy partner play**,
5. and the **aggregation rule** used to combine them, if any.

## Implementor consequence

Do not report one “cooperation” headline if the evaluation mixes these counterpart classes without a lane breakdown.
A gain that comes only from self-play or only from friendly scripted partners is not yet inheritor-grade evidence that the Golden Rule survives contact with unfamiliar agents or people.

## Archive consequence

Keep this compact.
The retained artifact does not need another wide report family.
One small benchmark card or receipt row can carry the counterpart-mix breakdown alongside the standing partner / environment / institution-generalization fields.
