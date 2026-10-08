# Cargo Build Script Delegation Kit — lane boundaries (2026-03-22)

This note prevents **P-0508** from swallowing every build-time problem in the archive.

## P-0508 is for

- named build-unit topology,
- per-unit output ownership,
- override/delegate authority,
- unstable bridge posture,
- and drift/comparison artifacts.

## P-0508 is not for

### 1. Generic build-script readability / logs

That belongs primarily to **P-0046 buildscript-ux-kit**.
If the main question is “how do I make the failure readable?”, do not force it into P-0508.

### 2. Hermetic test fixtures for script behavior

That belongs primarily to **P-0059 buildscript-testkit**.
If the main question is “how do I replay this buildscript behavior under fixed inputs?”, do not force it into P-0508.

### 3. Host-vs-target execution truth

That belongs primarily to **P-0484 Toolchain & Target Support Contract Kit**.
P-0508 may reference host/target posture, but it should not become the main source of target-support truth.

### 4. Native dependency contracts themselves

That belongs primarily to the native-deps lane.
P-0508 explains the delegated build machinery, not the meaning of every probed C library contract.

### 5. Artifact consumption after build

That belongs primarily to artifact-dependency / packaging lanes.
P-0508 may say which unit staged an artifact, but not define every downstream packaging policy.

## Core anti-flattening rule

Do not collapse these distinct claims into one fake “delegated build works” verdict:

1. **the units are ordered coherently**,
2. **the outputs are attributable**,
3. **the authority route is explicit**,
4. **the bridge posture is supportable**,
5. **and the new revision did not drift in a surprising way**.

A workflow can satisfy one or two of those and still be unreviewable.
