# AI-EDU — rev0336

## Help a teacher choose the next move

This checkpoint turns AI-EDU's educational purpose into a small, inspectable teaching experiment: after a learner has tried, can an AI help a teacher choose a better question, misconception check or hint without taking over the learner's thinking? The practical object is a local preparation-and-review workflow for one selected concept. It supplies the materials around a teaching cycle, while leaving the instructional judgment with the educator and the learning with the learner.

Its distinctive addition is a way to continue thoughtfully. A decision to try again points to the previous local result, but the next cycle starts with a fresh plan, a specified change and a separate transfer check. Continuity means remembering why another attempt is worth making, not treating accumulated paperwork as accumulated proof.

For the project's classroom, assessment and institutional arguments, start with the [AI-EDU guide](../../README.md). This entrance follows the later teacher-coach workflow and explains what rev0336 changes.

## The teaching problem comes before the packet

The [feasibility cycle](files/docs/30-operations/teacher-tutor-augmentation-micro-pilot.md) begins with an educator's actual problem, not a preselected demonstration of what the tool can do. The educator chooses one concept, an ordinary baseline task and a separate no-AI transfer or explanation check before coach use. They also settle participation, an ordinary non-AI fallback, review responsibilities and the time they can reasonably spend.

The optional [one-step equality kit](files/docs/30-operations/teacher-tutor-micro-pilot-measure-card-equality-one-step.md) gives this an instructional shape. A learner may solve `x + 5 = 12` procedurally while treating the equals sign as an answer cue, changing only one side or being unable to explain why the inverse operation preserves equality. The coach offers the teacher three possibilities: a probing question, a misconception check and a smallest-useful hint. The teacher chooses, edits or rejects each suggestion before it reaches the learner. A changed equation and independent explanation then ask whether the learner can use the idea beyond the familiar item.

This is not another solver wrapped in assessment language. The [generated prompt](files/tools/prepare_teacher_tutor_micro_pilot_pack.py) asks for teacher-facing moves after an attempted step, using a de-identified summary rather than raw learner work. It excludes final-answer delivery, grading, classification and record writing. The prompt is a card for the educator's chosen AI workflow; the packet generator does not itself provide a model service. Equality is an optional worked example, not the archive's decision about what a particular class needs.

## Four different achievements, not one success flag

The [readiness gate](files/docs/30-operations/teacher-tutor-micro-pilot-readiness-gate.md) distinguishes stages that a single “ready” label could obscure:

1. **Preparation:** generated cards, blank logs and a plan make work possible to organize. They do not say that a teacher has completed the plan or taught a lesson.
2. **Cycle entry:** a completed plan and coherent run definition can support one locally approved cycle while the post-cycle rows remain blank. This avoids requiring invented observations merely to start.
3. **Review:** after baseline, coach-use and transfer rows have been recorded, a coherent packet can be ready for human review. Software checks of completeness and chronology are not the review itself.
4. **Local result:** after that review, a recorder can summarize the local observations and bounded decision. A structured receipt still does not establish that the intervention caused learning.

A synthetic rehearsal has its own status and must be discarded or regenerated before real work. Partial, incoherent post-cycle entries return to repair rather than silently falling back to entry readiness. The [router](files/tools/decide_teacher_tutor_micro_pilot_next_action.py) translates these states into the next local action, so the operator need not rediscover the sequence by reading the whole governance archive.

The [run card](files/docs/30-operations/teacher-tutor-micro-pilot-run-card.md) keeps the educational stakes visible throughout: stop for answer leakage, loss of human review, inaccessible participation or fallback, unacceptable burden, intervention drift or obvious transfer harm. Review includes preparation and correction time, not just the seconds saved generating a suggestion. Learner voice and protected local access review can support stopping or redesign even when a completed task looks successful.

## Keep the reviewed intervention identifiable

The [packet generator](files/tools/prepare_teacher_tutor_micro_pilot_pack.py) records hashes for the generated discovery card, coach prompt, checklist, measure card and run sheet. Readiness compares those files with the manifest and the prompt hash in the owner plan. A different run definition calls for regeneration, not an unnoticed edit midway through the cycle.

The [owner-review recorder](files/tools/record_teacher_tutor_micro_pilot_owner_review.py) records hashes across the reviewed run definition and aggregate packet. The [result recorder](files/tools/record_teacher_tutor_micro_pilot_result.py) checks the recorded hashes and event dates before producing its receipt. Recorded phase dates cannot run backwards from baseline through coach use to transfer; review and result dates cannot precede the observations they describe. These checks answer “which materials and recorded sequence is this decision about?” They do not answer “was this good teaching?” or independently verify that the reported events occurred.

The result recorder can calculate a transfer-minus-baseline rate difference when the relevant rates are displayed. That arithmetic is useful as a description of this packet, not as a causal estimate. The cycle is deliberately a feasibility inquiry: can an educator use this arrangement, find a useful move and retain acceptable workload, access and learner independence? A later effectiveness inquiry would need its own evaluation design.

## Continue from a reason, not a generic repeat command

The [changelog](files/CHANGELOG.md) shows how the current path developed. Rev0326 made the local instructional problem primary; rev0327 separated entry from post-cycle readiness; rev0329 removed a post-cycle attestation obstacle to honest entry. Rev0335 required an educator's next constraint, one required change and a fresh-packet acknowledgment before a non-retire review decision. Rev0336 adds the link from a completed repeat/continue result to the next packet.

The implemented order matters. **Before review**, the owner decision memo records the intended next constraint and change. **After a result**, a `repeat-narrower` or `continue-bounded` decision can be used as the source for a fresh packet. The generator checks the source result's decision and non-evidence boundaries, then records its path and SHA-256 with limited provenance fields. The new concept, setting, window and transfer check are supplied anew by the human operator. Previous observations and the old memo's seed text are not copied into the new packet.

The [source-link check](files/tools/score_teacher_tutor_micro_pilot_readiness.py) requires the prior result to remain locally available at the recorded path with matching bytes. This is a concrete continuity dependency: carrying only the new packet while losing its source result leaves the linked packet not ready. The link makes the predecessor identifiable, not infallible, and does not pool cycles or infer an improving trend.

The alternatives remain real. `retire` stops this local line; `repeat-narrower` changes its scope; `continue-bounded` allows another bounded attempt with a refreshed plan; `escalate-to-pilot-review` leaves the micro-cycle lane for a separately designed review route. A repeat/continue packet is not the implementation of that escalation route.

## What can travel, and what remains local

The workflow prohibits putting raw learner work, names, protected facts and similar educational records into the release archive. Its result recorder withholds a session row's attempt and success counts and rate when the attempt count falls below the educator's threshold, which must be at least three. It also applies numeric/small-cell-sensitive redaction rules to the final readout. This is a specific minimization mechanism, not a guarantee of anonymity: a row above the attempt threshold can still display a small success or incident count.

The distinction between a preparation receipt, an observed local outcome and a defensible learning claim is the work's central discipline. The supplied checkpoint reports no real completed cycle or demonstrated benefit. Its concrete contribution is the packet-building, review and continuation machinery, together with an educational proposal that can be examined before anyone mistakes that machinery for an outcome.

## Read the historical work

- [Original introduction](files/README.md) and [operator entrance](files/START_HERE.md)
- [Feasibility cycle](files/docs/30-operations/teacher-tutor-augmentation-micro-pilot.md) and [equality worked kit](files/docs/30-operations/teacher-tutor-micro-pilot-measure-card-equality-one-step.md)
- [Readiness stages](files/docs/30-operations/teacher-tutor-micro-pilot-readiness-gate.md), [owner review](files/docs/30-operations/teacher-tutor-micro-pilot-owner-review-stop.md) and [local result](files/docs/30-operations/teacher-tutor-micro-pilot-result-recorder.md)
- [Development history](files/CHANGELOG.md), [archive index](files/ARCHIVE_INDEX.md), [release manifest](files/RELEASE-MANIFEST.json) and [charter](files/docs/00-meta/charter.md)

Reading guide by Lumen. Original archive and member contents are unchanged.

## Preservation and integrity

ZIP members passed CRC checks and were copied with exact content hashes. The available listed-file or tree-digest checks recorded in the integrity review matched their supplied contents. These checks establish preservation, not correctness of the archive’s claims, software behavior, current external sources or deployment readiness.

- [Original ZIP](../../originals/AI-EDU-rev0336-2026.06.18.17.42-source-result-hashlink-freshpacket-bridge.zip)
- ZIP SHA-256: `0a3f06f7e3202eb59dc09949a5dd29f483844473bfdda88e9125a7ca94fad809`
- Extracted file count: 840
- [Exact per-file inventory](INVENTORY.json)
- [Integrity review](INTEGRITY.json)

Member paths and wrapper directories are retained. The supplied code was not executed. Historical instructions, proposed contacts and open work do not authorize new action. Existing rights and license notices remain applicable; no new blanket license is granted.

