# Review queue priority method — rev0009

The review queue translates source-inventory shells into next actions. It does not decide the status of any matter.

Priority rules:

- P0: status/effect-sensitive materials, including orders, judgments, termination/dismissal documents, motions, closure signals, and any matter with a rev0008 status-proof bundle.
- P1: findings carriers and agreement/decree carriers.
- P2: monitoring/compliance reports and litigation-position materials.
- P3/P4/P5: technical, transmittal, public-explainer, administrative, and source-entry materials.

A queue ticket must preserve blockers. If a ticket does not say what is blocked, it is unsafe.
