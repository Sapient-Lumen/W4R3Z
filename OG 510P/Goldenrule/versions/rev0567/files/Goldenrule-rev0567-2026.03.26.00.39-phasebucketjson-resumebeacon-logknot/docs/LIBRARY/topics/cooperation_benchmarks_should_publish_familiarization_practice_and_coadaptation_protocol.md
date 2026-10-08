# Cooperation benchmarks should publish familiarization, practice, and co-adaptation protocol

Two cooperation benchmark lanes can use the same task, counterpart class, visibility regime, and score metric while still measure materially different collaboration problems.
A cold-start lane, a lane with tutorial rounds, and a lane with repeated exposure plus partner-specific learning are not interchangeable.
Two recent sources make the compact archive rule clear:

- `RS-GR-069` studies a hybrid human/bot partner-selection game and shows that humans learn about partner types over repeated interaction; disclosing bot identity reduced bots' initial selection chances but then let them gradually outcompete humans by facilitating human learning about each partner type.
- `RS-GR-070` introduces Moving Out and makes adaptation itself an explicit benchmark target, evaluating whether agents can adapt to diverse human behaviors and generalize to unseen physical attributes rather than only succeeding in one fixed collaboration regime.

## Minimum contract

Whenever a cooperation benchmark includes any tutorial, warm-up, repeated exposure, partner-specific adaptation, or online update opportunity, publish:

1. whether the measured lane is **cold-start, familiarized, or explicitly co-adaptive**;
2. how many **tutorial / practice / burn-in rounds** occur before scored evaluation, and whether those rounds use the same task, partner type, or payoff structure;
3. what **feedback** each side receives during familiarization and measured play, including whether outcomes, partner identity, trust cues, or hidden-state summaries are revealed;
4. whether the same human, model, or partner type is encountered repeatedly so that **partner-specific learning** can accumulate;
5. whether the model or scaffold is allowed any **online updating, memory carryover, prompt editing, or policy retuning** between rounds;
6. and whether headline results pool across cold-start and acclimated lanes or report them separately.

## Implementor consequence

Do not compare or pool cooperation results across lanes unless their adaptation opportunity is actually aligned.
A system can look more cooperative simply because people had time to learn its conventions, because the model got a longer acclimation window to the human, or because practice rounds quietly converted a zero-shot test into a partly trained interaction.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: warm-up / practice count, feedback during acclimation, repeat-exposure rule, and whether the reported score is cold-start or post-adaptation.
That prevents future sessions from laundering familiarization or co-adaptation into a policy-quality claim.
