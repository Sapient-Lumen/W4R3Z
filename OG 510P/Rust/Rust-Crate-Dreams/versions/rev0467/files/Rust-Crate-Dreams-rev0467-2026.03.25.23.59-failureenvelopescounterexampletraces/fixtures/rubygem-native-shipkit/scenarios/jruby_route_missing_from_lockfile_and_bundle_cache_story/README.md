# Scenario: JRuby route missing from lockfile and bundle-cache story

The gem README claims support for JRuby via fallback/source-build posture.
But the checked-in `Gemfile.lock` only carries MRI/native platform targets and the release workflow never caches all platforms, so the actual route for JRuby users remains under-specified.
