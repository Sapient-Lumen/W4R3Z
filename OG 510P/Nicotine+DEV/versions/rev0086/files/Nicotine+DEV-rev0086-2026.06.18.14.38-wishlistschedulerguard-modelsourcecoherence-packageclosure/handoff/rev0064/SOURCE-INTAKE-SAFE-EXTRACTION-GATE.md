# rev0064 source-intake / safe-extraction gate

Use this handoff note when checking whether the cube actually used the uploaded source bundle.

## Archived source bundle

```text
source bundle: Nicotine-source(1).zip
SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
ZIP entries scanned: 3551
source-lane file rows: 2139
source-lane total bytes: 46605550
```

## Lanes

```text
github-tag-3.3.10: files=678 bytes=14577303 manifest=12bf750459c12fff6770598b5dc11ab7c8e3e77b6995a74bad6a94a1cb37d2cd head=caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
github-branch-3.3.x: files=684 bytes=14625090 manifest=64f696fc32bcb45213b5f40491c546cf9a9a5844f2fd854001747d78f713df3d head=98089ac233aa57786e8dbdc48123f6ac1c4767d8
github-branch-master: files=777 bytes=17403157 manifest=eef3d4dae0c236813310ef79c886d8740127d175f9b058a6015c185a1c6289aa head=f4e17d59783dbc48ea31d2e899a681e2dd1ed500
```

## Reviewer command

```bash
python tools/probe_rev0064_source_intake_safety.py --source-zip /path/to/Nicotine-source.zip
```

Expected result:

```text
status: pass
entry_safety_failures: 0
safe_extraction_roundtrip_pass: 3
critical_file_crosscheck_pass: 15
negative_controls_pass: 4
```

## Boundary

This proves source-bundle intake and safe extraction for the archived source bundle. It does not replace a fresh current checkout/tarball before live-current filing.
