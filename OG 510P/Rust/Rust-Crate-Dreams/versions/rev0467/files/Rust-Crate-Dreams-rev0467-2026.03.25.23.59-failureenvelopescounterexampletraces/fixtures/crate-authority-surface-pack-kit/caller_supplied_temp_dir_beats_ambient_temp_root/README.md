# caller_supplied_temp_dir_beats_ambient_temp_root

This scenario exists to keep **P-0519** honest about **authority origin**.

A crate may offer both:

- an ambient temp-root path (`tempdir()` / `TempDir::new(...)`), and
- a capability-oriented temp-root path (`tempdir_in(&Dir)` / `TempDir::new_in(&Dir)`).

A worthy authority-surface crate should make it obvious that the second route is not just “also available somewhere in the crate”.
It should be able to say that in the named profile the **origin of tempdir authority is caller-supplied capability**, and that ambient tempdir discovery is either forbidden or only used in a different profile.
