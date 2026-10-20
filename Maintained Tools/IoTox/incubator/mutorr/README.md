# Mutorr research incubator

Mutorr is preserved research from the Milehigh contribution. It is not part of the
ratox-successor northstar, the default build, the default test set, or the current
product claim.

Nothing here is discarded. The topology, placement, mutable-head, simulation,
benchmark, tests, and fuzz corpus remain buildable behind:

```sh
cmake -S . -B build/mutorr \
  -DIOTOX_BUILD_MUTORR_RESEARCH=ON \
  -DIOTOX_BUILD_RESEARCH_LAB=ON \
  -DIOTOX_BUILD_BENCHMARK=ON
cmake --build build/mutorr
ctest --test-dir build/mutorr --output-on-failure
```

Reactivation requires an explicit office-holder decision. It must not silently regain
core-product status merely because the code remains available.
