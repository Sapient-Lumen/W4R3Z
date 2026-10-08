# rev0021 SHARE-SCAN-CACHE-01 source trace

## github-tag-3.3.10

### shares.py:563

```python
  560:                             self.mtimes[path] = file_mtime = file_stat.st_mtime
  561:                             virtual_file_path = f"{virtual_folder_path}\\{basename}"
  562: 
  563:                             if not self.rebuild and file_mtime == old_mtimes.get(path) and path in old_files:
  564:                                 full_path_file_data = old_files[path]
  565:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  566:                             else:
```

### shares.py:564

```python
  561:                             virtual_file_path = f"{virtual_folder_path}\\{basename}"
  562: 
  563:                             if not self.rebuild and file_mtime == old_mtimes.get(path) and path in old_files:
  564:                                 full_path_file_data = old_files[path]
  565:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  566:                             else:
  567:                                 full_path_file_data = self.get_file_info(virtual_file_path, path, file_stat)
```

### shares.py:567

```python
  564:                                 full_path_file_data = old_files[path]
  565:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  566:                             else:
  567:                                 full_path_file_data = self.get_file_info(virtual_file_path, path, file_stat)
  568: 
  569:                             basename_file_data = full_path_file_data[:]
  570:                             basename_file_data[0] = basename
```

### shares.py:617

```python
  614:         quality = None
  615:         duration = None
  616:         encoded_file_path = encode_path(file_path)
  617:         size = file_stat.st_size
  618: 
  619:         # We skip metadata scanning of files without meaningful content
  620:         if size > 128:
```

## github-branch-3.3.x

### shares.py:569

```python
  566:                             self.mtimes[path] = file_mtime = file_stat.st_mtime
  567:                             virtual_file_path = f"{virtual_folder_path}\\{basename}"
  568: 
  569:                             if not self.rebuild and file_mtime == old_mtimes.get(path) and path in old_files:
  570:                                 full_path_file_data = old_files[path]
  571:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  572:                             else:
```

### shares.py:570

```python
  567:                             virtual_file_path = f"{virtual_folder_path}\\{basename}"
  568: 
  569:                             if not self.rebuild and file_mtime == old_mtimes.get(path) and path in old_files:
  570:                                 full_path_file_data = old_files[path]
  571:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  572:                             else:
  573:                                 full_path_file_data = self.get_file_info(virtual_file_path, path, file_stat)
```

### shares.py:573

```python
  570:                                 full_path_file_data = old_files[path]
  571:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  572:                             else:
  573:                                 full_path_file_data = self.get_file_info(virtual_file_path, path, file_stat)
  574: 
  575:                             basename_file_data = full_path_file_data[:]
  576:                             basename_file_data[0] = basename
```

### shares.py:624

```python
  621:         quality = None
  622:         duration = None
  623:         encoded_file_path = encode_path(file_path)
  624:         size = file_stat.st_size
  625: 
  626:         # We skip metadata scanning of files without meaningful content
  627:         if size > 128:
```

## github-branch-master

### shares.py:616

```python
  613:                             file_stat = entry.stat()
  614:                             self.mtimes[path] = file_mtime = file_stat.st_mtime
  615: 
  616:                             if not self.rebuild and file_mtime == old_mtimes.get(path) and path in old_files:
  617:                                 full_path_file_data = old_files[path]
  618:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  619:                             else:
```

### shares.py:617

```python
  614:                             self.mtimes[path] = file_mtime = file_stat.st_mtime
  615: 
  616:                             if not self.rebuild and file_mtime == old_mtimes.get(path) and path in old_files:
  617:                                 full_path_file_data = old_files[path]
  618:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  619:                             else:
  620:                                 full_path_file_data = self.get_file_info(virtual_file_path, path, file_stat)
```

### shares.py:620

```python
  617:                                 full_path_file_data = old_files[path]
  618:                                 full_path_file_data[0] = virtual_file_path  # Virtual name might have changed
  619:                             else:
  620:                                 full_path_file_data = self.get_file_info(virtual_file_path, path, file_stat)
  621: 
  622:                             basename_file_data = full_path_file_data[:]
  623:                             basename_file_data[0] = basename_escaped
```

### shares.py:681

```python
  678:         tag = None
  679:         quality = None
  680:         duration = None
  681:         size = file_stat.st_size
  682: 
  683:         # We skip metadata scanning of files without meaningful content
  684:         if size > 128:
```
