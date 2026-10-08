# Architecture

GlassTTY is a local-first control plane for browser-native AI systems.

## System layers

### 1. Browser surface
A real visible browser tab on an official AI web surface.

### 2. Extension layer
The Chromium MV3 extension provides:
- page presence and tab awareness
- content-script and receiver discovery
- side-panel operator surfaces
- probe and diagnostic collection
- a browser-native action boundary

### 3. Native bridge layer
The native host and broker provide:
- local machine-facing command handling
- process and session continuity outside the browser
- CLI access and richer local artifact output

### 4. Adapter layer
Adapters translate a specific browser surface into shared workflows and shared state families.

Adapters are responsible for:
- supported-surface detection
- receiver/composer resolution
- read/write/submit heuristics
- latest-turn and generation-state extraction
- surface-specific evidence capture hints
- drift notes and recovery hints

### 5. State and evidence layer
GlassTTY should emit:
- structured state families
- action outcome records
- fixture/probe/support artifacts
- ledgers and diffs
- support truth and release-gate evidence

### 6. Operator and agent layer
GlassTTY must support:
- direct human CLI operation
- visible browser-side interaction
- assistive and policy-bound agent execution
- approval, stop-condition, and audit records

## Architectural principles

### Generic core, explicit adapters
The bridge, state contracts, evidence model, and operator semantics should stay generic.
Surface-specific logic belongs in adapters and surface profiles.

### Workflow-first support
Support should be defined by named workflows, not by vague surface claims.

### State before convenience
If a new feature reads or writes meaningful browser information, it should usually fit into the structured state model.

### Evidence before confidence
If a support claim or regression diagnosis cannot point to artifacts, the repo should treat it as weak knowledge.

### Visible execution
The browser remains a visible execution surface even when a local LLM is driving.

## Intended evolution

The earlier architecture was enough for “bridge a browser tab to a terminal.” The new target is broader:

- multiple official surfaces
- shared workflows across those surfaces
- shared state families across those surfaces
- drift detection and support truth as first-class infra
- agent execution layered on the same visible bridge

That means the architecture should now be read less as “extension + daemon” and more as:

**surface adapters + generic bridge + structured state + evidence and support truth + operator/agent control**
