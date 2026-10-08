# Scenario — checksum file missing from Hex tarball

The package generated `checksum-Elixir.MyPkg.Native.exs` in CI and uploaded precompiled artifacts, but `mix.exs` forgot to include `checksum-*.exs` in the Hex package `files:` list.

Expected verdict: `checksum_file_missing_from_tarball`.
