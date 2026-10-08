## Applied-state proof page

### Goal
Prove the strongest truthful sentence about whether the edited rule is active now.

### Proof ladder
1. **Disk-only proof**  
   We can prove the intended bytes or config text were written, but not that a running process adopted them.

2. **Reread-eligible proof**  
   We can prove the runtime class is one that may pick the change up on sidecar reread or rescan, but not that it already did.

3. **Post-rescan proof**  
   We can prove an explicit reread/rescan event occurred after the mutation and no stronger restart debt remains.

4. **Post-local-restart proof**  
   We can prove the local process restarted after the mutation and is the current authority for the changed behavior.

5. **Post-service-restart proof**  
   We can prove the governing service restarted after the mutation and the active service world owns the current behavior.

6. **Cache-burn proof**  
   We can prove the needed restart occurred and the remembered peer/route/cache debt was intentionally flushed.

7. **Successor-cutover proof**  
   We can prove a new runtime world or package/service instance is now governing the subject.

### Forbidden shortcuts
- Do not say `applied` when only disk-only proof exists.
- Do not say `restart completed, therefore done` when cache-burn proof is still absent.
- Do not say `service setting changed` when the interactive process, not the service, still owns the live behavior.
