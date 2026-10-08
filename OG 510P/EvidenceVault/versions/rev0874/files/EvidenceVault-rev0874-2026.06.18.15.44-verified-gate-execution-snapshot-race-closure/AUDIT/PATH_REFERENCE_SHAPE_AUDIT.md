# Path reference shape audit

This audit catches path/reference strings that are no longer cloud absolute paths but still look structurally unsafe for replay or interpretation.

- Status: `no_known_path_shape_anomalies_found`
- UTF-8 text files scanned: **4227**
- Files with shape anomalies: **0**
- Shape anomalies: **0**

## Finding counts

| Finding kind | Count |
| --- | ---: |
| none | 0 |

## By family/area

| Family/area | Findings |
| --- | ---: |

## Files with findings

| Path | Findings | Examples |
| --- | ---: | --- |

## Interpretation

Serialized-object path findings indicate producer bugs or failed resolver coercions. Rev0832 regenerates the known SIC/RTM trace that carried this issue.

Historical `/opt/pyvenv` benchmark commands are not treated as active shape anomalies when the same record carries rev0832 `portable_cmd` replay fields; see `AUDIT/OCF_PORTABLE_REPLAY_COMMANDS_REV0832.*`.
