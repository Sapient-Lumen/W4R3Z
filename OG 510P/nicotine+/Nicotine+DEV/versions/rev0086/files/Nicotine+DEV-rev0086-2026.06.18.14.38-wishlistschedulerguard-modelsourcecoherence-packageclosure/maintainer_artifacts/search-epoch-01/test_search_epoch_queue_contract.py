"""Why ordinary fire-and-forget enqueue calls are not a transaction."""
from __future__ import annotations

from search_epoch_model import FireAndForgetQueue, enqueue_three_ordinary_messages


def test_disabled_current_style_queue_silently_drops_entire_triad():
    queue = FireAndForgetQueue(enabled=False)
    enqueue_three_ordinary_messages(queue, old_token=90, new_token=91)
    assert queue.items == []


def test_enabled_current_style_queue_preserves_call_order_only():
    queue = FireAndForgetQueue(enabled=True)
    enqueue_three_ordinary_messages(queue, old_token=90, new_token=91)
    assert queue.items == [("remove", 90), ("add", 91), ("send", 91)]
