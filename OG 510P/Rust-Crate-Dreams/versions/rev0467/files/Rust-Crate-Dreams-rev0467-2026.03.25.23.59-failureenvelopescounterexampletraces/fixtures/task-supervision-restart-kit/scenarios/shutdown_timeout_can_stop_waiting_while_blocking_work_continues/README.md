# Scenario: shutdown timeout can stop waiting while blocking work continues

A service uses cooperative cancellation for async children but also has started blocking work. The receipt needs to make it explicit that timeout may only stop waiting, not necessarily stop the blocking work itself.

