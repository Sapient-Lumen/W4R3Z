# Worked Example Acceptance Tests & Ship Gates


**Purpose:** stop fake fixes from shipping by naming the minimum tests a repaired workflow must pass.

**Person served:** implementers, product teams, auditors, and supervisors.

---

## Ship gates

A proposed fix should not ship unless it can answer yes to these:
1) Does the person get a usable receipt?
2) Is there a visible owner and clock?
3) Does interim protection keep the person safe while review runs?
4) Can a reviewer replay what happened?
5) If the fix depends on vendors or delegation, is the public owner still visible?
6) If the workflow is multi-stage, can preliminary layers no longer execute final harm by stealth?
