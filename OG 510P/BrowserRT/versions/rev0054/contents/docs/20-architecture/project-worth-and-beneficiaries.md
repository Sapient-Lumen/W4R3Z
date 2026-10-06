# Project worth and beneficiaries

Current revision: rev0054

## Project identity

BrowserRT is a browser userspace kernel kit for heavy local web apps. It coordinates browser primitives that are individually powerful but painful in combination: Workers, SharedArrayBuffer, OPFS, Web Locks, WebGPU/WebNN frontiers, object refs, storage lanes, overload governors, traces, and tests.

## Continue, but narrow

The continuation verdict is not “build everything.” It is:

> Continue if the first wedge is small, testable, and useful: BrowserRT Kernel Kit.

That means the near-term architecture should optimize for:

- boot/capability report;
- worker agents;
- object refs;
- bounded mailboxes;
- OPFS block-store adapter;
- storage-lane scheduler;
- overload/admission/retry governors;
- trace logs;
- manifest-driven tests;
- clear non-claims.

## Beneficiary ranking

### 1. Browser IDE and agent-tool builders

They need local artifact execution, zip/workbench testing, worker orchestration, trace artifacts, and reproducible slices. BrowserRT already lives in that world.

### 2. Heavy data/media/visualization web apps

They need to keep the main thread responsive while doing large local work. BrowserRT's worker lanes, bounded queues, OPFS refs, and trace surfaces are relevant.

### 3. Local-first app builders

They need browser storage and cross-tab coordination, but also honest limits. BrowserRT can help by making provider contracts and non-claims explicit.

### 4. Library authors

They often rebuild worker pools, transfer protocols, queues, and storage wrappers. BrowserRT could provide a shared substrate if it stays small and framework-free.

### 5. Privacy/cloud-cost sensitive teams

They may benefit if BrowserRT makes client-side compute/storage safer and easier, but this needs external demand evidence.

## Risk of not being useful

BrowserRT becomes useless if it is too general too soon. It must not ship as a pile of nouns. Future sessions should ask: what heavy browser app becomes materially easier because this exists?

## Adoption wedge

The first real adoption wedge should be a tiny package and demo:

```txt
boot runtime
spawn worker agent
send object ref
write/read OPFS block through storage lane
apply admission/retry/breaker policy
emit trace
show test artifact
```

That is concrete enough to earn respect and small enough to test.

## Rev0041 audit keywords

continue-but-narrow. BrowserRT Kernel Kit. Who benefits: browser-heavy app builders, browser IDE and agent-tool builders, local-first app builders, data/media web apps, library authors, and privacy/cloud-cost sensitive teams.

No market validation claim. No user-demand proof. No product-market-fit claim. No production runtime claim. No WebGPU performance claim. No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim. No cross-browser conformance claim.
Current audit slice: `facility:project-worth-audit`.

## Rev0049 project-worth carry-forward guard

Current verdict: **continue-but-narrow**. The narrow wedge remains **BrowserRT Kernel Kit**.

Who benefits: browser IDE / agent workbench builders, heavy local browser app builders, local-first app builders, library authors who keep rebuilding worker/storage/trace facilities, privacy/cloud-cost-sensitive teams, and future BrowserRT sessions that need a legible office.

Required non-claims carried forward:

- No market validation claim.
- No user-demand proof.
- No product-market-fit claim.
- No production runtime claim.
- No WebGPU performance claim.
- No OPFS durability, quota, eviction, crash-recovery, or browser-restart claim.
- No cross-browser conformance claim.

