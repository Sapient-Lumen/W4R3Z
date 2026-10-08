# rev0022 source trace — TRANSFER-COMPLETE-LIFETIME-01 / U-269

Local source trace against archived rev0003 source lanes. The trace records why the reproducer distinguishes silent post-completion sockets from sockets that keep sending post-completion bytes.

## github-tag-3.3.10

### _process_upload completion only emits progress and returns True

`pynicotine/slskproto.py:1973-2028`


```python
1973:     def _process_upload(self, conn, num_sent_bytes, current_time):
1974: 
1975:         file_upload = self._file_upload_msgs[conn]
1976: 
1977:         if file_upload.offset is None:
1978:             return True
1979: 
1980:         out_buffer = conn.out_buffer
1981:         out_buffer_len = len(out_buffer)
1982:         file_upload.sentbytes += num_sent_bytes
1983:         total_read_bytes = file_upload.offset + file_upload.sentbytes + out_buffer_len
1984:         size = file_upload.size
1985: 
1986:         try:
1987:             if total_read_bytes < size:
1988:                 num_bytes_to_read = int(
1989:                     (max(4096, num_sent_bytes * 1.25) / max(1, current_time - conn.last_active))
1990:                     - out_buffer_len
1991:                 )
1992:                 if num_bytes_to_read > 0:
1993:                     out_buffer += file_upload.file.read(num_bytes_to_read)
1994:                     self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
1995: 
1996:         except (OSError, ValueError) as error:
1997:             events.emit_main_thread(
1998:                 "upload-file-error",
1999:                 username=conn.init.target_user, token=file_upload.token, error=error
2000:             )
2001:             return False  # Close the connection
2002: 
2003:         file_upload.speed += num_sent_bytes
2004:         self._total_upload_bandwidth += num_sent_bytes
2005: 
2006:         # Upload finished
2007:         if file_upload.offset + file_upload.sentbytes == size:
2008:             events.emit_main_thread(
2009:                 "file-upload-progress",
2010:                 username=conn.init.target_user, token=file_upload.token,
2011:                 offset=file_upload.offset, bytes_sent=file_upload.sentbytes
2012:             )
2013:         return True
2014: 
2015:     def _process_file_input(self, conn):
2016:         """Reads file messages from the input buffer of a 'F' connection."""
2017: 
2018:         in_buffer = conn.in_buffer
2019:         idx = 0
2020: 
2021:         if conn not in self._file_init_msgs:
2022:             idx = self._process_file_init_message(conn, in_buffer)
2023: 
2024:         elif conn in self._file_upload_msgs:
2025:             idx = self._process_file_offset_message(conn, in_buffer)
2026: 
2027:         if idx:
2028:             del in_buffer[:idx]
```

### _process_file_offset_message discards later F input once offset is set

`pynicotine/slskproto.py:1884-1916`


```python
1884:     def _process_file_offset_message(self, conn, in_buffer):
1885: 
1886:         file_upload = self._file_upload_msgs[conn]
1887: 
1888:         if file_upload.offset is not None:
1889:             # No more incoming messages on this connection after receiving the
1890:             # file offset. If peer sends something anyway, clear it.
1891:             return len(in_buffer)
1892: 
1893:         msg_size = idx = 8
1894:         msg = self._unpack_network_message(
1895:             FileOffset,
1896:             memoryview(in_buffer)[:msg_size],
1897:             msg_size,
1898:             conn_type="file",
1899:             sock=conn.sock,
1900:             username=conn.init.target_user
1901:         )
1902: 
1903:         if msg is None or msg.offset is None:
1904:             return idx
1905: 
1906:         file_upload.offset = msg.offset
1907: 
1908:         events.emit_main_thread(
1909:             "file-upload-progress",
1910:             username=conn.init.target_user, token=file_upload.token,
1911:             offset=file_upload.offset, bytes_sent=file_upload.sentbytes
1912:         )
1913: 
1914:         try:
1915:             file_upload.file.seek(msg.offset)
1916:             self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
```

### _read_data refreshes last_active on any nonempty recv

`pynicotine/slskproto.py:2615-2655`


```python
2615:     def _read_data(self, conn, current_time):
2616: 
2617:         sock = conn.sock
2618:         current_recv_size = conn.recv_size
2619:         is_file_download = (conn in self._file_download_msgs)
2620:         use_download_limit = (self._download_limit_split and is_file_download)
2621: 
2622:         if use_download_limit:
2623:             download_limit = (self._download_limit_split - self._conns_downloaded[conn])
2624: 
2625:             if current_recv_size > download_limit:  # pylint: disable=consider-using-min-builtin
2626:                 current_recv_size = download_limit
2627: 
2628:         data = sock.recv(current_recv_size)
2629:         data_len = len(data)
2630: 
2631:         if not data:
2632:             return False  # Close the connection
2633: 
2634:         # An intermediate buffer is useless when downloading a file. Write to the
2635:         # file immediately, and let the OS handle buffering when necessary.
2636:         if not is_file_download:
2637:             conn.in_buffer += data
2638: 
2639:         elif not self._process_download(conn, data, data_len):
2640:             return False  # Close the connection
2641: 
2642:         if use_download_limit:
2643:             self._conns_downloaded[conn] += data_len
2644: 
2645:         # Grow or shrink recv buffer depending on how much data we're receiving
2646:         elif data_len >= current_recv_size // 2:
2647:             conn.recv_size *= 2
2648: 
2649:         elif data_len <= current_recv_size // 6:
2650:             conn.recv_size //= 2
2651: 
2652:         conn.last_active = current_time
2653:         return True
2654: 
2655:     def _write_data(self, conn, current_time):
```

### _check_connections idle cleanup gate

`pynicotine/slskproto.py:1026-1074`


```python
1026:     def _check_connections(self, current_time):
1029:         inactive_conns = set()
1034:                 if (current_time - conn.last_active) > self.IN_PROGRESS_STALE_AFTER:
1037:             elif self._is_connection_inactive(conn, current_time, num_sockets):
1038:                 inactive_conns.add(conn)
1050:             elif conn in self._file_upload_msgs:
1051:                 file_upload = self._file_upload_msgs[conn]
1054:                     "file-upload-progress",
1055:                     username=conn.init.target_user, token=file_upload.token,
1056:                     offset=file_upload.offset, bytes_sent=file_upload.sentbytes,
1057:                     speed=file_upload.speed
1059:                 file_upload.speed = 0
1061:         if inactive_conns:
1062:             for conn in inactive_conns:
1063:                 self._close_connection(conn)
1065:             inactive_conns.clear()
1070:                 self._close_connection(conn)
```

### _close_connection removes file upload only on close

`pynicotine/slskproto.py:900-988`


```python
900:     def _close_connection(self, conn):
952:                 timed_out = (time.monotonic() - conn.last_active) > self.CONNECTION_MAX_IDLE
954:                     "file-connection-closed", username=username, token=file_init.token,
967:         elif conn in self._file_upload_msgs:
968:             del self._file_upload_msgs[conn]
969:             self._total_uploads -= 1
971:             if not self._total_uploads:
```



## github-branch-3.3.x

### _process_upload completion only emits progress and returns True

`pynicotine/slskproto.py:2058-2113`


```python
2058:     def _process_upload(self, conn, num_sent_bytes, current_time):
2059: 
2060:         file_upload = self._file_upload_msgs[conn]
2061: 
2062:         if file_upload.offset is None:
2063:             return True
2064: 
2065:         out_buffer = conn.out_buffer
2066:         out_buffer_len = len(out_buffer)
2067:         file_upload.sentbytes += num_sent_bytes
2068:         total_read_bytes = file_upload.offset + file_upload.sentbytes + out_buffer_len
2069:         size = file_upload.size
2070: 
2071:         try:
2072:             if total_read_bytes < size:
2073:                 num_bytes_to_read = int(
2074:                     (max(4096, num_sent_bytes * 1.25) / max(1, current_time - conn.last_active))
2075:                     - out_buffer_len
2076:                 )
2077:                 if num_bytes_to_read > 0:
2078:                     out_buffer += file_upload.file.read(num_bytes_to_read)
2079:                     self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
2080: 
2081:         except (OSError, ValueError) as error:
2082:             events.emit_main_thread(
2083:                 "upload-file-error",
2084:                 username=conn.init.target_user, token=file_upload.token, error=error
2085:             )
2086:             return False  # Close the connection
2087: 
2088:         file_upload.speed += num_sent_bytes
2089:         self._total_upload_bandwidth += num_sent_bytes
2090: 
2091:         # Upload finished
2092:         if file_upload.offset + file_upload.sentbytes == size:
2093:             events.emit_main_thread(
2094:                 "file-upload-progress",
2095:                 username=conn.init.target_user, token=file_upload.token,
2096:                 offset=file_upload.offset, bytes_sent=file_upload.sentbytes
2097:             )
2098:         return True
2099: 
2100:     def _process_file_input(self, conn):
2101:         """Reads file messages from the input buffer of a 'F' connection."""
2102: 
2103:         in_buffer = conn.in_buffer
2104:         idx = 0
2105: 
2106:         if conn not in self._file_init_msgs:
2107:             idx = self._process_file_init_message(conn, in_buffer)
2108: 
2109:         elif conn in self._file_upload_msgs:
2110:             idx = self._process_file_offset_message(conn, in_buffer)
2111: 
2112:         if idx:
2113:             del in_buffer[:idx]
```

### _process_file_offset_message discards later F input once offset is set

`pynicotine/slskproto.py:1969-2001`


```python
1969:     def _process_file_offset_message(self, conn, in_buffer):
1970: 
1971:         file_upload = self._file_upload_msgs[conn]
1972: 
1973:         if file_upload.offset is not None:
1974:             # No more incoming messages on this connection after receiving the
1975:             # file offset. If peer sends something anyway, clear it.
1976:             return len(in_buffer)
1977: 
1978:         msg_size = idx = 8
1979:         msg = self._unpack_network_message(
1980:             FileOffset,
1981:             memoryview(in_buffer)[:msg_size],
1982:             msg_size,
1983:             conn_type="file",
1984:             sock=conn.sock,
1985:             username=conn.init.target_user
1986:         )
1987: 
1988:         if msg is None or msg.offset is None:
1989:             return idx
1990: 
1991:         file_upload.offset = msg.offset
1992: 
1993:         events.emit_main_thread(
1994:             "file-upload-progress",
1995:             username=conn.init.target_user, token=file_upload.token,
1996:             offset=file_upload.offset, bytes_sent=file_upload.sentbytes
1997:         )
1998: 
1999:         try:
2000:             file_upload.file.seek(msg.offset)
2001:             self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
```

### _read_data refreshes last_active on any nonempty recv

`pynicotine/slskproto.py:2674-2714`


```python
2674:     def _read_data(self, conn, current_time):
2675: 
2676:         sock = conn.sock
2677:         current_recv_size = conn.recv_size
2678:         is_file_download = (conn in self._file_download_msgs)
2679:         use_download_limit = (self._download_limit_split and is_file_download)
2680: 
2681:         if use_download_limit:
2682:             download_limit = (self._download_limit_split - self._conns_downloaded[conn])
2683: 
2684:             if current_recv_size > download_limit:  # pylint: disable=consider-using-min-builtin
2685:                 current_recv_size = download_limit
2686: 
2687:         data = sock.recv(current_recv_size)
2688:         data_len = len(data)
2689: 
2690:         if not data:
2691:             return False  # Close the connection
2692: 
2693:         # An intermediate buffer is useless when downloading a file. Write to the
2694:         # file immediately, and let the OS handle buffering when necessary.
2695:         if not is_file_download:
2696:             conn.in_buffer += data
2697: 
2698:         elif not self._process_download(conn, data, data_len):
2699:             return False  # Close the connection
2700: 
2701:         if use_download_limit:
2702:             self._conns_downloaded[conn] += data_len
2703: 
2704:         # Grow or shrink recv buffer depending on how much data we're receiving
2705:         elif data_len >= current_recv_size // 2:
2706:             conn.recv_size *= 2
2707: 
2708:         elif data_len <= current_recv_size // 6:
2709:             conn.recv_size //= 2
2710: 
2711:         conn.last_active = current_time
2712:         return True
2713: 
2714:     def _write_data(self, conn, current_time):
```

### _check_connections idle cleanup gate

`pynicotine/slskproto.py:1082-1130`


```python
1082:     def _check_connections(self, current_time):
1085:         inactive_conns = set()
1090:                 if (current_time - conn.last_active) > self.IN_PROGRESS_STALE_AFTER:
1093:             elif self._is_connection_inactive(conn, current_time, num_sockets):
1094:                 inactive_conns.add(conn)
1106:             elif conn in self._file_upload_msgs:
1107:                 file_upload = self._file_upload_msgs[conn]
1110:                     "file-upload-progress",
1111:                     username=conn.init.target_user, token=file_upload.token,
1112:                     offset=file_upload.offset, bytes_sent=file_upload.sentbytes,
1113:                     speed=file_upload.speed
1115:                 file_upload.speed = 0
1117:         if inactive_conns:
1118:             for conn in inactive_conns:
1119:                 self._close_connection(conn)
1121:             inactive_conns.clear()
1126:                 self._close_connection(conn)
```

### _close_connection removes file upload only on close

`pynicotine/slskproto.py:956-1044`


```python
956:     def _close_connection(self, conn):
1008:                 timed_out = (time.monotonic() - conn.last_active) > self.CONNECTION_MAX_IDLE
1010:                     "file-connection-closed", username=username, token=file_init.token,
1023:         elif conn in self._file_upload_msgs:
1024:             del self._file_upload_msgs[conn]
1025:             self._total_uploads -= 1
1027:             if not self._total_uploads:
```



## github-branch-master

### _process_upload completion only emits progress and returns True

`pynicotine/slskproto.py:2095-2150`


```python
2095:     def _process_upload(self, conn, num_sent_bytes, current_time):
2096: 
2097:         file_upload = self._file_upload_msgs[conn]
2098: 
2099:         if file_upload.offset is None:
2100:             return True
2101: 
2102:         out_buffer = conn.out_buffer
2103:         out_buffer_len = len(out_buffer)
2104:         file_upload.sentbytes += num_sent_bytes
2105:         total_read_bytes = file_upload.offset + file_upload.sentbytes + out_buffer_len
2106:         size = file_upload.size
2107: 
2108:         try:
2109:             if total_read_bytes < size:
2110:                 num_bytes_to_read = int(
2111:                     (max(4096, num_sent_bytes * 1.25) / max(1, current_time - conn.last_active))
2112:                     - out_buffer_len
2113:                 )
2114:                 if num_bytes_to_read > 0:
2115:                     out_buffer += file_upload.file.read(num_bytes_to_read)
2116:                     self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
2117: 
2118:         except (OSError, ValueError) as error:
2119:             events.emit_main_thread(
2120:                 "upload-file-error",
2121:                 username=conn.init.target_user, token=file_upload.token, error=error
2122:             )
2123:             return False  # Close the connection
2124: 
2125:         file_upload.speed += num_sent_bytes
2126:         self._total_upload_bandwidth += num_sent_bytes
2127: 
2128:         # Upload finished
2129:         if file_upload.offset + file_upload.sentbytes == size:
2130:             events.emit_main_thread(
2131:                 "file-upload-progress",
2132:                 username=conn.init.target_user, token=file_upload.token,
2133:                 offset=file_upload.offset, bytes_sent=file_upload.sentbytes
2134:             )
2135:         return True
2136: 
2137:     def _process_file_input(self, conn):
2138:         """Reads file messages from the input buffer of a 'F' connection."""
2139: 
2140:         in_buffer = conn.in_buffer
2141:         idx = 0
2142: 
2143:         if conn not in self._file_init_msgs:
2144:             idx = self._process_file_init_message(conn, in_buffer)
2145: 
2146:         elif conn in self._file_upload_msgs:
2147:             idx = self._process_file_offset_message(conn, in_buffer)
2148: 
2149:         if idx:
2150:             del in_buffer[:idx]
```

### _process_file_offset_message discards later F input once offset is set

`pynicotine/slskproto.py:2011-2043`


```python
2011:     def _process_file_offset_message(self, conn, in_buffer):
2012: 
2013:         file_upload = self._file_upload_msgs[conn]
2014: 
2015:         if file_upload.offset is not None:
2016:             # No more incoming messages on this connection after receiving the
2017:             # file offset. If peer sends something anyway, clear it.
2018:             return len(in_buffer)
2019: 
2020:         msg_size = idx = 8
2021:         msg = self._unpack_network_message(
2022:             FileOffset,
2023:             memoryview(in_buffer)[:msg_size],
2024:             msg_size,
2025:             conn_type="file",
2026:             sock=conn.sock,
2027:             username=conn.init.target_user
2028:         )
2029: 
2030:         if msg is None or msg.offset is None:
2031:             return idx
2032: 
2033:         file_upload.offset = msg.offset
2034: 
2035:         events.emit_main_thread(
2036:             "file-upload-progress",
2037:             username=conn.init.target_user, token=file_upload.token,
2038:             offset=file_upload.offset, bytes_sent=file_upload.sentbytes
2039:         )
2040: 
2041:         try:
2042:             file_upload.file.seek(msg.offset)
2043:             self._modify_connection_events(conn, selectors.EVENT_READ | selectors.EVENT_WRITE)
```

### _read_data refreshes last_active on any nonempty recv

`pynicotine/slskproto.py:2798-2838`


```python
2798:     def _read_data(self, conn, current_time):
2799: 
2800:         sock = conn.sock
2801:         current_recv_size = conn.recv_size
2802:         is_file_download = (conn in self._file_download_msgs)
2803:         use_download_limit = (self._download_limit_split and is_file_download)
2804: 
2805:         if use_download_limit:
2806:             download_limit = (self._download_limit_split - self._conns_downloaded[conn])
2807: 
2808:             if current_recv_size > download_limit:  # pylint: disable=consider-using-min-builtin
2809:                 current_recv_size = download_limit
2810: 
2811:         data = sock.recv(current_recv_size)
2812:         data_len = len(data)
2813: 
2814:         if not data:
2815:             return False  # Close the connection
2816: 
2817:         # An intermediate buffer is useless when downloading a file. Write to the
2818:         # file immediately, and let the OS handle buffering when necessary.
2819:         if not is_file_download:
2820:             conn.in_buffer += data
2821: 
2822:         elif not self._process_download(conn, data, data_len):
2823:             return False  # Close the connection
2824: 
2825:         if use_download_limit:
2826:             self._conns_downloaded[conn] += data_len
2827: 
2828:         # Grow or shrink recv buffer depending on how much data we're receiving
2829:         elif data_len >= current_recv_size // 2:
2830:             conn.recv_size *= 2
2831: 
2832:         elif data_len <= current_recv_size // 6:
2833:             conn.recv_size //= 2
2834: 
2835:         conn.last_active = current_time
2836:         return True
2837: 
2838:     def _write_data(self, conn, current_time):
```

### _check_connections idle cleanup gate

`pynicotine/slskproto.py:1110-1158`


```python
1110:     def _check_connections(self, current_time):
1113:         inactive_conns = set()
1118:                 if (current_time - conn.last_active) > self.IN_PROGRESS_STALE_AFTER:
1121:             elif self._is_connection_inactive(conn, current_time, num_sockets):
1122:                 inactive_conns.add(conn)
1134:             elif conn in self._file_upload_msgs:
1135:                 file_upload = self._file_upload_msgs[conn]
1138:                     "file-upload-progress",
1139:                     username=conn.init.target_user, token=file_upload.token,
1140:                     offset=file_upload.offset, bytes_sent=file_upload.sentbytes,
1141:                     speed=file_upload.speed
1143:                 file_upload.speed = 0
1145:         if inactive_conns:
1146:             for conn in inactive_conns:
1147:                 self._close_connection(conn)
1149:             inactive_conns.clear()
1154:                 self._close_connection(conn)
```

### _close_connection removes file upload only on close

`pynicotine/slskproto.py:974-1062`


```python
974:     def _close_connection(self, conn):
1036:                 timed_out = (time.monotonic() - conn.last_active) > self.CONNECTION_MAX_IDLE
1038:                     "file-connection-closed", username=username, token=file_init.token,
1051:         elif conn in self._file_upload_msgs:
1052:             del self._file_upload_msgs[conn]
1053:             self._total_uploads -= 1
1055:             if not self._total_uploads:
```


