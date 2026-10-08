# Scenario: multiple format versions do not imply every query is safe

A consumer can genuinely support several rustdoc JSON format versions.
That still does not mean every downstream query or relation is equally supported.

This scenario keeps format-window support separate from downstream query scope.
