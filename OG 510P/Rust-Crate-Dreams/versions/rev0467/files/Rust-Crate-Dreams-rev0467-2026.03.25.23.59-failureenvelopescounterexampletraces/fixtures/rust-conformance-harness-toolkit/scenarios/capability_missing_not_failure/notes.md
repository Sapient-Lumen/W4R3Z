# capability_missing_not_failure

The implementation did not advertise the required capability `profile:tls13`.

The important assertion is that the toolkit records this as **unsupported**, not **failed**.
That distinction matters for protocol interoperability dashboards and for any later assurance import.
