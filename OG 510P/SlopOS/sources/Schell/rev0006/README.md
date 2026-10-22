# Schell living archive

**North star:** see [`docs/00-meta/charter.md`](docs/00-meta/charter.md).

Revision notes: [`CHANGELOG.md`](CHANGELOG.md).

Schell is a **living archive** for designing a shell from scratch in **Rust** that is worthy of SlopOS: explicit about authority, careful about side effects, durable across sessions, and disciplined enough to serve both interactive humans and automation.

This revision keeps the archive in **research mode** while making three bounded advances:

- it advances more questions through explicit proof surfaces rather than abstract intent,
- it adds a transcript-truth layer so semantic terminal ambition stays portable, and
- it tightens repo hygiene around head-bundle truth and question-state discipline.

## How to navigate

1. Start-here briefing: [`START_HERE.md`](START_HERE.md)
2. Charter + trajectory + move registry: [`docs/00-meta/`](docs/00-meta/)
3. Question machine + advancement pass: [`docs/00-meta/question-machine.md`](docs/00-meta/question-machine.md) and [`docs/00-meta/question-advancement-pass-2026-03-20.md`](docs/00-meta/question-advancement-pass-2026-03-20.md)
4. Repo hygiene + process: [`docs/00-meta/repo-hygiene-and-rust-process.md`](docs/00-meta/repo-hygiene-and-rust-process.md)
5. SlopOS datacube evaluation: [`docs/00-meta/slopos-datacube-evaluation.md`](docs/00-meta/slopos-datacube-evaluation.md), [`docs/00-meta/slopos-datacube-evaluation-rust-pass.md`](docs/00-meta/slopos-datacube-evaluation-rust-pass.md), [`docs/00-meta/slopos-datacube-evaluation-pass-ii.md`](docs/00-meta/slopos-datacube-evaluation-pass-ii.md), and [`docs/00-meta/slopos-datacube-evaluation-pass-iii.md`](docs/00-meta/slopos-datacube-evaluation-pass-iii.md)
6. Research synthesis: [`docs/00-meta/research-synthesis-2026-03-20.md`](docs/00-meta/research-synthesis-2026-03-20.md), [`docs/00-meta/research-synthesis-2026-03-20-rust-pass.md`](docs/00-meta/research-synthesis-2026-03-20-rust-pass.md), [`docs/00-meta/research-synthesis-2026-03-20-ratchet-pass.md`](docs/00-meta/research-synthesis-2026-03-20-ratchet-pass.md), and [`docs/00-meta/research-synthesis-2026-03-20-pass-iii.md`](docs/00-meta/research-synthesis-2026-03-20-pass-iii.md)
7. Question machine + advancement passes: [`docs/00-meta/question-machine.md`](docs/00-meta/question-machine.md), [`docs/00-meta/question-advancement-pass-2026-03-20.md`](docs/00-meta/question-advancement-pass-2026-03-20.md), and [`docs/00-meta/question-advancement-pass-iii-2026-03-20.md`](docs/00-meta/question-advancement-pass-iii-2026-03-20.md)
8. Question registry: [`QUESTION-REGISTRY.json`](QUESTION-REGISTRY.json)
9. Portable core + platform profile: [`docs/60-platform/`](docs/60-platform/)
10. Terminal surfaces + protocol sketch: [`docs/80-terminal/`](docs/80-terminal/)
11. Decisions and proposals: [`adrs/`](adrs/) and [`rfcs/`](rfcs/)

## Design stance

Schell is **not** just a nicer command prompt. The working thesis is that a modern shell should:

- separate execution IR, review/authority, interactive language sugar, and terminal presentation,
- make side effects legible before they happen,
- preserve session lineage so command history can become evidence instead of gossip,
- support both text streams and structured control/diagnostic lanes,
- keep interactive ergonomics without smuggling ambient authority,
- keep the datacube's unresolved questions first-class until they earn answers,
- and stay portable enough to boot on ordinary Unix-like systems before chasing exotic runtimes.

## One command

```bash
make lint
```
