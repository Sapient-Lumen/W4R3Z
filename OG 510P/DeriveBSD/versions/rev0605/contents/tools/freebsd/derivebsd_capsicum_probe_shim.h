/*
 * Cloudtainer syntax-only shim for rm_post_detach_capsicum_worker.c.
 *
 * This header is deliberately enabled only by DERIVEBSD_CAPSICUM_COMPILE_PROBE.
 * It is not a Capsicum implementation and must never be used for a production
 * worker build.  It lets Linux CI catch ordinary C syntax/signature drift until
 * the real FreeBSD build/run lane exists.
 */
#ifndef DERIVEBSD_CAPSICUM_PROBE_SHIM_H
#define DERIVEBSD_CAPSICUM_PROBE_SHIM_H

#define CAP_READ 0x0001u
#define CAP_WRITE 0x0002u
#define CAP_FSTAT 0x0004u
#define CAP_FSYNC 0x0008u

typedef struct derivebsd_probe_cap_rights {
    unsigned int rights_seen;
} cap_rights_t;

static inline cap_rights_t *
derivebsd_probe_cap_rights_init(cap_rights_t *rights)
{
    rights->rights_seen = 0;
    return rights;
}

/* The real FreeBSD cap_rights_init() accepts a comma-separated rights list
 * without a sentinel. Use a variadic macro in the shim so the cloudtainer
 * execution probe cannot read beyond provided arguments while pretending to
 * parse rights. */
#define cap_rights_init(rights, ...) derivebsd_probe_cap_rights_init((rights))

static inline int
cap_rights_limit(int fd, const cap_rights_t *rights)
{
    (void)fd;
    (void)rights;
    return 0;
}

static inline int
cap_enter(void)
{
    return 0;
}

static inline void
derivebsd_probe_closefrom(int lowfd)
{
    for (int fd = lowfd; fd < 1024; fd++)
        (void)close(fd);
}

#define closefrom derivebsd_probe_closefrom

#endif /* DERIVEBSD_CAPSICUM_PROBE_SHIM_H */
