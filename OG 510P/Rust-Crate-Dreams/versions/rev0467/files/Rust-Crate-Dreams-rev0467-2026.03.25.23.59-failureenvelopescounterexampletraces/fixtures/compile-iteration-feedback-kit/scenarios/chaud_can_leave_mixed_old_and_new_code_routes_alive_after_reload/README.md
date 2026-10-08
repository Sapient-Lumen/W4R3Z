# Chaud can leave mixed old and new code routes alive after reload

This scenario freezes the fact that Chaud activation is entrypoint-gated and that old code can survive after reload through function pointers or trait objects.
That means mixed-generation execution can persist even after a successful hot-reload event.
