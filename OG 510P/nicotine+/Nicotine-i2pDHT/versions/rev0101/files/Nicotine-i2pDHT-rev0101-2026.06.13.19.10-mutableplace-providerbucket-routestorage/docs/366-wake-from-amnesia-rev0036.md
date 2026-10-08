# Wake from amnesia — rev0036

You are in rev0036. The cube is still designing a consumer-agnostic mutable DHT over I2P, with Nicotine only a distant downstream consumer.

What changed since rev0035:

- rev0035 made startup profiles explicit.
- rev0036 asks what a giving profile actually offers.
- `servicecatalog.py` signs the garden/bridge service surface.
- `loadsheath.py` decides per-window service load and useful refusals.
- `profilegc.py` keeps hard-negative memory across profile/config cleanup.
- `foldregistry.py` starts consolidating fold/audit navigation.

Do not open a live SAM socket yet. Keep treating router work as shadow/harness until local risk boundaries stabilize.
