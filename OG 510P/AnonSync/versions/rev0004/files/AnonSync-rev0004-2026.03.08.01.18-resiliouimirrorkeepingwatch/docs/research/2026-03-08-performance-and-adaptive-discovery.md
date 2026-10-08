# 2026-03-08 — Performance and adaptive discovery research note

This note captures upstream findings that are strong enough to influence the archive now.

## Resilio lessons worth copying

- Resilio documents **filesystem notifications plus scheduled folder scans**, with a default `folder_rescan_interval` of **600 seconds**, and rescans on Sync start. See [How soon does synchronization start?](https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start) and [Power user preferences](https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences).
- Resilio documents a **small-file fast path**: `direct_torrent_enabled` avoids breaking small files into pieces, and `direct_torrent_mem_limit` caps RAM used by that path. See [Power user preferences](https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences).
- Resilio also exposes `prioritize_initial_indexing`, `lazy_indexing`, `disk_worker_pool_size`, and `parallel_indexing`, which is a strong signal that indexing and scan behavior need explicit operator-level control. See [Power user preferences](https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences).
- Resilio's LAN discovery docs say instances use multicast/broadcast on **UDP 3838**, and that discovery packets contain **ShareIDs and IP:port**. AnonSync should learn from the event posture, but not copy the stable-identifier wire image. See [What ports and protocols are used by Sync?](https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync) and [Key structure and flow](https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow).

## Syncthing lessons worth copying

- Syncthing's tuning guide recommends a **64-bit build** and keeping the **index database on SSD** for high performance. See [Configuration Tuning](https://docs.syncthing.net/users/tuning.html).
- Syncthing's security docs state that **local discovery defaults to on** and sends **broadcast/multicast packets every 30 seconds**, while **global discovery** announcements are every **30 minutes**. That makes a useful reference point for bounded steady-state cadence. See [Security Principles](https://docs.syncthing.net/users/security.html).
- Syncthing's FAQ explicitly says relayed connections are slower and should be checked first when troubleshooting speed. See [FAQ](https://docs.syncthing.net/users/faq.html).

## Tor lessons worth copying

- The Tor Project still publishes an **Expert Bundle** specifically for developers bundling Tor with applications, and the current stable Tor daemon listed there is **0.4.9.5**. See [Download Tor](https://www.torproject.org/download/tor/).
- The `torrc` man page documents `ConnectionPadding`, `CircuitPadding`, `ReducedConnectionPadding`, and `ReducedCircuitPadding`, and says these options should be offered to **mobile users where bandwidth may be expensive**. See [torrc(5)](https://manpages.debian.org/testing/tor/torrc.5.en.html).
- The same man page warns that `ConstrainedSockets` reduces TCP window sizes and can reduce throughput on long paths. That is a reminder not to turn RAM-saving knobs on blindly. See [torrc(5)](https://manpages.debian.org/testing/tor/torrc.5.en.html).

## i2pd lessons worth copying

- `i2pd` documents `notransit`, `bandwidth`, and `share` in its main config, which gives AnonSync direct levers for a non-transit bundled posture. See [Configuring](https://i2pd.readthedocs.io/en/latest/user-guide/configuration/).
- i2pd's tunnel docs expose `i2p.streaming.profile`, `i2p.streaming.maxWindowSize`, and stream speed caps. Those are real tuning seams for future provider-specific profiles. See [I2P tunnels configuration](https://i2pd.readthedocs.io/en/latest/user-guide/tunnels/).
- i2pd's FAQ says it uses less memory and CPU than Java I2P and advises setting correct bandwidth/share values. See [FAQ](https://i2pd.readthedocs.io/en/latest/user-guide/FAQ/).

## SQLite and hashing posture

- SQLite's WAL docs say WAL is often faster, gives more concurrency, and allows readers and writers to proceed concurrently. See [Write-Ahead Logging](https://sqlite.org/wal.html).
- SQLite's network guidance says the database engine should be on the **same machine** as the database, not across a high-traffic network boundary. See [SQLite Over a Network](https://sqlite.org/useovernet.html).
- SQLite's mmap docs say memory-mapped I/O is **disabled by default**, mainly helps reads, and uses address space equal to the configured `mmap_size` per database file. See [Memory-Mapped I/O](https://sqlite.org/mmap.html).
- SQLite's security guidance for hostile database files says **do not enable memory-mapped I/O**. AnonSync's own index is trusted local state, but this is still a warning against enabling mmap casually. See [Defense Against The Dark Arts](https://sqlite.org/security.html).
- The BLAKE3 draft describes BLAKE3 as **fast**, **highly parallelizable**, and suitable for incremental/tree-style hashing. See [The BLAKE3 Hashing Framework](https://www.ietf.org/archive/id/draft-aumasson-blake3-00.html).

## Archive opinions from this research

- Adaptation should mean **profiles + measurement**, not mysterious auto-magic.
- Discovery should be **event-sensitive** and **privacy-budgeted**.
- Mobile needs a **frugal** posture that changes Tor padding and discovery cadence together.
- Small-file direct send is worth copying, but only with a hard RAM ceiling.
- SQLite WAL is the right index default; mmap should stay off until benchmarks justify it.
