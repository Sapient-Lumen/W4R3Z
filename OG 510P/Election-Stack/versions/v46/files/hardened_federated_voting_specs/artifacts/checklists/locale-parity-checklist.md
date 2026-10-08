# Locale & device parity checklist

- [ ] Produce ContentLocaleManifest (locale -> hash) and sign it
- [ ] Include locale manifest hash in EPB
- [ ] Verify locale pack hashes during build + release
- [ ] Parity monitors fetch each locale canary and verify hash
- [ ] Ensure API and UI show same pinned hashes across locales and device classes
