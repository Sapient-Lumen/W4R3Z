from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TURN_ROLE_STEMS = {
    "lacuna-planner",
    "lacuna-narrator",
    "lacuna-proposal-builder",
    "lacuna-verifier",
}
CHECKPOINT_ROLE_STEMS = {
    "lacuna-retcon-generator",
    "lacuna-retcon-judge",
    "lacuna-retcon-compressor",
    "lacuna-retcon-verifier",
}
CONTINUATION_ROLE_STEMS = {"lacuna-fresh-narrator"}
ROLE_STEMS = TURN_ROLE_STEMS | CHECKPOINT_ROLE_STEMS | CONTINUATION_ROLE_STEMS


def expected_card_schema(role: str) -> str:
    if role in CONTINUATION_ROLE_STEMS:
        return "lacuna.checkpoint-continuation-dispatch.v2"
    return (
        "lacuna.checkpoint-task-card.v1"
        if role in CHECKPOINT_ROLE_STEMS
        else "lacuna.turn-task-card.v1"
    )


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} is missing YAML frontmatter")
    try:
        raw, body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise AssertionError(f"{path} has unterminated YAML frontmatter") from exc
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise AssertionError(f"unsupported frontmatter line in {path}: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields, body


class ProviderConfigTests(unittest.TestCase):
    def test_codex_custom_agents_are_parseable_read_only_and_name_mapped(self) -> None:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text())
        self.assertEqual(config["agents"]["max_threads"], 4)
        self.assertEqual(config["agents"]["max_depth"], 1)

        files = sorted((ROOT / ".codex" / "agents").glob("*.toml"))
        self.assertEqual({path.stem for path in files}, ROLE_STEMS)
        names = set()
        for path in files:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            names.add(data["name"])
            self.assertEqual(data["sandbox_mode"], "read-only")
            self.assertTrue(data["description"])
            instructions = data["developer_instructions"]
            self.assertIn("Do not", instructions)
            self.assertNotIn("turn commit", instructions.lower())
            self.assertIn(expected_card_schema(path.stem), instructions)
            self.assertIn(
                "return_contract.template"
                if path.stem in CONTINUATION_ROLE_STEMS
                else "output_contract.template",
                instructions,
            )
            self.assertIn("exactly one JSON object", instructions)
        self.assertEqual(names, {stem.replace("-", "_") for stem in ROLE_STEMS})

    def test_claude_subagents_have_empty_tool_allowlists(self) -> None:
        files = sorted((ROOT / ".claude" / "agents").glob("*.md"))
        self.assertEqual({path.stem for path in files}, ROLE_STEMS)
        for path in files:
            fields, body = frontmatter(path)
            self.assertEqual(fields["name"], path.stem)
            self.assertEqual(fields["tools"], "[]")
            self.assertGreaterEqual(int(fields["maxTurns"]), 1)
            self.assertTrue(fields["description"])
            self.assertIn("commit", body.lower())
            self.assertIn("not", body.lower())
            self.assertIn(expected_card_schema(path.stem), body)
            self.assertIn(
                "return_contract.template"
                if path.stem in CONTINUATION_ROLE_STEMS
                else "output_contract.template",
                body,
            )
            self.assertIn("exactly one JSON object", body)

    def test_gemini_subagents_have_empty_tool_allowlists(self) -> None:
        files = sorted((ROOT / ".gemini" / "agents").glob("*.md"))
        self.assertEqual({path.stem for path in files}, ROLE_STEMS)
        for path in files:
            fields, body = frontmatter(path)
            self.assertEqual(fields["name"], path.stem)
            self.assertEqual(fields["kind"], "local")
            self.assertEqual(fields["tools"], "[]")
            self.assertGreaterEqual(int(fields["max_turns"]), 1)
            self.assertTrue(fields["description"])
            self.assertIn("commit", body.lower())
            self.assertIn("not", body.lower())
            self.assertIn(expected_card_schema(path.stem), body)
            self.assertIn(
                "return_contract.template"
                if path.stem in CONTINUATION_ROLE_STEMS
                else "output_contract.template",
                body,
            )
            self.assertIn("exactly one JSON object", body)

    def test_root_instruction_adapters_route_play_and_map_provider_names(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Intent router", agents)
        self.assertIn("Will you DM?", agents)
        self.assertIn("lacuna_planner", agents)
        self.assertIn("lacuna-planner", agents)
        self.assertIn("top-level `narration` field", agents)
        self.assertIn("./lacuna turn run begin", agents)
        self.assertIn("RUN_PATH/NEXT.md", agents)
        self.assertIn("./lacuna turn run accept", agents)
        self.assertIn("./lacuna turn run commit", agents)
        self.assertIn("lacuna-retcon-generator", agents)
        self.assertIn("./lacuna checkpoint run begin", agents)
        self.assertIn("checkpoint run dispatch", agents)
        self.assertIn("checkpoint run accept", agents)
        self.assertIn("checkpoint run commit", agents)
        self.assertIn("only the parent", agents.lower())
        self.assertNotIn("./lacuna turn plan", agents)

        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        gemini = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        self.assertTrue(claude.startswith("@AGENTS.md\n"))
        self.assertTrue(gemini.startswith("@./AGENTS.md\n"))
        self.assertIn("parent owns", claude.lower())
        self.assertIn("parent owns", gemini.lower())

    def test_chatgpt_adapter_is_capability_honest_and_packet_exact(self) -> None:
        instructions = (
            ROOT / "integrations" / "chatgpt" / "PROJECT_INSTRUCTIONS.md"
        ).read_text(encoding="utf-8")
        self.assertIn("not yet committed to a Lacuna cube", instructions)
        self.assertIn("Return exactly one `lacuna.turn-proposal.v2` object", instructions)
        self.assertIn("Empty `operations`", instructions)
        self.assertIn("passing `lacuna.turn-receipt.v3`", instructions)
        self.assertIn("human or connected bridge", instructions)
        self.assertIn("NEXT.md", instructions)
        self.assertIn("Do not read an invented nested `receipt.narration` path", instructions)
        self.assertIn("lacuna.checkpoint-agent-dispatch.v1", instructions)
        self.assertIn("generator → judge → compressor → verifier", instructions)
        self.assertIn("parent", instructions.lower())
        self.assertIn("checkpoint run begin", instructions)
        self.assertIn("checkpoint run dispatch", instructions)
        self.assertIn("checkpoint run accept", instructions)
        self.assertIn("checkpoint run commit", instructions)

    def test_provider_guide_records_primary_source_urls_and_drift_boundary(self) -> None:
        guide = (ROOT / "docs" / "operators" / "PROVIDER_CONFIGS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("https://developers.openai.com/codex/subagents", guide)
        self.assertIn("https://code.claude.com/docs/en/sub-agents", guide)
        self.assertIn("https://geminicli.com/docs/core/subagents/", guide)
        self.assertIn("./lacuna checkpoint run dispatch", guide)
        self.assertIn("lacuna-retcon-generator", guide)
        self.assertIn("may change", guide.lower())


if __name__ == "__main__":
    unittest.main()
