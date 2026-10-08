# Source notes for rev0103

This revision leaned especially on the same current official Resilio sources already listed below, but with fresh attention on the successor-artifact seam: current share-dialog docs still say expired links require a new link from the owner and that each `N+1` attempt by whoever fails, while current approval/link-flow docs still say remembered approval can survive separately across later sharing and successful approval still mints certificate-backed access.

# Sources

This revision intentionally relied on a small set of load-bearing sources checked on 2026-03-18.
The newest pass especially reused the share-dialog, link-flow, linked-device, online-peer, hidden-device, ghost-file, peer-list, and remembered-approval articles to keep the non-clone case about current product semantics rather than dated folklore.

## Resilio official

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log

- Important before updating to Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/31193941051795-Important-before-updating-to-Resilio-Sync-3-0-0

- Updating installation to Resilio Sync v3  
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- FAQ Resilio Sync 3.0.0  
  https://help.resilio.com/hc/en-us/articles/32109883606035-FAQ-Resilio-Sync-3-0-0

- Licensing in Resilio Sync 3.0  
  https://help.resilio.com/hc/en-us/articles/31116248751123-Licensing-in-Resilio-Sync-3-0

- How to apply license key and share license seats  
  https://help.resilio.com/hc/en-us/articles/204762369-How-to-apply-license-key-and-share-license-seats

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Guide to Linux, and Sync peculiarities  
  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities

- Running Sync as a service on Windows  
  https://help.resilio.com/hc/en-us/articles/207701296-Running-Sync-as-a-service-on-Windows

- Sync Service Troubleshooting on Windows  
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Is there a Command Line Interface (CLI) for Resilio Sync on Windows?  
  https://help.resilio.com/hc/en-us/articles/205506359-Is-there-a-Command-Line-Interface-CLI-for-Resilio-Sync-on-Windows

- Configuring WebUI  
  https://help.resilio.com/hc/en-us/articles/115001184490-Configuring-WebUI

- Browser warning "Your connection is not private"  
  https://help.resilio.com/hc/en-us/articles/4404757430291-Browser-warning-Your-connection-is-not-private

- No Sync icons in the file browser/no Sync-related items in the context menu on Mac/Windows  
  https://help.resilio.com/hc/en-us/articles/206214625-No-Sync-icons-in-the-file-browser-no-Sync-related-items-in-the-context-menu-on-Mac-Windows

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Core warnings  
  https://help.resilio.com/hc/en-us/articles/360001217950-Core-warnings

- If your device is stolen  
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

- Sync functionality in detail  
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Is one-way synchronization possible?  
  https://help.resilio.com/hc/en-us/articles/204754279-Is-one-way-synchronization-possible

- How to create a Read Only folder while syncing across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Comprehensive guide to syncing (Desktop-Desktop)  
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- Can I move or rename a syncing folder?  
  https://help.resilio.com/hc/en-us/articles/205450655-Can-I-move-or-rename-a-syncing-folder

- Folder not found / Can't open the destination folder  
  https://help.resilio.com/hc/en-us/articles/205450255-Folder-not-found-Can-t-open-the-destination-folder

- Disconnecting and Removing Folders  
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- Service files missing / Cannot identify destination folder  
  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder

- What's the difference between Standard and Advanced folders?  
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Folder Types and Management  
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- User Management  
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Conflict files in Sync  
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- Ignoring files in Sync (Ignore List)  
  https://help.resilio.com/hc/en-us/articles/205458165-Ignoring-files-in-Sync-Ignore-List

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- What Is an RSLS File?  
  https://help.resilio.com/hc/en-us/articles/206115384-What-Is-an-RSLS-File

- Sync Interface on iOS devices  
  https://help.resilio.com/hc/en-us/articles/212016726-Sync-Interface-on-iOS-devices

- Sync interface on Android  
  https://help.resilio.com/hc/en-us/articles/213500383-Sync-interface-on-Android

- Is it possible to share a nested folder separately?  
  https://help.resilio.com/hc/en-us/articles/205506159-Is-it-possible-to-share-a-nested-folder-separately

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Syncing between a desktop computer and a mobile device  
  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device

- Sync Preferences  
  https://help.resilio.com/hc/en-us/articles/204762669-Sync-Preferences

- Performance overview  
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Running Sync on schedule  
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule

- Using Archive for file versioning and restoring deleted files.  
  https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

- What if several people make changes to the same file?  
  https://help.resilio.com/hc/en-us/articles/204754209-What-if-several-people-make-changes-to-the-same-file

- How to manually set the location of the folders synced across linked devices?  
  https://help.resilio.com/hc/en-us/articles/206216615-How-to-manually-set-the-location-of-the-folders-synced-across-linked-devices

- Can I connect two pre-populated pre-existing folders?  
  https://help.resilio.com/hc/en-us/articles/205506569-Can-I-connect-two-pre-populated-pre-existing-folders

- Folder not empty  
  https://help.resilio.com/hc/en-us/articles/204753689-Folder-not-empty

- Folders are duplicating with an index (i) in their name.  
  https://help.resilio.com/hc/en-us/articles/204753869-Folders-are-duplicating-with-an-index-i-in-their-name

- Can I force Sync to do local network (LAN) syncing only and not sync via the Internet?  
  https://help.resilio.com/hc/en-us/articles/204754349-Can-I-force-Sync-to-do-local-network-LAN-syncing-only-and-not-sync-via-the-Internet

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Locked files  
  https://help.resilio.com/hc/en-us/articles/205504549-Locked-files

- Sync Storage folder  
  https://help.resilio.com/hc/en-us/articles/206664690-Sync-Storage-folder

- Storage Management on iOS  
  https://help.resilio.com/hc/en-us/articles/115001726304-Storage-Management-on-iOS

- Setting Delay Time For Syncing  
  https://help.resilio.com/hc/en-us/articles/207491426-Setting-Delay-Time-For-Syncing

- Selective Sync (Mobile)  
  https://help.resilio.com/hc/en-us/articles/206217315-Selective-Sync-Mobile

- Sharing files with mobile devices  
  https://www.resilio.com/documentation/content/advanced-configuration/resilio-on-mobile-devices/sharing_files_with_mobile_devices_/

- How can I improve data transfer/sync speed?  
  https://help.resilio.com/hc/en-us/articles/204762319-How-can-I-improve-data-transfer-sync-speed

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- What happens when file is renamed  
  https://help.resilio.com/hc/en-us/articles/209606526-What-happens-when-file-is-renamed

- How soon does synchronization start?  
  https://help.resilio.com/hc/en-us/articles/204754319-How-soon-does-synchronization-start

- What is '.sync' folder, and StreamsList, IgnoreList and Archive inside?  
  https://help.resilio.com/hc/en-us/articles/206217185-What-is-sync-folder-and-StreamsList-IgnoreList-and-Archive-inside

- What ports and protocols are used by Sync?  
  https://help.resilio.com/hc/en-us/articles/204754759-What-ports-and-protocols-are-used-by-Sync

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- What is a Relay Server?  
  https://help.resilio.com/hc/en-us/articles/204754779-What-is-a-Relay-Server

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- My files don't sync  
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Peers aren't connecting  
  https://help.resilio.com/hc/en-us/articles/205450205-Peers-aren-t-connecting

- "Time difference" error  
  https://help.resilio.com/hc/en-us/articles/204753599--Time-difference-error

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan  
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Some internal tasks are taking time to complete  
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Cannot connect to trackers  
  https://help.resilio.com/hc/en-us/articles/210587126-Cannot-connect-to-trackers

- Cloning Sync  
  https://help.resilio.com/hc/en-us/articles/360018421940-Cloning-Sync

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- Can I change the name of my Sync identity?  
  https://help.resilio.com/hc/en-us/articles/206163443-Can-I-change-the-name-of-my-Sync-identity

- How to uninstall Sync?  
  https://help.resilio.com/hc/en-us/articles/204775029-How-to-uninstall-Sync

- Sync and SMB file shares  
  https://help.resilio.com/hc/en-us/articles/207755736-Sync-and-SMB-file-shares

- Soft links, hard links and symbolic links  
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Alt Streams and Xattrs in Sync  
  https://help.resilio.com/hc/en-us/articles/204754729-Alt-Streams-and-Xattrs-in-Sync

- Encrypted folders  
  https://help.resilio.com/hc/en-us/articles/207370466-Encrypted-folders

- Collecting debug logs manually  
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting debug logs automatically  
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting crash reports, mini-dumps and core dumps  
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Send info to Support team  
  https://help.resilio.com/hc/en-us/sections/201494276-Send-info-to-Support-team

## Syncthing official

- REST API  
  https://docs.syncthing.net/dev/rest.html

- Event API  
  https://docs.syncthing.net/dev/events.html

- DevicePaused  
  https://docs.syncthing.net/events/devicepaused.html

- FolderPaused  
  https://docs.syncthing.net/events/folderpaused.html

- Prometheus-Style Metrics  
  https://docs.syncthing.net/users/metrics.html

- GET /rest/stats/device  
  https://docs.syncthing.net/rest/stats-device-get.html

- GET /rest/stats/folder  
  https://docs.syncthing.net/rest/stats-folder-get.html

- GET /rest/system/connections  
  https://docs.syncthing.net/rest/system-connections-get.html

- GET /rest/db/status  
  https://docs.syncthing.net/rest/db-status-get.html

- Debug Endpoints  
  https://docs.syncthing.net/v1.21.0/rest/debug.html

- Command Line Operation  
  https://docs.syncthing.net/users/syncthing.html

- Config Endpoints  
  https://docs.syncthing.net/rest/config.html

- GET /rest/system/log  
  https://docs.syncthing.net/rest/system-log-get.html

- GET /rest/system/loglevels  
  https://docs.syncthing.net/rest/system-loglevels-get.html

- GET /rest/events  
  https://docs.syncthing.net/rest/events-get.html

- Understanding Synchronization  
  https://docs.syncthing.net/users/syncing.html

- File Versioning  
  https://docs.syncthing.net/users/versioning.html

- ignoreDelete  
  https://docs.syncthing.net/advanced/folder-ignoredelete.html

- Untrusted Device Encryption  
  https://docs.syncthing.net/specs/untrusted.html

- Introducer Configuration  
  https://docs.syncthing.net/users/introducer.html

- Security Principles  
  https://docs.syncthing.net/users/security.html

- Global Discovery v3  
  https://docs.syncthing.net/specs/globaldisco-v3.html

- Local Discovery Protocol v4  
  https://docs.syncthing.net/specs/localdisco-v4.html

- Syncthing Discovery Server  
  https://docs.syncthing.net/users/stdiscosrv.html

- Understanding Device IDs  
  https://docs.syncthing.net/dev/device-ids.html

- Syncthing Configuration  
  https://docs.syncthing.net/users/config.html

- GET /rest/cluster/pending/devices  
  https://docs.syncthing.net/rest/cluster-pending-devices-get.html

- DELETE /rest/cluster/pending/devices  
  https://docs.syncthing.net/rest/cluster-pending-devices-delete.html

- Syncthing Relay Server  
  https://docs.syncthing.net/users/strelaysrv.html

- FAQ  
  https://docs.syncthing.net/users/faq.html

- Folder Types  
  https://docs.syncthing.net/users/foldertypes.html



- How do I reset my WebUI password?  
  https://help.resilio.com/hc/en-us/articles/205450295-How-do-I-reset-my-WebUI-password

- There’s no Share button in Web UI…  
  https://help.resilio.com/hc/en-us/articles/204753699-There-s-no-Share-button-in-Web-UI

- The GUI Listen Address  
  https://docs.syncthing.net/users/guilisten.html

- Firewall Setup  
  https://docs.syncthing.net/users/firewall.html

- Reverse Proxy Setup  
  https://docs.syncthing.net/users/reverseproxy.html

- Updating Sync to latest version
  https://help.resilio.com/hc/en-us/articles/115001130830-Updating-Sync-to-latest-version

- Updating installation to Resilio Sync v3
  https://help.resilio.com/hc/en-us/articles/31194252837779-Updating-installation-to-Resilio-Sync-v3

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Versions & Releases
  https://docs.syncthing.net/users/releases.html


- Download/upload speed is very slow
  https://help.resilio.com/hc/en-us/articles/205450195-Download-upload-speed-is-very-slow


- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Sync functionality in detail
  https://help.resilio.com/hc/en-us/articles/204754389-Sync-functionality-in-detail

- Folder Types and Management
  https://help.resilio.com/hc/en-us/articles/204762459-Folder-Types-and-Management

- Introducer Configuration
  https://docs.syncthing.net/users/introducer.html

- Untrusted (Encrypted) Devices
  https://docs.syncthing.net/users/untrusted.html

- Disconnecting and Removing Folders
  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders

- How to clear offline devices? (desktop only)
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- If your device is stolen
  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen

- Syncthing Configuration
  https://docs.syncthing.net/users/config.html

- FAQ — Syncthing documentation
  https://docs.syncthing.net/users/faq.html

- Security Principles
  https://docs.syncthing.net/users/security.html

- What's the difference between Standard and Advanced folders?
  https://help.resilio.com/hc/en-us/articles/204754679-What-s-the-difference-between-Standard-and-Advanced-folders

- Sync Share Dialog (Desktop)
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- Sharing a folder locally
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Out of memory
  https://help.resilio.com/hc/en-us/articles/209724663-Out-of-memory

- Agent run out of system notify watchers. Updated files will be uploaded only after periodic folder rescan
  https://help.resilio.com/hc/en-us/articles/360015593120-Agent-run-out-of-system-notify-watchers-Updated-files-will-be-uploaded-only-after-periodic-folder-rescan

- Some internal tasks are taking time to complete
  https://help.resilio.com/hc/en-us/articles/360015586600-Some-internal-tasks-are-taking-time-to-complete

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences


- Selected folder is already added to Sync
  https://help.resilio.com/hc/en-us/articles/209316526-Selected-folder-is-already-added-to-Sync

- Sync doesn't start when opening Link in browser
  https://help.resilio.com/hc/en-us/articles/204753649-Sync-doesn-t-start-when-opening-Link-in-browser

- Selective Sync
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Simple Mode (Android)
  https://help.resilio.com/hc/en-us/articles/205458155-Simple-Mode-Android


- Link structure and flow
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

## Revision note — rev0102

This revision mainly leans again on the same current Resilio sources already in the archive, especially:

- `Sync Share Dialog (Desktop)` for bounded-use links, `Only new peers`, and `All peers`
- `Link structure and flow` for requester identity / approval / certificate-backed access
- `Comprehensive guide to syncing (Desktop-Desktop)` for ordinary-channel link sharing and approval flow


## Revision note — rev0104

This revision mainly leans again on the same current Resilio sources already in the archive, especially:

- `Link structure and flow` for landing-page preview, browser/app handoff, link fragment handling, and approval-time public-key flow
- `Comprehensive guide to syncing (Desktop-Desktop)` for browser launch prompts, remembered external-app handoff, and ordinary-channel delivery of links/keys
- `Sync Share Dialog (Desktop)` as continuing background for portable-link sharing means and link/QR mechanics


## Revision note — rev0105

This revision mainly leans again on the same current Resilio sources already in the archive, especially:

- `Link structure and flow` for wrapper URL, `btsync://` rewrite, fragment-not-sent behavior, and app handoff
- `Sync Share Dialog (Desktop)` for link/QR delivery options and ordinary copy/e-mail sharing means
- `Comprehensive guide to syncing (Desktop-Desktop)` for browser click, manual paste, QR intake, and ordinary-channel delivery of the same share


## Revision note — rev0106

This revision mainly leans again on the same current Resilio sources already in the archive, especially:

- `Link structure and flow` for landing-page basic folder info, protocol rewrite, minimal-link parameters, and fragment-not-sent behavior
- `Sync Share Dialog (Desktop)` for link/QR delivery means and ordinary sharing surfaces
- `Quick guide to syncing` and `Comprehensive guide to syncing (Desktop-Desktop)` for copied-link/key delivery through normal communication channels and later local paste/import flows


## Revision note — rev0107

This revision mainly leans again on the same current Resilio sources already in the archive, especially:

- `Link structure and flow` for the landing-page preview showing only basic folder info, and for the fuller artifact fields that exist beyond that preview
- `Sync Share Dialog (Desktop)` for permission levels, approval-policy options, expiration controls, and use-count controls that live outside the minimal preview
- `Sync functionality in detail` as continuing background that later trust and approval semantics still outlive any one preview surface
