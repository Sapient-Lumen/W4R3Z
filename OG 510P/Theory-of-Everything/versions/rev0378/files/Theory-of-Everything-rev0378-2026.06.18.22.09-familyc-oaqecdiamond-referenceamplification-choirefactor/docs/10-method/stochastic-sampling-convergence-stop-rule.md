# Stochastic sampling and convergence stop rule

`OQ-0106` blocks stochastic-sampling, Monte Carlo, MCMC, nested-sampling, HMC, posterior/evidence, effective-sample-size, R-hat, and convergence-diagnostic language unless `STOCHASTIC-SAMPLER-LEDGER.json`, `ESTIMATOR-VARIANCE-LEDGER.json`, and `CONVERGENCE-DIAGNOSTIC-LEDGER.json` are declared and current.

A route must say what is sampled, what estimator is computed, what convergence or stopping rule is used, what finite-sample residual remains, and what rollback fires if sampling, estimator, or diagnostic control fails.
