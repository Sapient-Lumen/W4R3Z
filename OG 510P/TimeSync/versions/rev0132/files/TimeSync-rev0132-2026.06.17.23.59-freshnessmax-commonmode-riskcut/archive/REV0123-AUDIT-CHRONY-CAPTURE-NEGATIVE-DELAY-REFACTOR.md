# rev0123 focused refactor audit — chrony capture and negative delay

## Refactor target

`tools/chrony_adapter.py` had two responsibilities blurred together: command collection and replay evaluation. rev0123 splits live command capture into `tools/chrony_capture.py`, leaving the adapter to consume either raw replay text or validated capture replay inputs.

## Why this reduces waste

The project has repeatedly grown by adding registries around uncertainty. This refactor adds only the executable boundary needed for the next live-host proof:

- command roles are fixed and checked;
- collection timing is bracketed;
- monotonic timing is preserved for local ordering sanity;
- command failures are kept diagnosable but not evaluable;
- unsupported conditions are attached to capture context instead of becoming new TimeState fields.

## Safety correction

The interval formula now refuses to let negative root delay reduce uncertainty. This prevents a path where an unusual upstream/peer condition could make the emitted TimeState interval narrower than a conservative consumer should accept.

## Tests added

- capture self-test for good fixture extraction;
- capture self-test for inverted monotonic command interval;
- capture self-test for command outside the collector monotonic bracket;
- capture self-test for failed tracking command rejected as replay evidence;
- chrony golden test for negative root delay;
- semantic vector for the generated conservative negative-root-delay assessed state.

## Still intentionally not done

- no generic capture schema family;
- no NTS verifier placeholder;
- no profile threshold expansion;
- no source-diversity independence inference beyond local chrony source-state summaries.
