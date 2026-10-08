# OCF portable replay command patch (rev0832)

Historical benchmark commands are retained unchanged, but every `/opt/pyvenv/bin/python3` command now has an archive-root portable replay command beside it.

- Status: `portable_replay_fields_present`
- Historical private-interpreter commands: **25**
- Portable commands present: **25**
- Portable commands with missing checked paths: **0**

## Commands by file

| File | Commands |
| --- | ---: |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | 6 |
| `sources/ocf_llm/examples/resolver_bench_v2.json` | 8 |
| `sources/ocf_llm/examples/resolver_bench_v3.json` | 7 |
| `sources/ocf_llm/examples/runtime_gate_bench_v1.json` | 4 |

## Sample mappings

| File | Row | Portable command |
| --- | --- | --- |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | `sabom_mcp_episode_abom.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/sabom_mcp_episode_abom.json` |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | `sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm_profile_abom.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/sic_zk_toy_privacy_vco_vte_vtpw2_fresh_rtm_profile_abom.json` |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | `cpc_profile_receipt_pbc_abom.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/cpc_profile_receipt_pbc_abom.json` |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | `cpc_profile_receipt_pbc_abom_policy_mismatch.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/cpc_profile_receipt_pbc_abom_policy_mismatch.json` |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | `cpc_profile_receipt_pbc_abom_stale_policy.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/cpc_profile_receipt_pbc_abom_stale_policy.json` |
| `sources/ocf_llm/examples/resolver_bench_v1.json` | `lean_passk_abom.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/lean_passk_abom.json` |
| `sources/ocf_llm/examples/resolver_bench_v2.json` | `example_abom_v1.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/example_abom_v1.json` |
| `sources/ocf_llm/examples/resolver_bench_v2.json` | `agentic_rag_abom.json` | `python3 sources/ocf_llm/tools/ocf_resolver.py sources/ocf_llm/examples/agentic_rag_abom.json` |

## Interpretation

This is not a re-benchmark. The original timing command remains as measurement provenance. The new field is a consumer replay affordance that avoids the private virtualenv path and resolves checked archive paths from the archive root.
