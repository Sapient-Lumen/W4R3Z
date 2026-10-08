# Public-overlap policy for Nicotine+DEV

This cube treats public-overlap as a first-class gate. A finding may be true and useful while still duplicating, extending, or regression-testing work already visible in issues, pull requests, discussions, release notes, commits, or documentation.

## Required statuses

Every finding must eventually receive one of these statuses:

1. `direct-public`: the same root cause, same sink, or same fix target is publicly described.
2. `public-adjacent`: public work describes nearby behavior, symptoms, class, or a partial remediation, but not the exact finding.
3. `upstream-in-flight`: current/future releases or PRs appear to fix or refactor the relevant boundary.
4. `candidate no-direct-public-found`: exact searches found no direct public overlap; this is provisional and must name the searches performed.
5. `insufficient-search`: some searching happened but not enough to rely on.
6. `not searched`: no real public-overlap evidence yet.

## Strict document admission rule

The high-priority/high-quality document may include only findings that meet all of these conditions:

- current and future source lanes checked;
- exact public-overlap searches recorded;
- source-level invariant identified;
- proof sketch or small reproduction path written;
- severity boundary stated without inflation;
- duplicate/alias check against the datacube completed;
- decision written as `fresh candidate`, `public-adjacent`, `upstream/backport`, or `regression-only`.

`candidate no-direct-public-found` does not mean proven novel. It means the hard-search record did not find direct public overlap yet.
