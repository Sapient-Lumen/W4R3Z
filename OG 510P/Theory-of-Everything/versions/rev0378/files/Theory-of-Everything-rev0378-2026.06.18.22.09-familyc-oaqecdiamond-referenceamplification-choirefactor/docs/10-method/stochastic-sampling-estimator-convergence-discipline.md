# Stochastic sampling, estimator variance, and convergence discipline

Stochastic samplers are route denominators, not authority multipliers. A route that invokes Monte Carlo, MCMC, nested sampling, HMC, bootstrap/resampling, stochastic simulation, survey posterior samples, catalog samplers, or benchmark samples must declare the target distribution or population, the transition or proposal mechanism, the finite-sample budget, seed/replay policy, and estimator uncertainty before sampling language can spend route-local credit.

The active rule is noncompensatory: a sampler can explore a target distribution without proving estimator accuracy; an estimator can report uncertainty without proving convergence; and a convergence diagnostic can pass without proving global-mode coverage or candidate identity.
