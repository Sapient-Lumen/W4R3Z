# external_monitor_capture_and_stack_sanitization_need_capture_receipt

This scenario shows why “we wrote a minidump” is not enough.
An out-of-process monitor using `minidumper` / `minidump-writer` has a different trust and privacy posture from in-process crash capture, and stack sanitization needs to be explicit.
