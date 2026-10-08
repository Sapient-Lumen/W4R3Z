# 03 — Control surfaces

TimeState is a state object. It is surrounded by policy and control surfaces that decide how the state is produced, downgraded, retained, and exposed.

## Minimal control-surface family

### 1. Source policy

Defines which sources are admissible, preferred, rejected, combined, or isolated.

### 2. Error and acceptability policy

Defines how uncertainty, drift, quality, and profile-specific tolerance map into usability.

### 3. Regime transition surface

Defines when the local system moves among normal, degraded, holdover, partition-local, and recovery regimes.

### 4. Holdover policy

Defines behavior after loss of discipline, including how freshness and applicability change over time.

### 5. Downstream applicability policy

Defines which uses may consume the current assessed state.

## Profile boundary

Dense control rules belong in profiles or deployment configuration. The shared model needs only the fact that these surfaces exist and that their consequences can appear as compact assessed state.

## Non-upgrade rule

Control surfaces must not silently upgrade trust. A relay, fallback mode, unknown hook state, stale profile reference, or missing required/default item may preserve or weaken applicability according to profile rules, but must not create a stronger claim without new evidence and assessment.
