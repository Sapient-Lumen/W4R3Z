# Cooperation benchmark human lanes should publish counterpart disclosure and belief protocol

Human-lane cooperation results are not only about the policy.
They also depend on what people think the counterpart is.
Recent work now supports a compact archive rule:

- `RS-GR-051` shows that people align differently with LLMs than with humans in a cooperative word game, and that users' beliefs about the partner further modulate those effects.
- `RS-GR-052` shows that people make different strategic choices against LLM opponents than against humans, partly because they expect more rationality and even more cooperation from the LLM side.

## Minimum contract

Whenever a benchmark lane includes real humans, publish:

1. whether participants were told the counterpart was **human**, **AI**, **mixed**, or **unspecified**;
2. when that disclosure happened (**before**, **during**, or **after** interaction);
3. whether any **deception / blinding** was used;
4. whether participant **beliefs** about counterpart identity or capability were elicited;
5. and the rule for comparing lanes when disclosure conditions differ.

## Implementor consequence

Do not compare or pool human-lane cooperation scores across studies if the counterpart-disclosure and belief protocol differs.
A policy can look better or worse partly because humans approach AI-labelled partners differently from human-labelled ones.

## Archive consequence

Keep the retained object tiny.
One benchmark-card row is enough: disclosure condition, belief-elicitation status, and any blinding/deception note.
That prevents future sessions from laundering a participant-belief effect into a policy-generalization claim.
