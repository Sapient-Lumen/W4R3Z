# TRANSFER-EOF-01 / U-251 source trace — rev0019

## github-tag-3.3.10

### `_process_upload()`

```text
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
```

### `_check_connections()` idle closure path

```text
 1026:     def _check_connections(self, current_time):
 1027: 
 1028:         num_sockets = self._num_sockets
 1029:         inactive_conns = set()
 1030:         stale_conns = set()
 1031: 
 1032:         for conn in self._conns.values():
 1033:             if not conn.is_established:
 1034:                 if (current_time - conn.last_active) > self.IN_PROGRESS_STALE_AFTER:
 1035:                     stale_conns.add(conn)
 1036: 
 1037:             elif self._is_connection_inactive(conn, current_time, num_sockets):
 1038:                 inactive_conns.add(conn)
 1039: 
 1040:             elif conn in self._file_download_msgs:
 1041:                 file_download = self._file_download_msgs[conn]
 1042: 
 1043:                 events.emit_main_thread(
 1044:                     "file-download-progress",
 1045:                     username=conn.init.target_user, token=file_download.token,
 1046:                     bytes_left=file_download.leftbytes, speed=file_download.speed
 1047:                 )
 1048:                 file_download.speed = 0
 1049: 
 1050:             elif conn in self._file_upload_msgs:
 1051:                 file_upload = self._file_upload_msgs[conn]
 1052: 
 1053:                 events.emit_main_thread(
 1054:                     "file-upload-progress",
 1055:                     username=conn.init.target_user, token=file_upload.token,
 1056:                     offset=file_upload.offset, bytes_sent=file_upload.sentbytes,
 1057:                     speed=file_upload.speed
 1058:                 )
 1059:                 file_upload.speed = 0
 1060: 
 1061:         if inactive_conns:
 1062:             for conn in inactive_conns:
 1063:                 self._close_connection(conn)
 1064: 
 1065:             inactive_conns.clear()
 1066: 
 1067:         if stale_conns:
 1068:             for conn in stale_conns:
 1069:                 self._connect_error(self.ERROR_TIMED_OUT, conn)
 1070:                 self._close_connection(conn)
 1071: 
```

### `_close_connection()` file-connection close event

```text
  900:     def _close_connection(self, conn):
  901: 
  902:         if conn is None:
  903:             return
  904: 
  905:         sock = conn.sock
  906:         del self._conns[sock]
  907: 
  908:         if conn is self._server_conn:
  909:             # Disconnecting from server, clean up connections and queue
  910:             self._server_disconnect()
  911: 
  912:         self._selector.unregister(sock)
  913:         self._close_socket(sock)
  914:         self._num_sockets -= 1
  915: 
  916:         conn.sock = None
  917:         conn.in_buffer.clear()
  918:         conn.out_buffer.clear()
  919: 
  920:         if conn.__class__ is not PeerConnection:
  921:             return
  922: 
  923:         init = conn.init
  924: 
  925:         if init is None:
  926:             # No peer init message present, nothing to do
  927:             return
  928: 
  929:         conn_type = init.conn_type
  930:         username = init.target_user
  931:         addr = conn.addr
  932:         is_connection_replaced = (init.sock is not sock)
  933: 
  934:         log.add_conn("Removed connection of type %s to user %s, address %s", (conn_type, username, addr))
  935: 
  936:         if not is_connection_replaced:
  937:             init.sock = None
  938: 
  939:         if conn_type == ConnectionType.DISTRIBUTED:
  940:             child_conn = self._child_peers.get(username)
  941: 
  942:             if child_conn is conn:
  943:                 self._remove_child_peer_connection(username)
  944: 
  945:             elif conn is self._parent_conn:
  946:                 self._send_have_no_parent()
  947: 
  948:         elif conn in self._file_init_msgs:
  949:             file_init = self._file_init_msgs.pop(conn)
  950: 
  951:             if self._should_process_queue:
  952:                 timed_out = (time.monotonic() - conn.last_active) > self.CONNECTION_MAX_IDLE
  953:                 events.emit_main_thread(
  954:                     "file-connection-closed", username=username, token=file_init.token,
  955:                     sock=sock, timed_out=timed_out
  956:                 )
  957: 
  958:         if conn in self._file_download_msgs:
  959:             del self._file_download_msgs[conn]
  960:             self._total_downloads -= 1
  961: 
  962:             if not self._total_downloads:
  963:                 self._total_download_bandwidth = 0
  964: 
  965:             self._calc_download_limit()
  966: 
  967:         elif conn in self._file_upload_msgs:
  968:             del self._file_upload_msgs[conn]
  969:             self._total_uploads -= 1
  970: 
  971:             if not self._total_uploads:
  972:                 self._total_upload_bandwidth = 0
  973: 
  974:             self._calc_upload_limit_function()
  975: 
  976:         init_key = username + conn_type
  977: 
  978:         if init_key not in self._username_init_msgs:
  979:             return
  980: 
```

## github-branch-3.3.x

### `_process_upload()`

```text
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
```

### `_check_connections()` idle closure path

```text
 1082:     def _check_connections(self, current_time):
 1083: 
 1084:         num_sockets = self._num_sockets
 1085:         inactive_conns = set()
 1086:         stale_conns = set()
 1087: 
 1088:         for conn in self._conns.values():
 1089:             if not conn.is_established:
 1090:                 if (current_time - conn.last_active) > self.IN_PROGRESS_STALE_AFTER:
 1091:                     stale_conns.add(conn)
 1092: 
 1093:             elif self._is_connection_inactive(conn, current_time, num_sockets):
 1094:                 inactive_conns.add(conn)
 1095: 
 1096:             elif conn in self._file_download_msgs:
 1097:                 file_download = self._file_download_msgs[conn]
 1098: 
 1099:                 events.emit_main_thread(
 1100:                     "file-download-progress",
 1101:                     username=conn.init.target_user, token=file_download.token,
 1102:                     bytes_left=file_download.leftbytes, speed=file_download.speed
 1103:                 )
 1104:                 file_download.speed = 0
 1105: 
 1106:             elif conn in self._file_upload_msgs:
 1107:                 file_upload = self._file_upload_msgs[conn]
 1108: 
 1109:                 events.emit_main_thread(
 1110:                     "file-upload-progress",
 1111:                     username=conn.init.target_user, token=file_upload.token,
 1112:                     offset=file_upload.offset, bytes_sent=file_upload.sentbytes,
 1113:                     speed=file_upload.speed
 1114:                 )
 1115:                 file_upload.speed = 0
 1116: 
 1117:         if inactive_conns:
 1118:             for conn in inactive_conns:
 1119:                 self._close_connection(conn)
 1120: 
 1121:             inactive_conns.clear()
 1122: 
 1123:         if stale_conns:
 1124:             for conn in stale_conns:
 1125:                 self._connect_error(self.ERROR_TIMED_OUT, conn)
 1126:                 self._close_connection(conn)
 1127: 
```

### `_close_connection()` file-connection close event

```text
  956:     def _close_connection(self, conn):
  957: 
  958:         if conn is None:
  959:             return
  960: 
  961:         sock = conn.sock
  962:         del self._conns[sock]
  963: 
  964:         if conn is self._server_conn:
  965:             # Disconnecting from server, clean up connections and queue
  966:             self._server_disconnect()
  967: 
  968:         self._selector.unregister(sock)
  969:         self._close_socket(sock)
  970:         self._num_sockets -= 1
  971: 
  972:         conn.sock = None
  973:         conn.in_buffer.clear()
  974:         conn.out_buffer.clear()
  975: 
  976:         if conn.__class__ is not PeerConnection:
  977:             return
  978: 
  979:         init = conn.init
  980: 
  981:         if init is None:
  982:             # No peer init message present, nothing to do
  983:             return
  984: 
  985:         conn_type = init.conn_type
  986:         username = init.target_user
  987:         addr = conn.addr
  988:         is_connection_replaced = (init.sock is not sock)
  989: 
  990:         log.add_conn("Removed connection of type %s to user %s, address %s", (conn_type, username, addr))
  991: 
  992:         if not is_connection_replaced:
  993:             init.sock = None
  994: 
  995:         if conn_type == ConnectionType.DISTRIBUTED:
  996:             child_conn = self._child_peers.get(username)
  997: 
  998:             if child_conn is conn:
  999:                 self._remove_child_peer_connection(username)
 1000: 
 1001:             elif conn is self._parent_conn:
 1002:                 self._send_have_no_parent()
 1003: 
 1004:         elif conn in self._file_init_msgs:
 1005:             file_init = self._file_init_msgs.pop(conn)
 1006: 
 1007:             if self._should_process_queue:
 1008:                 timed_out = (time.monotonic() - conn.last_active) > self.CONNECTION_MAX_IDLE
 1009:                 events.emit_main_thread(
 1010:                     "file-connection-closed", username=username, token=file_init.token,
 1011:                     sock=sock, timed_out=timed_out
 1012:                 )
 1013: 
 1014:         if conn in self._file_download_msgs:
 1015:             del self._file_download_msgs[conn]
 1016:             self._total_downloads -= 1
 1017: 
 1018:             if not self._total_downloads:
 1019:                 self._total_download_bandwidth = 0
 1020: 
 1021:             self._calc_download_limit()
 1022: 
 1023:         elif conn in self._file_upload_msgs:
 1024:             del self._file_upload_msgs[conn]
 1025:             self._total_uploads -= 1
 1026: 
 1027:             if not self._total_uploads:
 1028:                 self._total_upload_bandwidth = 0
 1029: 
 1030:             self._calc_upload_limit_function()
 1031: 
 1032:         init_key = username + conn_type
 1033: 
 1034:         if init_key not in self._username_init_msgs:
 1035:             return
 1036: 
```

## github-branch-master

### `_process_upload()`

```text
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
```

### `_check_connections()` idle closure path

```text
 1110:     def _check_connections(self, current_time):
 1111: 
 1112:         num_sockets = self._num_sockets
 1113:         inactive_conns = set()
 1114:         stale_conns = set()
 1115: 
 1116:         for conn in self._conns.values():
 1117:             if not conn.is_established:
 1118:                 if (current_time - conn.last_active) > self.IN_PROGRESS_STALE_AFTER:
 1119:                     stale_conns.add(conn)
 1120: 
 1121:             elif self._is_connection_inactive(conn, current_time, num_sockets):
 1122:                 inactive_conns.add(conn)
 1123: 
 1124:             elif conn in self._file_download_msgs:
 1125:                 file_download = self._file_download_msgs[conn]
 1126: 
 1127:                 events.emit_main_thread(
 1128:                     "file-download-progress",
 1129:                     username=conn.init.target_user, token=file_download.token,
 1130:                     bytes_left=file_download.leftbytes, speed=file_download.speed
 1131:                 )
 1132:                 file_download.speed = 0
 1133: 
 1134:             elif conn in self._file_upload_msgs:
 1135:                 file_upload = self._file_upload_msgs[conn]
 1136: 
 1137:                 events.emit_main_thread(
 1138:                     "file-upload-progress",
 1139:                     username=conn.init.target_user, token=file_upload.token,
 1140:                     offset=file_upload.offset, bytes_sent=file_upload.sentbytes,
 1141:                     speed=file_upload.speed
 1142:                 )
 1143:                 file_upload.speed = 0
 1144: 
 1145:         if inactive_conns:
 1146:             for conn in inactive_conns:
 1147:                 self._close_connection(conn)
 1148: 
 1149:             inactive_conns.clear()
 1150: 
 1151:         if stale_conns:
 1152:             for conn in stale_conns:
 1153:                 self._connect_error(self.ERROR_TIMED_OUT, conn)
 1154:                 self._close_connection(conn)
 1155: 
```

### `_close_connection()` file-connection close event

```text
  974:     def _close_connection(self, conn):
  975: 
  976:         if conn is None:
  977:             return
  978: 
  979:         sock = conn.sock
  980:         del self._conns[sock]
  981: 
  982:         if conn is self._server_conn:
  983:             # Disconnecting from server, clean up connections and queue
  984:             self._server_disconnect()
  985: 
  986:         self._selector.unregister(sock)
  987:         self._close_socket(sock)
  988:         self._num_sockets -= 1
  989: 
  990:         conn.sock = None
  991: 
  992:         try:
  993:             conn.in_buffer.clear()
  994:             conn.out_buffer.clear()
  995: 
  996:         except BufferError as error:
  997:             log.add_conn("Failed to clear connection buffers: %s", error)
  998: 
  999:         if conn.__class__ is not PeerConnection:
 1000:             return
 1001: 
 1002:         init = conn.init
 1003: 
 1004:         if init is None:
 1005:             # No peer init message present, nothing to do
 1006:             return
 1007: 
 1008:         conn_type = init.conn_type
 1009:         username = init.target_user
 1010:         addr = conn.addr
 1011:         is_connection_replaced = (init.sock is not sock)
 1012: 
 1013:         log.add_conn("Removed connection of type %s to user %s, address %s", (conn_type, username, addr))
 1014: 
 1015:         if not is_connection_replaced:
 1016:             init.sock = None
 1017: 
 1018:         if conn_type == ConnectionType.DISTRIBUTED:
 1019:             parent_candidate = self._potential_parents.get(username)
 1020: 
 1021:             if self._parent is not None and conn is self._parent.conn:
 1022:                 self._send_have_no_parent()
 1023: 
 1024:             if parent_candidate is not None and conn is parent_candidate.conn:
 1025:                 parent_candidate.conn = None
 1026: 
 1027:             child_conn = self._child_peers.get(username)
 1028: 
 1029:             if child_conn is conn:
 1030:                 self._remove_child_peer_connection(username)
 1031: 
 1032:         elif conn in self._file_init_msgs:
 1033:             file_init = self._file_init_msgs.pop(conn)
 1034: 
 1035:             if self._should_process_queue:
 1036:                 timed_out = (time.monotonic() - conn.last_active) > self.CONNECTION_MAX_IDLE
 1037:                 events.emit_main_thread(
 1038:                     "file-connection-closed", username=username, token=file_init.token,
 1039:                     sock=sock, timed_out=timed_out
 1040:                 )
 1041: 
 1042:         if conn in self._file_download_msgs:
 1043:             del self._file_download_msgs[conn]
 1044:             self._total_downloads -= 1
 1045: 
 1046:             if not self._total_downloads:
 1047:                 self._total_download_bandwidth = 0
 1048: 
 1049:             self._calc_download_limit()
 1050: 
 1051:         elif conn in self._file_upload_msgs:
 1052:             del self._file_upload_msgs[conn]
 1053:             self._total_uploads -= 1
 1054: 
```
