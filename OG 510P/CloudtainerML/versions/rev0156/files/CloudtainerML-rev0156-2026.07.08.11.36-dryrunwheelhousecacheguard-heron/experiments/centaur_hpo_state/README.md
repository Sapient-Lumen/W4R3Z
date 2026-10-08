# Centaur HPO State Probe

A toy HPO/autoresearch probe inspired by the paper on LLM agents vs classical HPO and Centaur-style hybrids. It simulates an OOM cliff and compares stateless domain proposals, random/TPE/CMA-ish baselines, and a hybrid that combines optimizer state with domain priors.

Run:

```bash
python experiments/centaur_hpo_state/centaur_hpo_probe.py
```
