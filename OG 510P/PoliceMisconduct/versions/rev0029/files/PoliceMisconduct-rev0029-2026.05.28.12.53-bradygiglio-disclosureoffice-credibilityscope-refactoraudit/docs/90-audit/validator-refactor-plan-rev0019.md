# Validator refactor plan — rev0019

`make lint` remains the single command. The validator is intentionally still monolithic in rev0019 because splitting it while adding a new source-family atlas would create two sources of risk.

Future refactor should split checks by office while preserving one command:

- release/reentry validation;
- source graph and preservation validation;
- lifecycle and claim-workbench validation;
- source-family atlas validation;
- root/refactor validation;
- schema registry validation.

The most important technical correction is to stop validating older surfaces only when `revision == revNNNN`. Rev0019 changes the rev0018 block so the workbench remains validated in later revisions.
