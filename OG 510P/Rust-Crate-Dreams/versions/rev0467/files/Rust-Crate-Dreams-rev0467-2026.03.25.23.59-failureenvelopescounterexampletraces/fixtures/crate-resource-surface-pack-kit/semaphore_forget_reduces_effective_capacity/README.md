# Semaphore permit-forget shrinks effective capacity scenario

Focus: `SemaphorePermit::forget` means effective capacity can shrink after initialization.

Resource-surface reading: the support story must distinguish constructor-time capacity from runtime-effective capacity.
