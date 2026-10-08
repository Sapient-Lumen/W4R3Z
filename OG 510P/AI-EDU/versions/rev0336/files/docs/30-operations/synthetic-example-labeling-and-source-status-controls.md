# Synthetic example labeling and source-status controls

AI-EDU now contains realistic service records, import maps, negative
fixtures, render tests, and handoff records. These examples are useful,
but they can become dangerous if a maintainer later treats them as field
evidence.

This surface makes the source status of example JSON explicit.

## Source truth classes

| Class | Meaning | Evidence use |
|---|---|---|
| `SRC0` | empty, placeholder, negative, or no-real-data artifact | never evidence |
| `SRC1` | realistic synthetic example or template | design rehearsal only |
| `SRC2` | local pilot export or owner-reviewed local record | local evidence only |
| `SRC3` | multi-site or independently reviewed record set | stronger but still scoped |
| `SRC4` | audited external dataset or standard-bearing evidence | strongest ordinary import |
| `SRCX` | contaminated, ambiguous, or unusable source | reject |

A service record example may include plausible fields and still remain
`SRC1`. Plausibility is not provenance.

## Required declaration

Every JSON file under `examples/`, except the declaration file itself,
should be listed in a synthetic-example declaration with:

- its path;
- source truth class;
- example role;
- allowed use;
- prohibited claims;
- whether it may support `FT-0181` closure.

The current declaration intentionally marks all existing examples as
non-closing. Some are realistic. None are real pilot imports.

## Promotion rule

Do not relabel an example from `SRC0` or `SRC1` to `SRC2+` by editing the
declaration alone. Promotion requires:

1. source owner identity and date;
2. source data dictionary;
3. import map;
4. acceptance/calibration packet;
5. public-summary render checks;
6. lifecycle decision;
7. decision-delta log;
8. closeout-board minutes.

The promoted record should usually be a new record, not a mutation of the
example. Keep the synthetic original so later reviewers can see what the
archive believed before real data arrived.

## Public-summary implication

If a public summary cites an example, it must say that the example is a
sample or template. If a public summary cites a real pilot record, it must
name the evidence grade, expiry date, sector adapter, redaction profile,
and claims it does not prove.

## Stop rules

Reject the release if:

- an example is unlisted;
- a declaration says an example can close `FT-0181` without `SRC2+`;
- a public summary relies on an `SRC0` or `SRC1` artifact as effectiveness
  evidence;
- a negative fixture is used as a mitigation record rather than a failing
  test case;
- a realistic service record is renamed or copied into a real-import path
  without provenance records.
