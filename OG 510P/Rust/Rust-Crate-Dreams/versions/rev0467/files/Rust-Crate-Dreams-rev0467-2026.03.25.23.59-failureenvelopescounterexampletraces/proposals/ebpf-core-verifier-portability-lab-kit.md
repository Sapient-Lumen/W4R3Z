---
id: P-0216
title: eBPF CO-RE + Verifier Portability Lab Kit — deterministic verifier reports, CO-RE probes, and repro bundles
status: idea
domains: [ebpf, linux, observability, networking, security, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://docs.kernel.org/bpf/verifier.html
  - https://libbpf.readthedocs.io/en/latest/libbpf_overview.html
  - https://docs.ebpf.io/concepts/core/
  - https://nakryiko.com/posts/bpf-portability-and-co-re/
  - https://bpftool.dev/
needs:
  - A practical, Rust-centric way to make eBPF portability failures reproducible (verifier differences, BTF/CO-RE reloc issues, helper availability).
  - Deterministic, diffable verifier output and “why it failed” explanations.
  - A portable bundle format that can be attached to issues/CI artifacts without shipping sensitive host details.
risks:
  - Kernel-version matrix and feature gates are huge; must focus on limited program types + curated kernels.
  - Verifier behavior is complex and output formats vary; need canonicalization/normalization.
---

## Problem

eBPF programs often fail in production not because the program is “wrong”, but because of **kernel-version differences**, verifier constraints, missing helpers, or CO-RE relocation mismatches.

The kernel verifier behavior is documented, and safety is established by control-flow validation plus path exploration.
Source: https://docs.kernel.org/bpf/verifier.html

CO-RE (“Compile Once – Run Everywhere”) depends on BTF + libbpf relocation machinery.
Source: https://libbpf.readthedocs.io/en/latest/libbpf_overview.html
Source: https://docs.ebpf.io/concepts/core/

But engineers still lack a **standard interop lab** that can answer:
- “Why does this program load on kernel A but not kernel B?”
- “Which CO-RE relocations failed and where?”
- “What’s the smallest repro we can share?”

## What this crate should provide

### 1) `ebpf-portability-lab` core
- Workspace with:
  - `lab-core` (bundle formats, canonicalization, runner APIs)
  - `lab-kernel-matrix` (known kernels + container/VM descriptors)
  - `lab-bpftool` adapter (introspection via bpftool)
  - `lab-libbpf` adapter (optional)

bpftool is a reference utility for inspecting/managing BPF objects.
Source: https://bpftool.dev/

### 2) Deterministic verifier capture + canonicalization
- Capture:
  - verifier logs
  - `BPF_OBJ_GET_INFO_BY_FD` snapshots (program + map metadata)
  - helper availability and feature bits (when accessible)
- Canonicalize:
  - strip addresses and unstable IDs
  - normalize kernel strings
  - structure key sections into JSON (insn index, reg state summaries, failure reason)

### 3) CO-RE “relocation explain”
- For BPF ELF objects, extract:
  - BTF IDs referenced
  - field offsets expected vs found
  - relocation sites
- Emit a machine-readable report for “this field changed” portability issues.

CO-RE mechanics and portability rationale are documented (and widely cited) by Alexei Starovoitov/Andrii Nakryiko community work.
Source: https://nakryiko.com/posts/bpf-portability-and-co-re/

### 4) Repro bundles: `*.bpfbundle.zip`
Redaction-friendly artifact:
- `program.o` (optional; allow “hash-only” mode)
- `btf.json` (selected type info only) or `btf.hash`
- `kernel.json` (version + config fingerprint)
- `verifier.log` + `verifier.json` (canonical)
- `core-relocs.json`
- `bpftool.json` (sanitized snapshots)
- `lab.json` (crate version, runner version)

### 5) UX
- `cargo ebpf-lab load program.o --kernel linux-6.6 --ptype tracing`
- `cargo ebpf-lab diff a.bpfbundle.zip b.bpfbundle.zip`
- `cargo ebpf-lab bisect --kernels 5.15..6.8`

## MVP plan (4–8 weeks)

1. Bundle format + canonical verifier parser (start with text, evolve to structured)
2. Single backend: local kernel + bpftool adapter
3. CO-RE relocation report for a subset of reloc kinds
4. Curated kernel matrix (3–5 kernels) via containers/VM recipes

## v1 plan (8–12 weeks)

- Expand program types coverage (xdp/tc/tracing) and helper maps.
- “Explain” engine: common failure pattern classifiers.
- Optional integration with Rust eBPF frameworks (Aya/cilium-ebpf) without coupling.

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (portable verifier+CO-RE evidence bundles + diffs)
