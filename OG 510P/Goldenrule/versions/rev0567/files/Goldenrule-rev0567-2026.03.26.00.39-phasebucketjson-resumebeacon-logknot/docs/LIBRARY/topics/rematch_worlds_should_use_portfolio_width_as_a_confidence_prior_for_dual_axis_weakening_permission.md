# Rematch worlds should use portfolio width as a confidence prior for dual-axis weakening permission

The weakening guardrail stack now has a confidence ladder, not just a possibility ladder.

The earlier width law said when dual-axis permission *can* become dominant or universal. This pass adds the sharper prior for random width-conditioned portfolios:

- width `4` is the first point where dual-axis permission is more likely than not
- width `7` is the first point where it is a `90%` prior
- width `10` is the first point where it is a `99%` prior
- width `11` leaves only a single non-dual-axis exception

The residual one-axis tail also collapses in a structured way.

From width `2` onward, the surviving non-dual-axis exceptions are always dominated by the `suffix_only` family. By width `8`, that suffix-only family already makes up at least three quarters of the remaining tail; by width `11`, it is the entire tail.

This gives the inheritor a compact stochastic policy prior:

- widths `1–3`: do not assume dual-axis permission unless the batch is known to mix hole families
- widths `4–6`: dual-axis permission is the default guess, but one-axis curation still has meaningful mass
- widths `7–10`: treat dual-axis permission as the overwhelming prior, with only a shrinking suffix-only tail worth manual exemption
- width `11`: there is only one surviving one-axis exception
- widths `12+`: dual-axis permission is forced, not merely likely

Future redesign signal: if the confidence ladder `{4, 5, 7, 8, 10, 11}` or the suffix-tail ladder `{3, 8, 10, 11}` moves, the current weakening staircase and hole-family geometry have changed materially.
