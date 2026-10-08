# Public-evidence-custody versus fresh-host-reinstantiation-closure gate

Purpose: split the archive's **witness-package progress** one step further.
A candidate should not earn the same witness credit merely because it can **place the decisive evidence bundle under durable public custody strong enough for outsiders to extract, identity-check, preserve, cite, transfer, and later reopen it** and because it can **let outsiders rebuild the executable evidential process on a fresh host or stack from the public bundle itself, with software identity, environment materialization, and rerun semantics explicit enough that reenactment is not hostage to one privileged lab, service, or operator memory chain**.
Those are related, but they are not the same achievement.

Read this together with:
- `docs/40-model/empirical-contact-burden-router.md`
- `docs/40-model/witness-closure-gate-family-frame.md`
- `docs/40-model/public-adjudication-vs-public-evidence-custody-closure-gate.md`
- `docs/40-model/local-law-vs-cosmological-package-vs-witness-package-split.md`
- `docs/40-model/completion-bid-cashout-sieve.md`

## Compression verdict

Inside the archive's witness package, once a lane has already moved beyond public adjudication and public evidence custody, the current score should now distinguish four nested layers:

1. **public evidence-custody closure** — the decisive evidence bundle or reference object is stably extractable, versioned, fixity-checkable, preservable, citable, and reopenable beyond one privileged repository or operator chain;
2. **fresh-host reinstantiation closure** — outsiders can take that public bundle, identify the exact workflow / software / environment objects it depends on, materialize an executable environment on a fresh host or stack, and rerun or rehydrate the evidential process under declared equivalence rules without privileged manual setup;
3. **independent implementation closure** — outsiders can derive a genuinely separate implementation from public semantics, test it against a public conformance clause, and recover the same evidential class without carrying the originating executable lineage itself;
4. **local public witness closure** — a lane can say where the physical records live, what stabilizes them, how they are reread, why they remain public evidence, and why that empirical loop is not mainly outsourced.

A lane may earn real credit on layer 1 while still being weak on layer 2.
That is progress.
It is just not yet fresh-host reinstantiation closure, much less independent implementation closure or full witness closure.

## Why this gate exists

Shared witness-gate scaffolding now lives in `docs/40-model/witness-closure-gate-family-frame.md`. This document only names the pair-specific inflation move below.

**durable public possession of the evidence bundle being retold as if outsiders therefore already possessed a public way to reinstantiate the evidential process itself on fresh infrastructure.**

That inflation can happen in at least seven ways:
- a lane can release outputs, logs, and artifacts while withholding the executable workflow plan that generated them;
- a lane can ship code or notebooks while leaving dependency versions, container digests, or workflow-engine semantics tacit, so reenactment silently depends on the original operator's remembered setup;
- a lane can expose a container image tag while failing to pin the content-addressed image, layers, or exact source tree, so later users inherit a nearby environment rather than the adjudicated one;
- a lane can publish a workflow description while leaving site-bound scheduler rules, credential assumptions, storage mount conventions, or hardware expectations implicit, making the supposed public rerun path host-specific;
- a lane can preserve code under mutable branch names or repository pointers rather than intrinsic identifiers, so later reinstantiation cannot prove that the same software object is being used;
- a lane can preserve everything needed for view-only archive inspection yet still require privileged dashboards, internal secrets, or manual intervention before the run can actually be rehydrated on a new host;
- or a lane can support rerun claims only inside the original service account or cloud tenancy, so fresh-host closure is replaced by continued dependence on one live operator stack.

## The five-step fresh-host-reinstantiation test

### 1. Executable plan, not just stored outputs

Before awarding reinstantiation credit, the archive should ask whether the public bundle contains an executable account of the evidential process rather than merely its products.
At minimum, a lane should disclose:
- the workflow, script graph, orchestration plan, or equivalent execution object,
- the named inputs, outputs, and step ordering that governed the decisive run,
- the parameterization or configuration state that matters for rerun,
- and which parts of the evidential process still exist only as operator memory, private runbooks, or portal-side buttons.

A lane that wins only here earns **public evidence-custody credit**, not yet fresh-host reinstantiation closure.

### 2. Public software identity and dependency closure

A lane earns more than custody credit only when outsiders can tell which software objects and dependencies must be reinstantiated.
At minimum, the archive should ask:
- what persistent software identifiers, source revisions, or equivalent intrinsic identities attach to the executable objects,
- what dependency manifests, lockfiles, package graphs, or image digests define the operative environment,
- how the workflow points to those exact software objects rather than to mutable branch tips or floating tags,
- and whether later users can verify that the retrieved software is exactly the intended one.

Without that route, apparent reinstantiation may still be public custody with informal setup folklore.

### 3. Host-independent environment materialization

A lane earns stronger reinstantiation credit only when the public bundle can be turned into a runnable environment on a new host or stack.
At minimum, the archive should ask:
- what portable environment format or build recipe exists,
- whether that format is content-addressed or otherwise identity-checkable,
- which host assumptions still remain: operating system, architecture, accelerator type, scheduler, storage layout, network access, secrets, or licensed dependencies,
- and whether those assumptions are declared as debts rather than hidden in the success story.

Without those answers, apparent reinstantiation may still be a frozen bundle whose operational semantics survive only on the original host.

### 4. Declared rerun semantics and equivalence test

A lane earns still stronger reinstantiation credit only when outsiders know what counts as a successful reenactment.
At minimum, the archive should ask:
- which run outputs must match exactly and which may vary within declared tolerances,
- how randomness, nondeterminism, hardware variation, or external-service drift are handled,
- whether test cases, example datasets, or workflow-run provenance are public enough to evaluate reenactment quality,
- and what public state follows if the rerun reproduces only approximately, partially, or not at all.

Without that route, apparent reinstantiation may still be symbolic executability without a public criterion for sameness.

### 5. Fresh-host rerun path beyond one privileged operator stack

A lane earns **fresh-host reinstantiation closure** credit only when later users can move from public custody to actual reenactment without depending on the originating host's continued special status.
At minimum, it should name:
- the executable plan,
- the stable software identities and dependency closure,
- the host-independent environment materialization path,
- the declared rerun / equivalence rule,
- and the remaining debt to full local record-carrier, rereadability, and candidate-native objectivity closure.

This is still not the same thing as full local public witness closure.
A lane may support fresh-host reinstantiation very well while still borrowing one inherited code lineage or one under-specified semantic contract; `docs/40-model/fresh-host-reinstantiation-vs-independent-implementation-closure-gate.md` now treats that stronger independent-implementation burden explicitly before the archive talks as if reenactment were implementation-independent public evidence.

## Common failure modes

1. **custody-to-reinstantiation inflation** — durable public possession of the bundle is retold as if outsiders therefore already possess a fresh-host rerun path.
2. **output-only openness** — public artifacts exist, but the executable workflow object is missing.
3. **mutable-software shadow** — the rerun path points to floating repository branches, image tags, or undocumented package resolution rather than fixed software identities.
4. **host-bound container theater** — a container or image exists, but it still depends on one scheduler, tenancy, filesystem convention, or secret operator configuration.
5. **equivalence silence** — a rerun is called successful without a declared match criterion, tolerance window, or treatment of nondeterminism.
6. **portal-only reenactment** — outsiders may click rerun inside the original service, but cannot materialize the workflow on a genuinely fresh host.
7. **software-custody gap** — data and outputs are preserved, but the operative code object, environment recipe, or image digest is not under equally stable public identity.

## Compact current readout

- **Workflow Run RO-Crate practice** makes the first burden explicit by treating workflow-run provenance as a bundle of inputs, outputs, code, and execution metadata rather than as outputs alone, with interoperable adoption across multiple workflow systems.
- **Workflow RO-Crate / WorkflowHub practice** makes the executable-object burden explicit by packaging workflows as reusable executable objects with declared main workflows, metadata, examples, and tests rather than as prose descriptions alone.
- **Current OCI image standards** make the environment-materialization burden explicit by treating images as content-addressable manifests, indexes, layers, and layouts rather than as vague “same container” claims.
- **Current SWHID practice and standardization** make the software-identity burden explicit by giving software artifacts intrinsic, verifiable identifiers that can be checked against the object itself rather than against one repository's mutable state.
- **Current reproducible-research platform work** makes the public side concrete by showing that version-controlled, containerized environments can let later users execute, reuse, and reproduce studies — including work over a decade old — without manual retrieval or platform-specific setup.

That does not refute current observer-relative or bridge-theory programs.
It just means they have not yet paid this stronger fresh-host-reinstantiation debt.

## Net rule

Within the archive:
- public evidence-custody closure earns real witness-package credit;
- but it does **not** yet count as fresh-host reinstantiation closure;
- and fresh-host reinstantiation does **not** yet count as independent implementation closure or local public witness closure.

Any future completion bid or bridge-family claim that wants stronger witness credit should now say not only what evidence bundle outsiders can possess, but how they can recover the executable workflow object, verify the exact software and environment identities, materialize the run on a fresh host, and judge whether the reenacted run is the same public evidence rather than a nearby imitation.
