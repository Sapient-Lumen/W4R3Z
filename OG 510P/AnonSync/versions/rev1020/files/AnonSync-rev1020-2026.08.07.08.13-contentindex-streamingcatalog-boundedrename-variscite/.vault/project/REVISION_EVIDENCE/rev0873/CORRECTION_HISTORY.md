# Correction history retained

1. An earlier richer transient branch disappeared during a cloudtainer reset.
   No result from that vanished workspace is used as release evidence. Rev0873
   was reconstructed from the independently verified rev0872 archive.
2. The first recovered design tried to reconstruct old release time from a
   retained deadline. That would have turned a lower bound into invented exact
   history. The final migration uses an explicit `LegacyUnproven` marker and
   zero exact release epoch instead.
3. A build-graph audit found the new time-fence test in CTest but not in
   sanitizer target lists. The final CMake graph instruments both the library
   and test and links the sanitizer runtime into the executable.
4. Stale test/audit names said malformed migrations failed "into v3" after the
   destination had become v4. The vocabulary was corrected so diagnostics name
   the boundary they actually protect.
5. README wording was corrected before sealing: final directory and ZIP
   verification are external post-manifest checks, not self-referential files
   embedded in the package.
6. Patch authority is the verified rev0872 parent plus the exact 13-file active
   delta. The patch was applied to a fresh parent active tree and all 340 active
   files were compared byte-for-byte.

These corrections remain part of the handoff because assurance depends on
separating observed success, recovery, cleanup, and inference.
