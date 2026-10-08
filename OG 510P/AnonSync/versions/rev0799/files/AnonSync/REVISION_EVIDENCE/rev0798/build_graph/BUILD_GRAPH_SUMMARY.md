# Rev0798 build-graph summary

The pure geometry proof is four fresh Ninja actions and two first-party
translation units (130 implementation + 239 test lines). It links neither the
core monolith, SQLite, OpenSSL, nor filesystem path security.

The integrated trailing-byte proof is ten fresh actions and four first-party
translation units plus the bundled SQLite C library. It still does not link the
22-translation-unit core archive. A fresh `anonsync_core` graph is 54 actions.
