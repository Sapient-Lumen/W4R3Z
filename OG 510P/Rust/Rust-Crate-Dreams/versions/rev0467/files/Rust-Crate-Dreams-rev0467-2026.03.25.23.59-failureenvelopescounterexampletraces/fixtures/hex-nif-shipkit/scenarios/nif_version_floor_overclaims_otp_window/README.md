# Scenario — NIF version floor overclaims OTP window

The package claims support for OTP 22+, but its Rustler feature selection and generated artifacts only cover NIF `2.17`, which corresponds to OTP 26+.

Expected verdict: `nif_window_claim_exceeds_features`.
