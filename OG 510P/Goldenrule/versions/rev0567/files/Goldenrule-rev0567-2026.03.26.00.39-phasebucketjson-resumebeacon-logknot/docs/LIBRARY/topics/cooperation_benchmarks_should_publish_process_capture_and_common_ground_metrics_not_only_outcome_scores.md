# Cooperation benchmarks should publish process capture and common-ground metrics, not only outcome scores

Two systems can post similar cooperation rates or task scores while arriving there through very different interaction processes.
That matters for inheritance: a benchmark that only reports final outcomes can hide **brittle reasoning**, **fragile communication**, or **poor repair under misunderstanding**.
Two recent sources make the compact archive rule clear:

- `RS-GR-063` shows that some models achieve seemingly reasonable mixed-motive outcomes while displaying pronounced inconsistencies in their reasoning and communication, so outcome-only evaluation can miss important social-behavior failure modes.
- `RS-GR-064` introduces a human-AI collaboration benchmark centered on common ground, situation awareness, referential coordination, and repair, and reports clear divergences between human-human and human-AI interaction on those process dimensions.

## Minimum contract

Whenever a cooperation benchmark is reported, publish:

1. whether the evaluation is **outcome-only** or **process-aware**;
2. which process channels were captured: **action trajectory**, **message transcript**, **elicited explanation / rationale**, **repair events**, or **common-ground markers**;
3. which process metrics are actually summarized, such as **repair success**, **communication effort**, **grounding success**, **referential coordination**, or another declared proxy;
4. whether those process traces are used only for audit or are part of the **headline benchmark score / profile**;
5. and whether final outcomes are reported separately from process quality rather than blended into one opaque scalar.

## Implementor consequence

Do not treat two benchmark lanes as equivalent just because their final cooperation or task-success rates look similar.
One policy can reach the same endpoint through stable shared understanding, while another gets there through brittle reasoning, accidental success, or high repair burden.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: outcome-only vs process-aware, captured trace channels, and any grounding / repair metrics.
That prevents future sessions from laundering a fragile coordination process into a durable cooperation claim.
