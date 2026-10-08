# Scenario: fresh advisory and new release force transition recheck, not silent keep

A previously accepted dependency posture should not silently carry forward when both an imported advisory signal and a newly published release appear.
The kit should emit one transition review packet that keeps the old basis visible, classifies the trigger, and records the new disposition.
