# Wake from amnesia — rev0087

Remember: rev0081 through rev0087 are not a native rewrite. The native line exists to keep optional GCC leaf kernels narrow, reproducible, auditable, and fallback-bound.

rev0087 adds the lifecycle seam after selection/promotion: load permission, crash memory, and performance evidence. Performance cannot promote native. Crash evidence cannot be garbage-collected as a log message. Native load is still no-network dry permission.
