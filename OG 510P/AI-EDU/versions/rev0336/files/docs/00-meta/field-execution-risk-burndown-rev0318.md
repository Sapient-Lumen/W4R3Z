# rev0318 field execution risk burndown

## Risk posture

`FT-0181` remains live because the archive still lacks a real owner-reviewed `SRC2+` packet. The
parallel mission risk is that the teacher/tutor micro-pilot remains planned but not run. Rev0318
reduces the latter risk by turning the micro-pilot packet into one command while preserving the
no-evidence boundary.

## Burned down in rev0318

| Risk | Previous state | rev0318 change | Remaining boundary |
|---|---|---|---|
| micro-pilot assembly burden | owner plan, session log, final readout, prompt, and checklist were scattered | `make micro-pilot-pack` prepares a complete scratch-only packet | a real owner must still run the cycle |
| raw/protected-data drift | operator could overfill packet fields from local examples | utility refuses obvious identifier/protected/raw-data argument terms and writes only scratch/external output | human still controls what is entered during the actual run |
| execution invisibility | README named the run card but not a concrete command | startup docs now show owner-field and micro-pilot commands side by side | human send and human run remain outside archive |
| control-growth relapse | easiest move could have been another validator | new tool is utility-only; no schema, validator, or branch was added | future uncovered real failures may still justify new controls |

## Next field actions

1. Run or regenerate `make owner-field-work`.
2. Use [`../30-operations/ft0181-owner-contact-send-pack.md`](../30-operations/ft0181-owner-contact-send-pack.md)
   to send the bounded owner request or record a route block.
3. Prepare one teacher/tutor cycle with `make micro-pilot-pack`.
4. Run the cycle only after a real owner completes the owner plan and chooses the no-AI transfer or
   explanation check.
5. When real owner material returns, run `make owner-field-next CSV=/path/to/real-owner-return.csv`
   and execute only the emitted command.

## Claim boundary

Rev0318 lowers execution friction. It does not contact an owner, run the micro-pilot, accept evidence,
prove learning or workload effects, authorize service use, upgrade public language, or close
`FT-0181`.
