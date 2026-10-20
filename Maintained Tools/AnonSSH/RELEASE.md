# AnonSSH 0.2.0: downloads, source and provenance

[Portable x86-64 Linux executable and supporting files](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/anonssh-v0.2.0-9831b007cd47) · [Introduction](README.md) · [Project source](source/) · [Version-pinned third-party source index](SOURCE-INDEX.md)

## Portable distribution

The `anonssh` download is the supplied static x86-64 Linux executable, including its six child-program payloads and public I2P bootstrap corpus. It is not the separate Nix-integrated Monsternix package. External tools such as Git, rsync, Borg and SSHFS remain external applications. Follow the [project operating guide](source/README.md) for first use and server preparation.

- Supplied source revision: `9831b007cd47ad9d8b1c82c417804fac9a780db2`.
- Executable: **53,494,696 bytes**.
- SHA-256: `451f1eee963c9d16c27883054df5d3a70659ca8213eaec31ce5136886d521fcd`.
- Bootstrap contains 636 signed public RouterInfo records. Its source manifest and separate observation ledger retain selection provenance; these are startup hints rather than trust roots. Ordinary reseeding remains enabled.

`W4R3Z-SHA256SUMS` covers the files offered here, including the source supplement and notice collection. These are integrity checks, not a publisher signature.

## Source access without a large duplicate archive

Project code and documentation are browsable under [source/](source/). The complete 721-file project build tree, including all 636 binary RouterInfos, is separately available as the compact `anonssh-project-source-9831b007cd47-public.zip` release asset (1,282,767 bytes). These RouterInfo bytes remain in both that archive and the portable executable; they are not duplicated as hundreds of individual Git files. [SOURCE-INDEX.md](SOURCE-INDEX.md) names exact upstream versions, revisions, download locations, build expressions and patches; its machine-readable companion retains hash kinds explicitly. The 219 MB aggregate source archive is **not** distributed here. Source access is provided through the indexed upstream locations and the project/build modifications in this repository instead.

The small `anonssh-source-supplement-20261020.zip` contains the exact pinned libxcrypt 4.5.2 release source, its supplied Nix recipe/local patch and applicable licensing files, plus the identified upstream libevent patch. The downloaded patch's raw hash differs from Nix fetchpatch's normalized-output hash; the supplement distinguishes them. It does not change the portable executable.

Tor's enabled GPL code and the statically linked libxcrypt have source-distribution conditions. See [GPLv3 section 6(d)](https://www.gnu.org/licenses/gpl-3.0.html#section6) and [libxcrypt's LGPL terms](https://github.com/besser82/libxcrypt/blob/v4.5.2/COPYING.LIB). Separate linked source access is different from requiring every recipient to download source with the executable. The distributor remains responsible for maintaining the required access; a source index is not a reason to ignore broken or mismatched links.

## Notices and inventory scope

The original [project license](source/LICENSE) and [third-party summary](source/THIRD_PARTY.md) are preserved. Their package-level labels are not an exhaustive inventory of every linked component: Dropbear includes libxcrypt; the SSH client includes LDNS; i2pd includes Boost. The linked liblzma component of XZ 5.8.4 is **0BSD**, despite the wider source package's mixed licensing. Applicable upstream texts remain associated with the named source components; libxcrypt's explicit notice/license files also accompany the supplement.

`anonssh-notices-20261020.zip` provides an indexed collection of upstream licensing files from the supplied component/vendor sources, plus explicit libxcrypt terms. `ADDITIONAL-NOTICES.txt` preserves the LDNS copyright notice and Boost Software License alongside that collection. Source-vendored crates include build and other-target dependencies, not only code linked into this executable. The source index does not claim a newly reproduced binary, a complete independently reconstructed link map, or an independently verified offline rebuild. Controlled protocol measurements and live overlay behavior have different scopes, explained in the [evidence guide](source/docs/context/evidence.md).

## Preservation

The executable and original release metadata are unchanged. Project implementation files retain supplied bytes and modes. The complete project-source ZIP makes one documentation-only publication edit that replaces the maintainer's local home-directory checkout example in `source/README.md` with `/path/to/AnonSSH`; the original supplied README remains preserved privately. The browsing README additionally explains that its complete build tree is the ZIP. These documentation edits change neither the build expression nor the program. The public source is therefore a transparently documented publication snapshot, not an assertion that every documentation byte is identical to the original handoff.

Project copyright and attribution remain with h0p3 and the respective upstream authors. W4R3Z's introduction, source index and release explanation are editorial additions.
