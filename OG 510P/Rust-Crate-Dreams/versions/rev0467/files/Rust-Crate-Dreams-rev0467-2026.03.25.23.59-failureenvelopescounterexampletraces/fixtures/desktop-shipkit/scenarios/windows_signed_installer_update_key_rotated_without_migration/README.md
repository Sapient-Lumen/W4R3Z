# windows_signed_installer_update_key_rotated_without_migration

This scenario exists to keep **signed installer output** separate from **updater key continuity**.

A release pipeline can successfully sign a Windows installer and still break the update path if the updater signing identity rotates without a migration story.
