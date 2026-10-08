from __future__ import annotations

from pathlib import Path

from vhk.project.prompt_profiles import PromptProfileStore, apply_saved_answers, make_prompt_profile_store, sanitize_prompt_answers
from vhk.system.dialogs import FormField


def test_prompt_profile_store_saves_last_and_named_profiles(tmp_path: Path) -> None:
    store = make_prompt_profile_store(tmp_path, ".vhk/prompt_profiles.json")

    store.save_last("macro:deploy:preset:prod", {"ticket": "OPS-1", "version": "1.2.3"})
    store.save_profile("macro:deploy:preset:prod", "release", {"ticket": "OPS-9", "version": "9.9.9"})

    assert store.load_last("macro:deploy:preset:prod") == {"ticket": "OPS-1", "version": "1.2.3"}
    assert store.load_profile("macro:deploy:preset:prod", "release") == {"ticket": "OPS-9", "version": "9.9.9"}
    assert (tmp_path / ".vhk" / "prompt_profiles.json").exists()


def test_apply_saved_answers_overrides_defaults_but_not_passwords() -> None:
    fields = [
        FormField(name="version", kind="text", default="1.0.0"),
        FormField(name="token", kind="password", default="secret"),
        FormField(name="remembered", kind="text", default="old", remember=True),
        FormField(name="ignored", kind="text", default="old", remember=False),
    ]

    updated = apply_saved_answers(
        fields,
        {"version": "2.0.0", "token": "newsecret", "remembered": "new", "ignored": "skip"},
    )

    assert [f.default for f in updated] == ["2.0.0", "secret", "new", "old"]


def test_sanitize_prompt_answers_excludes_passwords_and_nonremembered() -> None:
    fields = [
        FormField(name="version", kind="text", remember=True),
        FormField(name="token", kind="password", remember=True),
        FormField(name="note", kind="text", remember=False),
    ]

    saved = sanitize_prompt_answers(fields, {"version": "2.0.0", "token": "abc", "note": "skip"})

    assert saved == {"version": "2.0.0"}


def test_prompt_profile_store_can_list_and_delete_named_profiles(tmp_path: Path) -> None:
    store = make_prompt_profile_store(tmp_path, ".vhk/prompt_profiles.json")

    store.save_profile("macro:deploy:preset:prod", "release", {"ticket": "OPS-9"})
    store.save_profile("macro:deploy:preset:prod", "hotfix", {"ticket": "OPS-8"})

    assert store.list_profiles("macro:deploy:preset:prod") == ["hotfix", "release"]
    assert store.list_all_profiles() == {"macro:deploy:preset:prod": ["hotfix", "release"]}
    assert store.delete_profile("macro:deploy:preset:prod", "hotfix") is True
    assert store.list_profiles("macro:deploy:preset:prod") == ["release"]
    assert store.delete_profile("macro:deploy:preset:prod", "missing") is False
