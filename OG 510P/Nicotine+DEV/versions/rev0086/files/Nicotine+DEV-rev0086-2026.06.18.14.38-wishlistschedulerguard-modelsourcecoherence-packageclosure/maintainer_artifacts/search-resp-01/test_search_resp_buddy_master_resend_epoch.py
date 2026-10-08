"""Bundled-master counterexample: Search Again needs a fresh buddy epoch."""
from pynicotine.search import Search, SearchRequest

from buddy_search_harness import install_environment, recipient_names


def existing_search():
    return SearchRequest(
        token=530031,
        term="rareprobe",
        term_sanitized="rareprobe",
        term_transmitted="rareprobe",
        included_words=["rareprobe"],
        excluded_words=[],
        mode="buddies",
        users=("removed_buddy", "staying_buddy"),
    )


def test_resend_uses_current_buddy_list(monkeypatch):
    core, sent = install_environment(monkeypatch, ["staying_buddy", "new_buddy"])
    Search._send_buddies_search_request(object(), existing_search())
    assert core.buddies.users == ["staying_buddy", "new_buddy"]
    assert recipient_names(sent) == ["staying_buddy", "new_buddy"]


def test_rev0040_resend_reuses_initial_snapshot(monkeypatch):
    _core, sent = install_environment(monkeypatch, ["staying_buddy", "new_buddy"])
    Search._send_buddies_search_request(object(), existing_search())
    assert recipient_names(sent) == ["removed_buddy", "staying_buddy"]
