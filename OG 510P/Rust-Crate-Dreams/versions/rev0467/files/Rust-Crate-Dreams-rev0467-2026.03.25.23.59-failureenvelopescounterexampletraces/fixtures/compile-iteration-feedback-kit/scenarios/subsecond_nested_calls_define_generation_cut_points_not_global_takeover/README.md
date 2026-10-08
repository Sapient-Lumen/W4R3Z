# Subsecond nested calls define generation cut points, not global takeover

This scenario freezes the fact that Subsecond nested `call` boundaries are explicit patch cut points.
A new inner generation can become active without proving that every surrounding route or retained frame is already on the same generation.
