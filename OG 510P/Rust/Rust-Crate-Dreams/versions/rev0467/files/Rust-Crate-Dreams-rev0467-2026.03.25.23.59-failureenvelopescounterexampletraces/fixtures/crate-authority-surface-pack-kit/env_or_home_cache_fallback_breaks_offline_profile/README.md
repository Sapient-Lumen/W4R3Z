# Env-or-home fallback breaks offline profile

Focus: a crate advertises an `offline_readonly` profile, but on cache miss it falls back to `$XDG_CACHE_HOME`, `$HOME`, or a temp directory.
This fixture exists to prove that “no network” is not enough if authority budget and witness artifacts do not also account for env reads, home-dir discovery, and opportunistic filesystem writes.
