# Perturbative, loop-order, and resummation discipline

Perturbative success is a local support object, not a completion certificate. A route that invokes a weak-coupling expansion, loop calculation, genus expansion, post-Newtonian series, gradient expansion, EFT expansion, saddle expansion, waveform expansion, or benchmark-order expansion must declare the expansion parameter, expansion point, order, omitted sectors, scheme, regulator, and public carrier.

`PERTURBATIVE-EXPANSION-LEDGER.json`, `LOOP-ORDER-LEDGER.json`, and `RESUMMATION-BOREL-LEDGER.json` make those declarations executable. Their role is conservative: cap or roll back perturbative, counterterm, convergence, Borel, renormalon, transseries, resurgence, exact-result, and UV-completion wording unless the route rows are current.

Noncompensation rule: a controlled perturbative expansion does not pay loop-order debt; a finite loop-order calculation does not prove convergence or nonperturbative completion; a successful resummation does not identify the candidate or select the observed sector.
