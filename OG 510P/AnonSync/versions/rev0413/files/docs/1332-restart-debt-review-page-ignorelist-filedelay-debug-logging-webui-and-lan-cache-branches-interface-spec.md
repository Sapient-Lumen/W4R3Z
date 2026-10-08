## Restart-debt review page

### Question
What still depends on a later boundary event before this change is truly in force?

### Mandatory review branches
1. **Hot-reread file branch**  
   Use when a sidecar like IgnoreList can be re-read on change or at rescan, but immediate full adoption is not yet proven.

2. **Local-restart branch**  
   Use when the operator changed a storage-folder file such as FileDelayConfig or debug.txt and the docs say restart is the first honest activation rung.

3. **Service-restart branch**  
   Use when the effective process is a service and the changed control plane is only adopted when that service is restarted.

4. **Credential-reset branch**  
   Use when on-disk auth state changed but the currently running control surface is still governed by older credentials until process restart.

5. **Cache-burn branch**  
   Use when remembered peer or route data can survive a settings mutation until expiration knobs are changed and a restart sequence flushes the old memory.

6. **Successor-cutover branch**  
   Use when the real activation event is not a restart of the same runtime but a stop/replace/start or new world launch under a service/package/config regime.

### Required review outputs
- mutation locus
- minimum honest activation rung
- surviving old-world debt
- evidence still missing for a stronger immediacy claim
- safer wording for operators right now
