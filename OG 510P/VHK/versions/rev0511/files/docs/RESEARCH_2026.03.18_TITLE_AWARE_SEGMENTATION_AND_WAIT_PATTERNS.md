# Research — title-aware recorder segmentation and wait patterns

Why this note exists
--------------------

Revision 0318 extends recorder segmentation so one recorded window can be split
into multiple guarded segments when the title changes and the author opts into
that fragility.

Design lesson
-------------

Window identity is not always the same as workflow identity. Browser tabs,
editor buffers, terminal tabs, and document viewers often reuse one top-level
window while changing only the title. A recorder that only notices window ID /
class changes will flatten those transitions into delays, even though users
experience them as distinct states.

VHK answer
----------

- keep the default segmentation lane conservative and window-identity-first
- add an explicit opt-in for title-aware segmentation instead of making title
  fragility the default
- reuse the existing selector suggestion machinery so per-segment stable/exact
  selectors still get chosen honestly
- when multiple title segments would share the same stable selector, fall back
  to exact selectors per segment so the recorded title boundary survives review

Why this stays opt-in
---------------------

Title text is useful, but it is also noisy. Loading spinners, unsaved markers,
notification counts, and document prefixes can all churn. The right Linux-native
lesson is not "ignore titles" or "always trust titles"; it is "make title
matching explicit when the workflow truth depends on it".
