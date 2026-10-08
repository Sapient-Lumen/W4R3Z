# same Miri pass but toolchain or target shift breaks direct comparison

This scenario models two green Miri runs that are not honestly identical evidence because the toolchain and interpreted target lane changed.

The comparison object should make the scope shift explicit instead of quietly calling this “no change”.
