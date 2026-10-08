# Command step page: seat, path, process, and precondition proof interface spec

## Purpose

Some external recipes collapse into literal commands or file operations.
That deserves its own page family because the operator needs more than a pasted snippet.

This document defines the interface contract for one first-class **command step** page.

## Core rule

If the next action is a literal command, script, config-file write, or hidden-file operation, the product must show:

1. the command identity
2. the exact target tuple
3. what must already be true before execution
4. what immediate witness proves the command ran
5. what hazards remain even if the command ran successfully
6. what return-proof page must be read next

The product must not present copied commands as self-authenticating.

## Public object

### Command step

Suggested fields:

- `command_step_id`
- `external_recipe_ref`
- `command_family` (`shell-command`, `service-command`, `config-write`, `file-create`, `file-delete`, `file-rename`, `browser-address-action`, `script-run`)
- `literal_command_or_operation`
- `target_tuple_ref`
- `requires_runtime_stopped` bool
- `requires_admin_or_shell_access` bool
- `idempotence_class` (`idempotent`, `mostly-idempotent`, `non-idempotent`, `unknown`)
- `expected_execution_witness`
- `execution_hazards[]`
- `expected_local_side_effects[]`
- `next_postcondition_ref`
- `state` (`draft`, `reviewed`, `armed`, `executed`, `contradicted`, `aborted`)

## Fixed page order

1. **Command identity**
   - what kind of step this is
   - literal command or precise operation
   - why this command exists in the plan

2. **Target tuple**
   - seat
   - runtime
   - process identity
   - path / store / browser cache target
   - hidden-state family if relevant

3. **Preconditions**
   - what must already be closed, stopped, mounted, or visible
   - what privilege is required
   - what evidence proves those preconditions are true

4. **Immediate witness and hazards**
   - what counts as command execution witness
   - what counts as contradiction
   - what harms could still occur even if the witness is positive

5. **Return and receipt**
   - link to required postcondition-verification page
   - durable execution receipt
   - note whether step should be repeated or not

## Example command families this page must handle

- `touch`-style freshness repair
- `iperf3` measurement commands
- creating `debug.txt` in storage
- putting `sync.conf` in the active storage path
- deleting `settings.dat`
- deleting or rebuilding hidden `.sync` state

## Dense row contract

A dense command-step row should preserve these labels in this order:

- `Step`
- `Target`
- `Must already be true`
- `Witness`
- `Hazards`
- `Read next`

## Anti-goals

- no bare pasted commands without scope
- no command rows that omit stop/restart preconditions
- no `ran successfully` treated as the same thing as `problem solved`
- no silent repetition of non-idempotent steps

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following before pressing run:

- what exact command or file operation this is
- what seat / runtime / path it addresses
- what had to be stopped first
- what makes the step non-idempotent or risky
- what evidence proves execution
- what must still be reread afterward
