# Record schema notes

`RECORD-SCHEMA.json` is the machine-readable intake contract for future records. It requires source, axes, content, provenance, safety, and review state.

The most important design choice is separation:

- observation is not interpretation;
- contributor interpretation is not editor interpretation;
- a single record is not a universal claim;
- a seed cue is not a record;
- a public-source citation is not consent for private details;
- medical vocabulary is not medical advice.

Future schema work should test whether ordinary users can still read records without feeling trapped inside metadata.
