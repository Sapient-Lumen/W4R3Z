# rev0018 experiment matrix additions

| Axis | rev0018 status | Why it matters |
|---|---:|---|
| C++ transition diff cases | 10,022 | Larger stack/choice coverage before full rollout acceleration |
| Response-pass resolution cases | 830 | Tests real stack-resolve traffic instead of only spell-cast traffic |
| Choice cases | 743 | Tests Overlord discard, Jace choices, cleanup discard, legend rule |
| Attack-action cases | 53 | Tests trigger-producing attack actions, not only pass/block combat |
| Ordered-library signatures | yes | Required for Brainstorm and Jace +2 bottoming |
| Chosen-action C++ support | 100% in smoke | Shows current sampled public agents stay inside covered transition space |
| Legal-action C++ support | 100% in smoke | More important than chosen-only support for future learned agents |

## Next experimental use

The new coverage/diff artifacts should guide C++ batching work. The best next experiment is not a larger strategy tournament; it is a short recorded DecisionFrame trace played through Python and through C++ one-action transitions, checking every intermediate `SIGv2`.
