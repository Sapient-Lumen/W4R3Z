# Browser policy relaxation

Revision: rev0028

## Problem

The cloudtainer Chromium environment can include a managed URL policy that blocks page navigation, including local pages. A browser test that ignores this may fail as a page navigation problem even though the app code is fine.

## Policy

BrowserRT browser tests may temporarily relax the local managed URL block policy only inside a single owned command. The command must restore the original policy text during teardown.

## Required behavior

A browser fixture that touches managed policy must:

1. record the policy path,
2. record whether the file existed,
3. record whether a global block was present,
4. write a temporary relaxed policy only when needed,
5. restore the original bytes during teardown,
6. mark restoration in the artifact,
7. fail loudly if cleanup cannot be trusted.

## Why not start a daemon?

A daemon would hide policy state and process state across a turn boundary. BrowserRT should assume cloudtainer turns are finite and that process survival is a non-claim. The fixture should be one-shot, explicit, and artifact-producing.

## Testing implication

Browser policy is part of the fixture, not part of the application. Future browser tasks must treat local server, browser launch, CDP connection, and policy restoration as owned setup/teardown work.
