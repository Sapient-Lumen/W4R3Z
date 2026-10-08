from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PromptProfileStore:
    path: Path
    _data: dict[str, Any] | None = None

    def _ensure_loaded(self) -> dict[str, Any]:
        if self._data is not None:
            return self._data
        if self.path.exists():
            try:
                payload = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                payload = {}
        else:
            payload = {}
        if not isinstance(payload, dict):
            payload = {}
        payload.setdefault("version", 1)
        payload.setdefault("last", {})
        payload.setdefault("profiles", {})
        self._data = payload
        return payload

    def load_last(self, key: str) -> dict[str, Any]:
        data = self._ensure_loaded()
        value = data.get("last", {}).get(key, {})
        return dict(value) if isinstance(value, dict) else {}

    def load_profile(self, key: str, profile_name: str) -> dict[str, Any]:
        data = self._ensure_loaded()
        value = data.get("profiles", {}).get(key, {}).get(profile_name, {})
        return dict(value) if isinstance(value, dict) else {}

    def save_last(self, key: str, values: dict[str, Any]) -> None:
        data = self._ensure_loaded()
        data.setdefault("last", {})[key] = dict(values)
        self._flush()

    def save_profile(self, key: str, profile_name: str, values: dict[str, Any]) -> None:
        data = self._ensure_loaded()
        profiles = data.setdefault("profiles", {})
        bucket = profiles.setdefault(key, {})
        bucket[profile_name] = dict(values)
        self._flush()

    def has_profile(self, key: str, profile_name: str) -> bool:
        data = self._ensure_loaded()
        bucket = data.get("profiles", {}).get(key, {})
        return isinstance(bucket, dict) and profile_name in bucket

    def copy_profile(self, key: str, source_name: str, target_name: str, *, overwrite: bool = False) -> bool:
        data = self._ensure_loaded()
        profiles = data.get("profiles", {})
        if not isinstance(profiles, dict):
            return False
        bucket = profiles.get(key)
        if not isinstance(bucket, dict) or source_name not in bucket:
            return False
        if target_name in bucket and not overwrite:
            raise FileExistsError(f"Profile already exists: {key} #{target_name}")
        bucket[target_name] = dict(bucket[source_name])
        self._flush()
        return True

    def rename_profile(self, key: str, old_name: str, new_name: str, *, overwrite: bool = False) -> bool:
        data = self._ensure_loaded()
        profiles = data.get("profiles", {})
        if not isinstance(profiles, dict):
            return False
        bucket = profiles.get(key)
        if not isinstance(bucket, dict) or old_name not in bucket:
            return False
        if new_name in bucket and new_name != old_name and not overwrite:
            raise FileExistsError(f"Profile already exists: {key} #{new_name}")
        bucket[new_name] = dict(bucket[old_name])
        if new_name != old_name:
            del bucket[old_name]
        self._flush()
        return True

    def list_profiles(self, key: str) -> list[str]:
        data = self._ensure_loaded()
        bucket = data.get("profiles", {}).get(key, {})
        if not isinstance(bucket, dict):
            return []
        return sorted(str(name) for name in bucket.keys() if str(name).strip())

    def list_all_profiles(self) -> dict[str, list[str]]:
        data = self._ensure_loaded()
        profiles = data.get("profiles", {})
        if not isinstance(profiles, dict):
            return {}
        out: dict[str, list[str]] = {}
        for key, bucket in profiles.items():
            if not isinstance(bucket, dict):
                continue
            names = sorted(str(name) for name in bucket.keys() if str(name).strip())
            if names:
                out[str(key)] = names
        return dict(sorted(out.items()))

    def export_profiles(self) -> dict[str, dict[str, dict[str, Any]]]:
        data = self._ensure_loaded()
        profiles = data.get("profiles", {})
        if not isinstance(profiles, dict):
            return {}
        out: dict[str, dict[str, dict[str, Any]]] = {}
        for key, bucket in profiles.items():
            if not isinstance(bucket, dict):
                continue
            rows: dict[str, dict[str, Any]] = {}
            for name, values in bucket.items():
                if not str(name).strip() or not isinstance(values, dict):
                    continue
                rows[str(name)] = dict(values)
            if rows:
                out[str(key)] = dict(sorted(rows.items()))
        return dict(sorted(out.items()))

    def delete_profile(self, key: str, profile_name: str) -> bool:
        data = self._ensure_loaded()
        profiles = data.get("profiles", {})
        if not isinstance(profiles, dict):
            return False
        bucket = profiles.get(key)
        if not isinstance(bucket, dict) or profile_name not in bucket:
            return False
        del bucket[profile_name]
        if not bucket:
            profiles.pop(key, None)
        self._flush()
        return True

    def _flush(self) -> None:
        data = self._ensure_loaded()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.replace(self.path)


def make_prompt_profile_store(project_root: str | Path, relative_path: str = ".vhk/prompt_profiles.json") -> PromptProfileStore:
    root = Path(project_root)
    rel = Path(relative_path)
    path = rel if rel.is_absolute() else (root / rel)
    return PromptProfileStore(path=path)


def sanitize_prompt_answers(fields, values: dict[str, Any] | None) -> dict[str, Any]:
    if not values:
        return {}
    keep: dict[str, Any] = {}
    for field in fields or []:
        name = str(getattr(field, "name", "") or "").strip()
        if not name or name not in values:
            continue
        if str(getattr(field, "kind", "")).lower() == "password":
            continue
        if not bool(getattr(field, "remember", True)):
            continue
        keep[name] = values[name]
    return keep


def apply_saved_answers(fields, saved_values: dict[str, Any] | None):
    if not saved_values:
        return list(fields)
    updated = []
    for field in fields:
        default = getattr(field, "default", None)
        name = str(getattr(field, "name", "") or "").strip()
        if name and name in saved_values and str(getattr(field, "kind", "")).lower() != "password" and bool(getattr(field, "remember", True)):
            default = saved_values[name]
        updated.append(type(field)(
            name=field.name,
            label=getattr(field, "label", None),
            kind=getattr(field, "kind", "text"),
            default=default,
            choices=list(getattr(field, "choices", []) or []),
            remember=bool(getattr(field, "remember", True)),
        ))
    return updated
