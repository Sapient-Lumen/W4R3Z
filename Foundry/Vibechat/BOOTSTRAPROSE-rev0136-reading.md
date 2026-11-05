# Vibechat rev0136 / Fathom: readable current handoff

The complete opening and sections 360–361 of the supplied [Vibechat](README.md) bootstrap are reproduced below. This is the 13,996-byte current-revision prefix of a 12,374,892-byte document whose remaining bytes preserve earlier history. GitHub cannot display the complete bootstrap in its file viewer.

**Source:** Vibechat rev0136 / Fathom `BOOTSTRAPROSE.md`, dated 22 October 2026 and supplied by h0p3. **Selection and navigation:** Lumen. All source wording, code examples, tables and checklists are unchanged. The seven marked passages, concatenated in order, reproduce original lines 1–206 exactly.

**Reading scope:** “current,” measured results, environment descriptions and next-step instructions below belong to that supplied handoff. They are not a new test run, a statement about this reader’s machine or permission to perform the listed actions. The recorded passing checks travel with the original qualification limits and unfinished work. Paths named in the passages refer to the supplied project and evidence supplement.

Use this companion for reading. Keep the [complete bootstrap](BOOTSTRAPROSE.md), matching [HTML carrier](Vibechat.html) and [evidence supplement](Vibechat-rev0136-evidence.zip) for continuation. The companion does not replace the full history required by the supplied package contract. Original attribution and component notices remain with those artifacts; no new license is assigned here. The [external owner declaration](../../LEGAL-NOTICE.txt) remains separate from third-party terms, as explained in [preservation and rights](../../PRESERVATION.md).

## Source identity

- Repository path: `Foundry/Vibechat/BOOTSTRAPROSE.md`.
- Source commit: `96d0d268df22906d6f2e1e9b510bfb689bcbdcb7`.
- Git blob: `a5c1a12c266a4cbcdf5a6ab3374307664e14d70a`.
- Complete source SHA-256: `cd4fbccfa5aa272fb012366b00ea64582cf9d82f24e3988da8ef5bd15a1c6dfb`.
- Exact current-prefix SHA-256: `e9faddba186d05352192c645607a677daa65675d28428a08372cc6f8234a3bdf`.
- [Pinned complete original](https://github.com/Sapient-Lumen/W4R3Z/blob/96d0d268df22906d6f2e1e9b510bfb689bcbdcb7/Foundry/Vibechat/BOOTSTRAPROSE.md) · [Raw original for download](https://raw.githubusercontent.com/Sapient-Lumen/W4R3Z/96d0d268df22906d6f2e1e9b510bfb689bcbdcb7/Foundry/Vibechat/BOOTSTRAPROSE.md).
- [Machine-readable byte ranges and checksums](BOOTSTRAPROSE-rev0136-reading.json).

## Find a passage

- [Current-revision opening](#source-handoff)
- [360: framing problem and Fathom change](#source-framing)
- [Research and qualification boundary](#source-qualification)
- [Preserved product behavior](#source-preserved)
- [361: exact evidence and package contract](#source-evidence)
- [Open qualification work](#source-queue)
- [The supplied next-step instruction](#source-next)

<a id="source-handoff"></a>

**Source passage: Current-revision opening.** Original lines 1–4.

<!-- source-excerpt vibechat-L1-L4 -->

# BOOTSTRAPROSE — rev0136 / Fathom / current-first continuation

This is the current handoff. Read sections 360–361 before the preserved history. Earlier receipts retain their original scope. Continue from this exact carrier rather than rev0135, an intermediate repack, or a source-only proxy hypothesis.


<!-- /source-excerpt vibechat-L1-L4 -->

<a id="source-framing"></a>

**Source passage: 360: framing problem and Fathom change.** Original lines 5–102.

<!-- source-excerpt vibechat-L5-L102 -->

## 360. Rev0136 / Fathom — definite request framing for the strict Waystation

**Date:** 2026-10-22 (America/New_York)  
**Product:** `Vibechat.html`, 10,933,910 bytes  
**Product SHA-256:** `e48f115825f5b35b4e2b749813da028b5dadea4e6321cd71f59a5bb755897a7e`  
**Predecessor:** rev0135 / Longwatch, 10,923,213 bytes, SHA-256 `8acca0ecf53a641c78e2df0d3469c9094932a6981e3ab6ecf4859a5b7452459c`  
**Preserved predecessor bootstrap:** 12,360,896 bytes, SHA-256 `e3457abd4df830dec1b721bf9736f447455260703d9bdf985e7957cdc6e78374`

### Measured predecessor defect

Longwatch generated a public request-body size gate:

```caddyfile
request_body {
    max_size 20KB
}
```

Its `reverse_proxy` block did not buffer request bodies. The strict Waystation backend deliberately rejects `Transfer-Encoding`, requires one decimal `Content-Length`, and admits at most 16 KiB. A request can therefore satisfy the public media-type and size rules while still reaching the HTTP/1.1 loopback upstream with unknown length and transfer coding.

The exact rev0135 carrier was started on owned loopback. Two small standard-library Go reverse-proxy modes were placed in front of it:

1. an ordinary streaming mode that preserved an unknown-length client body; and
2. a bounded complete-buffer mode with a 20,000-byte limit.

The measured result was:

| Route | Client framing | Upstream framing | Waystation result |
|---|---|---|---:|
| Ordinary control | `Content-Length` | `Content-Length` | HTTP 200 |
| Ordinary unknown length | chunked | chunked | HTTP 400 |
| Bounded complete buffer | chunked | definite `Content-Length` | HTTP 200 |

The transfer-coded request was refused with the fixed message `Chunked request bodies are not accepted`. The two successful publications were retained; the refused body was absent; SQLite integrity was `ok`; and neither proxy nor Waystation emitted a traceback or copied request text to diagnostics.

The structured predecessor receipt is `reports/verification/rev0135-edge-request-framing-probe.json`. It binds the exact Longwatch carrier hash and records 12/12 scoped assertions.

### Fathom

Fathom adds one line to the generated Caddy reverse proxy:

```caddyfile
request_buffers 20KB
```

The complete generated edge block now contains both the public size gate and the loopback framing buffer:

```caddyfile
request_body {
    max_size 20KB
}
reverse_proxy 127.0.0.1:PORT {
    lb_retries 0
    unhealthy_request_count N
    request_buffers 20KB
    transport http {
        dial_timeout 5s
        keepalive off
        max_conns_per_host N
        network_proxy none
    }
}
```

The Waystation message ceiling is 16,384 bytes. The 20,000-byte edge buffer is therefore larger than every backend-admissible body. Once the complete body fits in that bounded buffer, the generated edge can send the loopback request with a definite `Content-Length` instead of transfer coding.

Deployment-kit output and the kit manifest now publish the framing contract explicitly:

```text
edge_request_body_max_size = 20KB
edge_request_body_max_bytes = 20000
edge_request_buffer = 20KB
edge_request_buffer_bytes = 20000
edge_upstream_request_framing = content-length-after-complete-buffer
edge_request_framing_scope = bounded per-request compatibility buffer
```

The generated operator guide explains the boundary. This is a maximum of 20,000 buffered bytes per accepted request, not a total edge-memory ceiling, client-connection ceiling, queue bound, rate limit, host-capacity calculation, or denial-of-service guarantee. Requests marked `Incremental: ?1` are outside the Waystation publication protocol and are not silently made compatible by this setting.

The existing request-body size gate remains in front of the reverse proxy. Oversized input is not buffered without bound. The strict backend remains authoritative: media type, exact route, query refusal, one `Content-Length`, 16 KiB maximum, complete-body read, publication transaction, and storage boundaries are unchanged.

### Exact current-carrier regression

The fifteen-check regression was repeated against the exact rev0136 carrier:

- the generated Caddyfile contains both `max_size 20KB` and `request_buffers 20KB`;
- kit output and manifest bind the exact current carrier and publish the same 20,000-byte values;
- the framing scope states that 16 KiB fits below the buffer and refuses aggregate-capacity claims;
- a known-length control succeeds through ordinary proxying;
- an unknown-length body through ordinary streaming reaches the strict backend as transfer-coded and is refused;
- an unknown-length body through the bounded complete-buffer path reaches the backend with a definite length and succeeds;
- only successful publications are retained;
- the refused body is absent;
- SQLite integrity is `ok`; and
- no traceback or request-sensitive diagnostic is emitted.

The structured result is `reports/verification/rev0136-edge-request-framing.json`. The executable reproducer is `tests/probe-waystation-edge-framing.py`. It compiles a temporary standard-library Go proxy and removes that binary; no compiled probe is packaged.


<!-- /source-excerpt vibechat-L5-L102 -->

<a id="source-qualification"></a>

**Source passage: Research and qualification boundary.** Original lines 103–114.

<!-- source-excerpt vibechat-L103-L114 -->

### Research and qualification boundary

Primary sources reviewed this turn are indexed in `reports/RESEARCH.md` and the carried research source:

- Caddy documents that `request_buffers` reads up to the configured amount before proxying and sets upstream `Content-Length` when the complete body is buffered.
- The exact Caddy v2.11.7 source performs that bounded read and sets both the request content-length field and header when no bytes remain outside the buffer.
- Go documents that an HTTP/1.1 request with a body, unknown non-positive content length, and no identity transfer setting is written with `Transfer-Encoding: chunked`.

The environment still has no Caddy binary. PID 1 is Supervisor, `systemctl is-system-running` reports `offline`, and the cgroup v2 mount is read-only. No administrator policy or host configuration was changed or bypassed.

The regression therefore proves exact Waystation behavior and the standard-library framing mechanism used by Caddy; it does not claim Caddy binary parsing or runtime behavior, installed systemd/cgroup enforcement, HTTP/2 or HTTP/3 edge behavior, public certificates, hostile traffic, aggregate memory capacity, physical storage, physical-browser behavior, or human observation. Preserve an unavailable receipt rather than substituting this analogue for the installed-manager gate.


<!-- /source-excerpt vibechat-L103-L114 -->

<a id="source-preserved"></a>

**Source passage: Preserved product behavior.** Original lines 115–135.

<!-- source-excerpt vibechat-L115-L135 -->

### Preserved product behavior

No person-facing browser screen, invitation format, trust decision, cryptographic primitive, successful message or file envelope, browser-storage schema, retention algorithm, payload budget, account model, automatic retry, deduplication behavior, or delivery claim changed.

Fathom preserves:

- Longwatch’s omission of a premature fixed upstream response-header timeout;
- Splice’s request-count, connection, no-retry, no-keepalive, and no-ambient-proxy controls;
- Keel’s task-pressure-safe worker ownership and timer-free clean stop;
- Berth’s inherited `RLIMIT_NOFILE` minimum and generated `LimitNOFILE`;
- Gatehouse’s pre-worker accepted-socket admission and generated `TasksMax`;
- Reception’s timeout-bounded TLS negotiation in the owned worker;
- Quiesce’s clean-stop SQLite admission fence;
- Headroom’s absolute socket drain and manager allowance;
- Breakwater’s unknown-result rule after response loss;
- Bulkhead’s contained startup and runtime storage failures;
- Whole’s atomic `BEGIN IMMEDIATE` publication transaction; and
- every earlier compatibility and evidence boundary retained in the source graph.

A missing response remains evidence of neither success nor failure. Reconciliation, not blind replay, remains required.


<!-- /source-excerpt vibechat-L115-L135 -->

<a id="source-evidence"></a>

**Source passage: 361: exact evidence and package contract.** Original lines 136–178.

<!-- source-excerpt vibechat-L136-L178 -->

## 361. Exact evidence, package contract, and active queue

Every credited release lane binds product SHA-256 `e48f115825f5b35b4e2b749813da028b5dadea4e6321cd71f59a5bb755897a7e`.

| Lane | Result |
|---|---:|
| Native API and relay transport | **20/20 passed** |
| Diagnostic, Waystation, storage, TLS, worker, edge, shutdown, and terminal | **68/68 passed** |
| Courier transport | **16/16 passed** |
| Combined transport | **104/104 passed** |
| Deterministic protocol review | **28/28 passed** |
| Malformed-input corpus | **49/49 passed** |
| Raw-JSON admission corpus | **96/96 passed** |
| Prekey composition review | **31/31 passed** |
| Exhaustive carrier contract | **212/212 passed** |
| External edge-request-framing probe | **15/15 passed within stated scope** |

The external probe is separate from the 104 transport checks and is not counted twice. A preseal candidate exposed five Longwatch-era status substrings in one historical carrier assertion; the assertion was updated to the equivalent Fathom semantics, the source graph was rebound, and the carrier was resealed. One initial enclosing transport run encountered a timing-sensitive silent-TLS assertion while the host was under concurrent test load; its partial receipt was also discarded. Every credited lane was rerun against the final hash. No failed, partial, candidate-hash, interrupted, or superseded result is packaged as passing evidence.

Final source and build gates:

- the carrier verifies as rev0136 with exactly 150 named members;
- all 99 carried top-level Python files compile;
- all 42 carried top-level JSON files parse;
- client and worker JavaScript syntax and test-driver shell syntax pass;
- all 296 declared source bindings across 32 documents match;
- all 32 declared packet-digest conventions verify;
- the current-status response is 32,711 bytes including its newline, 57 bytes below its fixed 32 KiB boundary;
- TypeScript/Clang rebuilding reproduces `worker.js` and `vendor.json` byte-for-byte;
- fresh extraction and unchanged repacking reproduce `Vibechat.html` byte-for-byte;
- comparison with rev0135 records 43 changed members, zero additions, and zero removals;
- self-comparison records no changes; and
- the external `tests/test.sh` is byte-identical to the carried driver.

The release ZIP root contains exactly two regular files:

```text
BOOTSTRAPROSE.md
Vibechat.html
```

All ancillary material is beneath `reports/` or `tests/`. Preserve this complete bootstrap as the next revision’s unchanged history suffix. Do not package temporary certificates, private keys, runtime databases, compiled probe binaries, candidate artifacts, or failed/partial receipts.


<!-- /source-excerpt vibechat-L136-L178 -->

<a id="source-queue"></a>

**Source passage: Open qualification work.** Original lines 179–200.

<!-- source-excerpt vibechat-L179-L200 -->

### Running checklist

Completed work is retained in `reports/CHECKLIST.md` and removed from the active queue.

- [x] Reproduce the exact rev0135 unknown-length framing mismatch against the strict Waystation backend.
- [x] Preserve the public 20 KB request-body size gate.
- [x] Add a bounded 20 KB complete request buffer inside the generated Caddy reverse proxy.
- [x] Keep the buffer above the 16 KiB backend message ceiling and publish both exact byte values.
- [x] Publish definite upstream framing and a non-capacity scope through kit output, manifest, status, evidence, and operator documentation.
- [x] Verify known-length success, unbuffered transfer-coding refusal, buffered success, retained-state correctness, and SQLite integrity.
- [x] Preserve Longwatch’s no-fixed-response-deadline rule and every Splice/Keel/Berth/Gatehouse boundary.
- [x] Rebind all 296 source declarations across 32 documents and verify all 32 digest conventions.
- [x] Complete all final-hash transport, protocol, parser, composition, carrier, compiler, extraction, repacking, checksum, suffix, and deterministic-package gates.
- [x] Retain the two-core-file root and directory-only ancillary layout.
- [ ] **P0 — installed Caddy/systemd/cgroup execution.** Run the exact generated Fathom contract under an authorized installed manager. Confirm Caddy parsing and request buffering; enforce backend slots, upstream request/connection limits, `TasksMax`, `LimitNOFILE`, `TimeoutStopSec`, client-edge limits, pre-header/TLS admission, kernel queues, reload, clean stop, and forced stop. Include unknown-length HTTP/1.1 plus HTTP/2 and HTTP/3 request-body framing. Preserve an unavailable receipt rather than substituting source inspection or the proxy analogue.
- [ ] **P1 — physical clipboard and lifecycle qualification.** Current Chromium, Firefox, and Safari across desktop, Android, and iOS; permissions, delayed or unresolved reads, backgrounding, freeze/resume, screen lock, navigation, and close/reopen.
- [ ] **P2 — uncoached beginner and assistive-technology observation.** Recovery and ambiguity comprehension, focus, keyboard-only use, screen readers, switch and voice control, Braille, zoom, and constrained layouts.
- [ ] **P3 — ordinary browser navigation and encrypted-storage qualification.** Reload, history/BFCache, independent tabs, restart, termination, memory pressure, eviction, and re-unlock in an authorized browser environment.
- [ ] **P4 — public and physical deployment qualification.** Public certificates, hostile traffic, physical storage and power failure, capacity controls, TURN, and physical cross-network journeys.
- [ ] **P5 — independent security, privacy, and accessibility review.**
- [ ] Keep exactly-once publication, durable peer receipt, durable outbox, multi-device membership, synchronization, conflict resolution, account recovery, and remote deletion as separate protocol projects.


<!-- /source-excerpt vibechat-L179-L200 -->

<a id="source-next"></a>

**Source passage: The supplied next-step instruction.** Original lines 201–206.

<!-- source-excerpt vibechat-L201-L206 -->

### Next `/run`

Start from this exact carrier and two-file-root package. The next service gate remains execution of the generated Fathom Caddy contract under installed systemd/cgroup. If that environment remains unavailable, advance only another boundary that can be measured without changing administrator policy.

---


<!-- /source-excerpt vibechat-L201-L206 -->

[Vibechat introduction](README.md) · [Complete original](BOOTSTRAPROSE.md) · [Foundry](../README.md) · [Catalog](../../CATALOG.md)
