# Forecast sparse routing probe

A toy simulator for decoupled sparse attention / forecast-routing. It asks when a
forecast signal for the next layer's KV needs beats reusing current query scores
or a shared once-computed route.

Run:

```bash
python experiments/forecast_sparse_routing/sparda_forecast_probe.py
```
