# Minimal XSS corpus (seed)

These inputs are intended for sanitization conformance tests. They should render safely (no script execution) after the pipeline.

1) Raw script tag:
<script>alert(1)</script>

2) Event handler attribute:
<img src=x onerror=alert(1)>

3) JavaScript URL:
[click](javascript:alert(1))

4) SVG/onload:
<svg onload=alert(1)></svg>

5) HTML comment tricks:
<!--><script>alert(1)</script>-->

