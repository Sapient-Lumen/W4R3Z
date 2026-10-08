# FILE-ATTRIBUTE-BUDGET-01 source trace — rev0029
Focus: **U-199** / peer-supplied file-attribute counts in search, browse, and folder result parsers.
The trace below was produced from the supplied upstream source bundle. It records only compact line evidence; the large source tree is not embedded in this DEV cube.
## github-tag-3.3.10
Commit: `caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026`  
File: `pynicotine/slskmessages.py`
### Shared helper
The parser reads a peer-provided `numattr` and iterates that count without a semantic cap tied to the known retained attribute set.
```python
  444: 
  445:     @classmethod
  446:     def unpack_file_attributes(cls, message, pos):
  447: 
  448:         attrs = {}
  449:         valid_file_attributes = cls.VALID_FILE_ATTRIBUTES
  450: 
  451:         pos, numattr = cls.unpack_uint32(message, pos)
  452: 
  453:         for _ in range(numattr):
  454:             pos, attrnum = cls.unpack_uint32(message, pos)
  455:             pos, attr = cls.unpack_uint32(message, pos)
  456: 
  457:             if attrnum in valid_file_attributes:
  458:                 attrs[attrnum] = attr
  459: 
  460:         return pos, attrs
```
### SharedFileListResponse / browse shares
```python
 3176:             for _ in range(nfiles):
 3177:                 pos, code = self.unpack_uint8(message, pos)
 3178:                 pos, name = self.unpack_string(message, pos)
 3179:                 pos, size = FileListMessage.parse_file_size(message, pos)
 3180:                 pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3181:                 pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3182: 
 3183:                 files.append((code, name, size, ext, attrs))
 3184: 
 3185:             if nfiles > 1:
```
### FileSearchResponse / search results
```python
 3314:         for _ in range(nfiles):
 3315:             pos, code = self.unpack_uint8(message, pos)
 3316:             pos, name = self.unpack_string(message, pos)
 3317:             pos, size = FileListMessage.parse_file_size(message, pos)
 3318:             pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3319:             pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3320: 
 3321:             results.append((code, name.replace("/", "\\"), size, ext, attrs))
 3322: 
 3323:         if nfiles > 1:
```
### FolderContentsResponse / folder contents
```python
 3493:             for _ in range(nfiles):
 3494:                 pos, code = self.unpack_uint8(message, pos)
 3495:                 pos, name = self.unpack_string(message, pos)
 3496:                 pos, size = self.unpack_uint64(message, pos)
 3497:                 pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3498:                 pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3499: 
 3500:                 folders[directory].append((code, name, size, ext, attrs))
 3501: 
 3502:             if nfiles > 1:
```
## github-branch-3.3.x
Commit: `98089ac233aa57786e8dbdc48123f6ac1c4767d8`  
File: `pynicotine/slskmessages.py`
### Shared helper
The parser reads a peer-provided `numattr` and iterates that count without a semantic cap tied to the known retained attribute set.
```python
  444: 
  445:     @classmethod
  446:     def unpack_file_attributes(cls, message, pos):
  447: 
  448:         attrs = {}
  449:         valid_file_attributes = cls.VALID_FILE_ATTRIBUTES
  450: 
  451:         pos, numattr = cls.unpack_uint32(message, pos)
  452: 
  453:         for _ in range(numattr):
  454:             pos, attrnum = cls.unpack_uint32(message, pos)
  455:             pos, attr = cls.unpack_uint32(message, pos)
  456: 
  457:             if attrnum in valid_file_attributes:
  458:                 attrs[attrnum] = attr
  459: 
  460:         return pos, attrs
```
### SharedFileListResponse / browse shares
```python
 3204:             for _ in range(nfiles):
 3205:                 pos, code = self.unpack_uint8(message, pos)
 3206:                 pos, name = self.unpack_string(message, pos)
 3207:                 pos, size = FileListMessage.parse_file_size(message, pos)
 3208:                 pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3209:                 pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3210: 
 3211:                 files.append((code, name, size, ext, attrs))
 3212: 
 3213:             if nfiles > 1:
```
### FileSearchResponse / search results
```python
 3345:         for _ in range(nfiles):
 3346:             pos, code = self.unpack_uint8(message, pos)
 3347:             pos, name = self.unpack_string(message, pos)
 3348:             pos, size = FileListMessage.parse_file_size(message, pos)
 3349:             pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3350:             pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3351: 
 3352:             results.append((code, name.replace("/", "\\"), size, ext, attrs))
 3353: 
 3354:         if nfiles > 1:
```
### FolderContentsResponse / folder contents
```python
 3529:             for _ in range(nfiles):
 3530:                 pos, code = self.unpack_uint8(message, pos)
 3531:                 pos, name = self.unpack_string(message, pos)
 3532:                 pos, size = self.unpack_uint64(message, pos)
 3533:                 pos, ext_len = self.unpack_uint32(message, pos)  # Obsolete, ignore
 3534:                 pos, attrs = FileListMessage.unpack_file_attributes(message, pos + ext_len)
 3535: 
 3536:                 folders[directory].append((code, name, size, ext, attrs))
 3537: 
 3538:             if nfiles > 1:
```
## github-branch-master
Commit: `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`  
File: `pynicotine/slskmessages.py`
### Shared helper
The parser reads a peer-provided `numattr` and iterates that count without a semantic cap tied to the known retained attribute set.
```python
 3223:         return size
 3224: 
 3225:     def unpack_file_attributes(self):
 3226: 
 3227:         attrs = FileAttributes()
 3228:         numattr = self.unpack_uint32()
 3229: 
 3230:         for _ in range(numattr):
 3231:             attrnum = self.unpack_uint32()
 3232:             attr = self.unpack_uint32()
 3233: 
 3234:             if attrnum == FileAttribute.BITRATE:
 3235:                 attrs.bitrate = attr
 3236: 
 3237:             elif attrnum == FileAttribute.LENGTH:
 3238:                 attrs.length = attr
 3239: 
 3240:             elif attrnum == FileAttribute.VBR:
 3241:                 attrs.vbr = attr
 3242: 
 3243:             elif attrnum == FileAttribute.SAMPLE_RATE:
 3244:                 attrs.sample_rate = attr
 3245: 
 3246:             elif attrnum == FileAttribute.BIT_DEPTH:
 3247:                 attrs.bit_depth = attr
 3248: 
 3249:         return attrs
 3250: 
```
### SharedFileListResponse / browse shares
```python
 3377:                 code = self.unpack_uint8()
 3378:                 name = self.unpack_string()
 3379:                 size = self.unpack_file_size()
 3380:                 ext_len = self.unpack_uint32()  # Obsolete, ignore
 3381:                 self._offset += ext_len
 3382:                 attrs = self.unpack_file_attributes()
 3383: 
 3384:                 files.append((code, name, size, ext, attrs))
 3385: 
 3386:             if nfiles > 1:
```
### FileSearchResponse / search results
```python
 3521:             code = self.unpack_uint8()
 3522:             name = self.unpack_string()
 3523:             size = self.unpack_file_size()
 3524:             ext_len = self.unpack_uint32()  # Obsolete, ignore
 3525:             self._offset += ext_len
 3526:             attrs = self.unpack_file_attributes()
 3527: 
 3528:             results.append((code, name.replace("/", "\\"), size, ext, attrs))
 3529: 
 3530:         if nfiles > 1:
```
### FolderContentsResponse / folder contents
```python
 3685:                 code = self.unpack_uint8()
 3686:                 name = self.unpack_string()
 3687:                 size = self.unpack_file_size()
 3688:                 ext_len = self.unpack_uint32()  # Obsolete, ignore
 3689:                 self._offset += ext_len
 3690:                 attrs = self.unpack_file_attributes()
 3691: 
 3692:                 folders[directory].append((code, name, size, ext, attrs))
 3693: 
 3694:             if nfiles > 1:
```
## Current-behavior witness
`maintainer_artifacts/file-attribute-budget-01/test_file_attribute_budget_reproducer.py` creates compact compressed peer messages with eleven filler attributes followed by a valid bitrate attribute. The valid attribute is deliberately placed beyond the known five retained file-attribute budget. All three parsers retain the final bitrate in all archived lanes, proving that the parser walks the peer-supplied attribute count rather than enforcing a semantic cap.
