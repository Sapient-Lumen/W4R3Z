# Wake from amnesia — rev0090

You are in the native/GCC safety branch. The current head is rev0090.

Read first:

```text
docs/938-rev0090-nativehandoff-relaunchgate-loaderseal.md
```

The design rule is:

```text
cold-start + probe corpus + loader-GC -> relaunch candidate only
relaunch candidate + prior native lane revalidation -> no-network relaunch plan only
relaunch plan + loader seal -> restart-sticky evidence only
```

None of those steps loads or dispatches native code. Python fallback remains active and Python remains the oracle.
