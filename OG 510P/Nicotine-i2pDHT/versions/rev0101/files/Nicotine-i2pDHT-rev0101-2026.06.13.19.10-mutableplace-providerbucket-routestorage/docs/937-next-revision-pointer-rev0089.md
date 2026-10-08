# Next revision pointer rev0089

Suggested next: **rev0090 `nativehandoff-relaunchgate-loaderseal`**.

Focus:

```text
cold-start + probe-corpus + loader-GC -> no-network relaunch candidate
relaunch candidate -> dispatch still blocked until parity/selection/load lanes revalidate
loader seal -> restart memory for the relaunch candidate without dynamic loading
```
