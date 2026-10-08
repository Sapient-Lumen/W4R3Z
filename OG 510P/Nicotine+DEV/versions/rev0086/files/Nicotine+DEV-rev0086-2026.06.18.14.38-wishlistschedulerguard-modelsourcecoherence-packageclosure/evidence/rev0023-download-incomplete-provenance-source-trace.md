# rev0023 source trace — DOWNLOAD-INCOMPLETE-PROVENANCE-01

This trace uses the external rev0003 source bundle, not embedded source blobs. It records the local code shape used by the maintainer-style witness.

Source lanes:

| lane | commit |
|---|---|
| github-tag-3.3.10 | caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026 |
| github-branch-3.3.x | 98089ac233aa57786e8dbdc48123f6ac1c4767d8 |
| github-branch-master | f4e17d59783dbc48ea31d2e899a681e2dd1ed500 |

## Key source-shape observations

- `get_complete_download_file_path()` treats an existing completed file with matching size as already downloaded.
- `get_incomplete_download_file_path()` derives the incomplete filename prefix from `md5(virtual_path + username)` and then appends a cleaned/truncated basename.
- `_file_transfer_init()` opens the deterministic incomplete path using append/resume mode (`ab+`), logs and continues after advisory lock failure, seeks to end, and uses that offset to decide whether to resume or finish.
- `_move_finished_transfer()` chooses a conflict-avoiding basename before calling `shutil.move()`, but does not revalidate the destination entry immediately before move.

## github-tag-3.3.10

### complete-file shortcut and incomplete filename
```text
687:        basename_limit = max_bytes - len(extension.encode())
688:        basename_no_extension = truncate_string_byte(basename_no_extension, max(0, basename_limit))
690:        if basename_limit < 0:
700:        while os.path.exists(encode_path(os.path.join(download_folder_path, corrected_basename))):
706:    def get_complete_download_file_path(self, username, virtual_path, size, download_folder_path=None):
719:        while os.path.exists(encode_path(download_file_path)):
720:            if os.stat(encode_path(download_file_path)).st_size == size:
731:    def get_incomplete_download_file_path(self, username, virtual_path):
736:        md5sum.update((virtual_path + username).encode())
737:        prefix = f"INCOMPLETE{md5sum.hexdigest()}"
746:        basename_limit = max_bytes - len(prefix) - len(extension.encode())
747:        basename_no_extension = truncate_string_byte(basename_no_extension, max(0, basename_limit))
749:        if basename_limit < 0:
752:        return os.path.join(incomplete_folder_path, prefix + basename_no_extension + extension)
```

### incomplete open/resume/lock behavior
```text
45:from pynicotine.slskmessages import DownloadFile
46:from pynicotine.slskmessages import FileOffset
310:            self._finish_transfer(transfer)
457:    def _finish_transfer(self, transfer):
464:        super()._finish_transfer(transfer)
1152:    def _file_transfer_init(self, msg):
1182:            file_handle = open(encode_path(incomplete_file_path), "ab+")  # pylint: disable=consider-using-with
1187:                    fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
1189:                    log.add(_("Can't get an exclusive lock on file - I/O error: %s"), error)
1196:                file_handle.truncate(0)
1199:            offset = file_handle.seek(0, os.SEEK_END)
1227:            if download.size > offset:
1229:                core.send_message_to_network_thread(DownloadFile(
1232:                core.send_message_to_peer(username, FileOffset(sock, offset))
1235:                self._finish_transfer(download)
1359:            self._finish_transfer(download)
```

### finished move path
```text
427:    def _move_finished_transfer(self, transfer, incomplete_file_path):
432:        download_basename = self.get_download_basename(transfer.virtual_path, download_folder_path, avoid_conflict=True)
439:            shutil.move(incomplete_file_path, encode_path(download_file_path))
```

## github-branch-3.3.x

### complete-file shortcut and incomplete filename
```text
700:        basename_limit = max_bytes - len(extension.encode())
701:        basename_no_extension = truncate_string_byte(basename_no_extension, max(0, basename_limit))
703:        if basename_limit < 0:
713:        while os.path.exists(encode_path(os.path.join(download_folder_path, corrected_basename))):
719:    def get_complete_download_file_path(self, username, virtual_path, size, download_folder_path=None):
731:        while os.path.exists(encode_path(download_file_path)):
732:            if os.stat(encode_path(download_file_path)).st_size == size:
743:    def get_incomplete_download_file_path(self, username, virtual_path):
748:        md5sum.update((virtual_path + username).encode())
749:        prefix = f"INCOMPLETE{md5sum.hexdigest()}"
757:        basename_limit = max_bytes - len(prefix) - len(extension.encode())
758:        basename_no_extension = truncate_string_byte(basename_no_extension, max(0, basename_limit))
760:        if basename_limit < 0:
763:        return os.path.join(incomplete_folder_path, prefix + basename_no_extension + extension)
```

### incomplete open/resume/lock behavior
```text
46:from pynicotine.slskmessages import DownloadFile
47:from pynicotine.slskmessages import FileOffset
311:            self._finish_transfer(transfer)
458:    def _finish_transfer(self, transfer):
465:        super()._finish_transfer(transfer)
1163:    def _file_transfer_init(self, msg):
1195:            file_handle = open(encode_path(incomplete_file_path), "ab+")  # pylint: disable=consider-using-with
1200:                    fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
1202:                    log.add(_("Can't get an exclusive lock on file - I/O error: %s"), error)
1209:                file_handle.truncate(0)
1212:            offset = file_handle.seek(0, os.SEEK_END)
1240:            if download.size > offset:
1242:                core.send_message_to_network_thread(DownloadFile(
1245:                core.send_message_to_peer(username, FileOffset(sock, offset))
1249:                self._finish_transfer(download)
1373:            self._finish_transfer(download)
```

### finished move path
```text
428:    def _move_finished_transfer(self, transfer, incomplete_file_path):
433:        download_basename = self.get_download_basename(transfer.virtual_path, download_folder_path, avoid_conflict=True)
440:            shutil.move(incomplete_file_path, encode_path(download_file_path))
```

## github-branch-master

### complete-file shortcut and incomplete filename
```text
675:        basename_limit = max_bytes - len(extension.encode())
676:        basename_no_extension = truncate_string_byte(basename_no_extension, max(0, basename_limit))
678:        if basename_limit < 0:
688:        while os.path.exists(encode_path(os.path.join(download_folder_path, corrected_basename))):
694:    def get_complete_download_file_path(self, username, virtual_path, size, download_folder_path=None):
706:        while os.path.exists(encode_path(download_file_path)):
707:            if os.stat(encode_path(download_file_path)).st_size == size:
718:    def get_incomplete_download_file_path(self, username, virtual_path):
723:        md5sum.update((virtual_path + username).encode())
724:        prefix = f"INCOMPLETE{md5sum.hexdigest()}"
732:        basename_limit = max_bytes - len(prefix) - len(extension.encode())
733:        basename_no_extension = truncate_string_byte(basename_no_extension, max(0, basename_limit))
735:        if basename_limit < 0:
738:        return os.path.join(incomplete_folder_path, prefix + basename_no_extension + extension)
```

### incomplete open/resume/lock behavior
```text
32:from pynicotine.slskmessages import DownloadFile
33:from pynicotine.slskmessages import FileOffset
297:            self._finish_transfer(transfer)
444:    def _finish_transfer(self, transfer):
451:        super()._finish_transfer(transfer)
1134:    def _file_transfer_init(self, msg):
1166:            file_handle = open(encode_path(incomplete_file_path), "ab+")  # pylint: disable=consider-using-with
1171:                    fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
1173:                    log.add(_("Can't get an exclusive lock on file - I/O error: %s"), error)
1180:                file_handle.truncate(0)
1183:            offset = file_handle.seek(0, os.SEEK_END)
1211:            if download.size > offset:
1213:                core.send_message_to_network_thread(DownloadFile(
1216:                core.send_message_to_peer(username, FileOffset(sock, offset))
1220:                self._finish_transfer(download)
1344:            self._finish_transfer(download)
```

### finished move path
```text
414:    def _move_finished_transfer(self, transfer, incomplete_file_path):
419:        download_basename = self.get_download_basename(transfer.virtual_path, download_folder_path, avoid_conflict=True)
426:            shutil.move(incomplete_file_path, encode_path(download_file_path))
```

