## Surface-shift timeline

### Purpose
Show how the truthful surface for an action changed over time.

### Timeline event types
- **surface became primary**: desktop app, WebUI, mobile, or headless/config lane became the active control/execution surface
- **surface-only exception discovered**: action found to be desktop-only, Android-only, ignored in Linux WebUI, or unavailable on iOS
- **witness shift**: success/failure could only be confirmed on another surface
- **out-of-band recovery event**: operator had to use file browser, shell, config, or service manager
- **browser / OS handoff break**: browser or OS stopped the fast path while the artifact itself remained valid
- **runtime posture shift**: service/headless/mobile/background posture changed what could honestly be promised
- **surface parity repair**: later version or posture restored stronger same-surface capability

### Timeline rules
- preserve both **what the operator tried here** and **where the truthful lane actually lived**
- keep surface loss visibly separate from permission loss or artifact invalidity
- keep out-of-band recovery visibly separate from in-product recovery
- keep Android/iOS divergence visibly separate from generic `mobile` language

### Why this matters
A later operator should be able to answer:
- when did this action stop being honestly completable from the current surface?
- was the failure caused by runtime class, platform rules, browser/OS handoff, or true product absence?
- which stronger same-surface sentence is still blocked now?
