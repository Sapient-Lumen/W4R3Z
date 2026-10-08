## Surface-locality review

### Question this page answers
When the operator asks `can I do this here?`, is the answer **yes here**, **yes elsewhere**, **only out of band**, or **not honestly supported at all**?

### Review branches

#### 1) Desktop-native branch
Use this branch when a desktop app surface exposes the strongest action lane.
Render:
- whether execution is truly desktop-only
- whether witness and recovery also remain in desktop UI
- whether a shell / file-browser assist is still required

#### 2) WebUI-default / WebUI-limited branch
Use this branch when WebUI is the main surface or the only in-product surface for this runtime.
Render:
- whether the action executes in WebUI, only inspects there, or is omitted there
- whether a config-file, browser, or filesystem fallback is required
- exact note when the same setting or affordance is ignored in Linux WebUI

#### 3) Mobile branch
Use this branch when Android or iOS posture changes the answer.
Render:
- whether the action exists on Android, iOS, both, or neither
- whether background execution changes the truthful promise
- whether file-browser or `Open In...` handoff is needed to finish the work

#### 4) File-browser / shell branch
Use this branch when the strongest truthful action is outside the product surface.
Render:
- whether the user must use Finder / Explorer / file browser / terminal / service manager
- whether this is equivalent recovery or a weaker salvage path
- what state cannot be fully witnessed from the product after the handoff

#### 5) Browser / OS handoff branch
Use this branch when a browser, protocol handler, or OS permission boundary mediates the action.
Render:
- whether the action is blocked by browser/OS handoff rather than product authority
- whether manual paste or another lane preserves the same artifact semantics
- whether the review must be reopened because the lane materially changed

### Locality ladder
- **mentioned in docs** is weaker than **executable on this surface**
- **executable here** is weaker than **witnessable here**
- **witnessable here** is weaker than **recoverable here**
- **recoverable here** is weaker than **no out-of-band dependency remains**

### Forbidden overclaims
Do not let the UI say:
- `available` when only another surface can actually perform the work
- `recover here` when the operator must leave the product for filesystem or service-manager steps
- `supported on mobile` when the verb is Android-only or iOS-open-app-only
- `same action` when the fallback changes the review lane or evidence quality
