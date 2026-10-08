# Unsafe attribute obligation is a symbol contract, not a memory-model claim

This scenario keeps one semantic truth visible:
some unsafe obligations exist because the compiler cannot verify symbol/ABI properties, not because an interpreter is expected to find aliasing or initialization bugs.
