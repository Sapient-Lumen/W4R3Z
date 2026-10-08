# 59 — PTY + Agent I/O Notes (v0.19)

Your workflow uses multiple terminal windows running CLI clients.
The router needs reliable multi-process I/O:
- spawn and manage child processes OR attach to existing PTYs
- read partial output
- avoid deadlocks
- survive terminal weirdness

## 1) PTY abstraction options
### portable-pty (recommended starter)
- cross-platform trait-based API
- used by wezterm ecosystem
- gives you master/slave handles and resizing

Caveats:
- Windows toolchain/support may be tricky depending on targets.
- You still need your own async integration strategy.

## 2) Async integration patterns
Common pattern:
- one blocking reader thread per PTY (or per group), forwarding chunks into tokio channels
- tokio task parses chunks and extracts CTRL early

Avoid:
- unbounded channels from PTY readers (memory blowup)
- waiting on full output before parsing

## 3) “Stop reading after CTRL?”
Optionally, once CTRL is observed you may:
- stop reading until next slice, OR
- keep draining output but prioritize control-plane commit

This is a throughput/observability tradeoff:
- stopping saves bandwidth
- draining preserves debugging info (ledger)

## 4) Chunking and terminators
Because outputs can be truncated:
- parse should be incremental
- treat missing terminators as common
- rely on JSON healing + repair ladder

## 5) CLI client quirks
Many CLI LLMs:
- stream tokens slowly
- print spinners/ANSI control codes
- wrap lines unexpectedly
You may need:
- ANSI stripping for parsing
- separate raw log capture for ledger

For ANSI/control-code cleanup and dual-stream logging, see 73_ansi_and_terminal_control_handling.md.
