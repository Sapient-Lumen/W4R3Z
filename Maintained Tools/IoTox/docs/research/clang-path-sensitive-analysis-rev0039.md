# Focused Clang path-sensitive analysis — rev0039

- **Date checked online:** 2026-08-19 America/New_York
- **Scope:** local source-level defect search for four admission and pressure-control translation units
- **Toolchain used by the retained lane:** the Clang compiler selected by the qualified `clang-debug`
  CMake preset

## Primary interfaces reviewed

The construction checked the current primary documentation:

- Clang Static Analyzer command-line usage:
  `https://clang.llvm.org/docs/analyzer/user-docs/CommandLineUsage.html`
- Clang analyzer configuration, including `mode=deep`:
  `https://clang.llvm.org/docs/analyzer/user-docs/Options.html`
- CMake compilation database generation:
  `https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html`

Clang documents direct `clang --analyze` operation as analysis of one translation unit. Its analyzer
configuration documents `deep` and `shallow` modes and identifies `deep` as the default. CMake documents
`compile_commands.json` as machine-readable exact compiler calls for project translation units when the
supported generator exports them.

## Applied lane

`tools/focused-static-analysis.py` reads the qualified Clang Debug compilation database and selects
exactly these source files by normalized repository path:

```text
src/terminal_profile.cpp
src/terminal_cgroup.cpp
src/agent.cpp
src/local/runtime_tree.cpp
```

For each selected file, the tool requires exactly one compile-database entry and a Clang driver. It
retains the generated preprocessor definitions, include paths, language mode, debug configuration, and
warnings; removes only compile/dependency output arguments and the original source argument; then adds:

```text
--analyze
-Xanalyzer -analyzer-output=text
-Xanalyzer -analyzer-config -Xanalyzer mode=deep
-o /dev/null
```

The process runs without a shell, from the compile entry's exact working directory, with a bounded
per-translation-unit timeout. A missing or duplicate target, malformed compilation database, non-Clang
compiler, process-launch failure, timeout, nonzero exit, or any nonempty analyzer output fails the lane.
The successful terminal marker is exactly:

```text
focused-static-analysis=pass files=4 diagnostics=0
```

`tools/build-matrix.sh` runs the lane after the ordinary Clang Debug build and retains a dedicated log.
`tools/refresh-retained-artifacts.sh` requires one clean per-file result, one terminal analyzer marker,
no failure marker, the same single marker in the complete matrix transcript, and one terminal
`final-source-matrix=pass`. Missing, duplicated, truncated, concatenated, or failed evidence is rejected.

## Why these units

The selected translation units hold the highest-consequence local paths added or composed by the recent
cgroup work:

- exact terminal-profile and aggregate resource policy validation;
- delegated-root cgroup accounting, PSI sampling, trigger registration, monitor handoff, and admission;
- Agent startup ordering and new-session mutation gates;
- owner-private runtime projection of policy and controller state.

This is a focused supplement to warnings-as-errors compilation, deterministic tests, sanitizers,
ThreadSanitizer, and fuzzing. It is not a replacement for any of them.

## Retained limits

A zero-diagnostic run means only that this Clang analyzer configuration emitted no report for the four
selected translation units on the analyzed source and toolchain. It does not prove absence of defects,
exercise cross-translation-unit analysis, validate kernel behavior, establish coverage, replace live
cgroup/PSI qualification, or imply that unselected code was analyzed. The lane deliberately records no
HTML or source-containing report when clean; the retained log contains only selected file names, pass
markers, and the terminal summary.
