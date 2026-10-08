# Public trace device/dtype/timing contract — REV0103

Public trace evidence now binds runtime identity in addition to prompt/cache/backend identity.

Required capture defaults:

```bash
TRACE_TORCH_DTYPE=float32
TRACE_DEVICE=auto
ATTENTION_IMPLEMENTATION=eager
CACHE_IMPLEMENTATION=dynamic
```

The capture helper records requested/resolved dtype, requested/actual device, parameter dtype/device sets, CUDA availability/name/capability, synchronized timing-clock metadata, and an explicit `named_hardware_timing_measured=false` boundary. Capture timing is not promotion timing; sparse-vs-dense named-hardware timing remains blocked until a separate benchmark lane exists.
