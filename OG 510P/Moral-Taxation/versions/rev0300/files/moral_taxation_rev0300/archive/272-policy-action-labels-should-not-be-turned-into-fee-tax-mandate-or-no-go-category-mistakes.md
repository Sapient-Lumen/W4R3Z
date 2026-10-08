# 272. Policy-action labels should not be turned into fee, tax, mandate, or no-go category mistakes

Rev0290 adds a policy-action profile layer because the cube could already say what route fired, what remedy followed, and what golden case tested the answer, but it still allowed a quieter category mistake: the proposal's label could smuggle in the policy action. A charge called a fee might fund broad public regulation. A tax might try to sell permission for non-compensable harm. A mitigation payment might be used where the correct answer is denial. A rebate might go to the remitter while the real burden bearer waits.

The new rule is that `instrument` is an axis, not a conclusion. Each route now has an action family, legitimate use, category error to block, required distinctions, and a remedy-profile link. This lets the archive ask whether the correct move is tax, fee, duty, public option, compensation, no-go rule, or release block before it argues about rate design.

The practical test is simple: if the action would still be wrong after the rate is set perfectly, the problem is not rate calibration. It is instrument semantics. Fix the action family first.

## Source cues

[S573][S662][S663][S664]

[S573]: ../SOURCES.md#S573
[S662]: ../SOURCES.md#S662
[S663]: ../SOURCES.md#S663
[S664]: ../SOURCES.md#S664
