from __future__ import annotations

from pathlib import Path

import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)

    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))

    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_csv_and_foreach_roundtrip(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {
                        "type": "SetVar",
                        "name": "rows",
                        "value": [
                            {"id": "1", "name": "Ada"},
                            {"id": "2", "name": "Linus"},
                        ],
                    },
                    {"type": "WriteCsv", "path": "data/users.csv", "rows_expr": "rows"},
                    {"type": "ReadCsv", "path": "data/users.csv", "out_var": "rows2", "out_row_count": "n"},
                    {
                        "type": "ForEach",
                        "items_expr": "rows2",
                        "item_var": "row",
                        "index_var": "i",
                        "steps": [
                            {"type": "AppendFile", "path": "data/names.txt", "text": "${i}:${row.name}\n"},
                        ],
                    },
                    {"type": "ReadFile", "path": "data/names.txt", "out_var": "names"},
                ],
            }
        },
    )

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.vars["n"] == 2
    assert res.vars["rows2"][0]["name"] == "Ada"
    assert res.vars["names"] == "0:Ada\n1:Linus\n"


def test_json_and_text_steps(tmp_path: Path):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "SetVar", "name": "payload", "value": {"users": [" Ada ", "Linus  "]}},
                    {"type": "WriteJson", "path": "data/users.json", "value_expr": "payload"},
                    {"type": "ReadJson", "path": "data/users.json", "out_var": "payload2"},
                    {"type": "SetVar", "name": "raw", "value": "  alpha, beta ,gamma  "},
                    {"type": "TrimText", "text": "${raw}", "out_var": "trimmed"},
                    {"type": "SplitText", "text": "${trimmed}", "sep": ",", "out_var": "parts"},
                    {"type": "ForEach", "items_expr": "parts", "item_var": "part", "index_var": None, "steps": [
                        {"type": "TrimText", "text": "${part}", "out_var": "part_clean"},
                        {"type": "AppendFile", "path": "data/parts.txt", "text": "${part_clean}\n"},
                    ]},
                    {"type": "ReadFile", "path": "data/parts.txt", "out_var": "parts_txt"},
                    {"type": "RegexReplace", "text": "${parts_txt}", "pattern": "a", "replacement": "A", "count": 1, "out_var": "patched"},
                    {"type": "SetVar", "name": "join_parts", "value": ["x", "y", "z"]},
                    {"type": "JoinText", "items_expr": "join_parts", "sep": "-", "out_var": "joined"},
                ],
            }
        },
    )

    res = Runner(load_project(proj)).run("m")
    assert res.ok
    assert res.vars["payload2"]["users"][1] == "Linus  "
    assert res.vars["parts_txt"] == "alpha\nbeta\ngamma\n"
    assert res.vars["patched"] == "Alpha\nbeta\ngamma\n"
    assert res.vars["joined"] == "x-y-z"
