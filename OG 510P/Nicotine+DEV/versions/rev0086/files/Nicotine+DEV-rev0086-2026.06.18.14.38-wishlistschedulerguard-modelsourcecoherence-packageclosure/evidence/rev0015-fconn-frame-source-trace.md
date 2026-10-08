## github-tag-3.3.10 — pynicotine/slskproto.py

### _process_file_init_message around line 1866
 1866:     def _process_file_init_message(self, conn, in_buffer):
 1867: 
 1868:         msg_size = idx = 4
 1869:         msg = self._unpack_network_message(
 1870:             FileTransferInit,
 1871:             memoryview(in_buffer)[:msg_size],
 1872:             msg_size,
 1873:             conn_type="file",
 1874:             sock=conn.sock,
 1875:             username=conn.init.target_user
 1876:         )
 1877: 
 1878:         if msg is not None and msg.token is not None:
 1879:             self._file_init_msgs[conn] = msg
 1880:             self._emit_network_message_event(msg)
 1881: 
 1882:         return idx
 1883: 
 1884:     def _process_file_offset_message(self, conn, in_buffer):
 1885: 
 1886:         file_upload = self._file_upload_msgs[conn]
 1887: 
 1888:         if file_upload.offset is not None:
 1889:             # No more incoming messages on this connection after receiving the
 1890:             # file offset. If peer sends something anyway, clear it.

### _process_file_offset_message around line 1884
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
 1917: 
 1918:         except (OSError, ValueError) as error:
 1919:             events.emit_main_thread(
 1920:                 "upload-file-error",
 1921:                 username=conn.init.target_user, token=file_upload.token, error=error
 1922:             )
 1923:             self._close_connection(conn)
 1924:             return None
 1925: 
 1926:         return idx
 1927: 
 1928:     def _write_download_file(self, file_download, data, data_len):

### _process_file_input around line 2015
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
 2029:             conn.has_post_init_activity = True
 2030: 
 2031:     def _process_file_output(self, msg):
 2032: 
 2033:         msg_class = msg.__class__


## github-branch-3.3.x — pynicotine/slskproto.py

### _process_file_init_message around line 1951
 1951:     def _process_file_init_message(self, conn, in_buffer):
 1952: 
 1953:         msg_size = idx = 4
 1954:         msg = self._unpack_network_message(
 1955:             FileTransferInit,
 1956:             memoryview(in_buffer)[:msg_size],
 1957:             msg_size,
 1958:             conn_type="file",
 1959:             sock=conn.sock,
 1960:             username=conn.init.target_user
 1961:         )
 1962: 
 1963:         if msg is not None and msg.token is not None:
 1964:             self._file_init_msgs[conn] = msg
 1965:             self._emit_network_message_event(msg)
 1966: 
 1967:         return idx
 1968: 
 1969:     def _process_file_offset_message(self, conn, in_buffer):
 1970: 
 1971:         file_upload = self._file_upload_msgs[conn]
 1972: 
 1973:         if file_upload.offset is not None:
 1974:             # No more incoming messages on this connection after receiving the
 1975:             # file offset. If peer sends something anyway, clear it.

### _process_file_offset_message around line 1969
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
 2002: 
 2003:         except (OSError, ValueError) as error:
 2004:             events.emit_main_thread(
 2005:                 "upload-file-error",
 2006:                 username=conn.init.target_user, token=file_upload.token, error=error
 2007:             )
 2008:             self._close_connection(conn)
 2009:             return None
 2010: 
 2011:         return idx
 2012: 
 2013:     def _write_download_file(self, file_download, data, data_len):

### _process_file_input around line 2100
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
 2114:             conn.has_post_init_activity = True
 2115: 
 2116:     def _process_file_output(self, conn, msg):
 2117: 
 2118:         msg_class = msg.__class__


## github-branch-master — pynicotine/slskproto.py

### _process_file_init_message around line 1993
 1993:     def _process_file_init_message(self, conn, in_buffer):
 1994: 
 1995:         msg_size = idx = 4
 1996:         msg = self._unpack_network_message(
 1997:             FileTransferInit,
 1998:             memoryview(in_buffer)[:msg_size],
 1999:             msg_size,
 2000:             conn_type="file",
 2001:             sock=conn.sock,
 2002:             username=conn.init.target_user
 2003:         )
 2004: 
 2005:         if msg is not None and msg.token is not None:
 2006:             self._file_init_msgs[conn] = msg
 2007:             self._emit_network_message_event(msg)
 2008: 
 2009:         return idx
 2010: 
 2011:     def _process_file_offset_message(self, conn, in_buffer):
 2012: 
 2013:         file_upload = self._file_upload_msgs[conn]
 2014: 
 2015:         if file_upload.offset is not None:
 2016:             # No more incoming messages on this connection after receiving the
 2017:             # file offset. If peer sends something anyway, clear it.

### _process_file_offset_message around line 2011
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
 2044: 
 2045:         except (OSError, ValueError) as error:
 2046:             events.emit_main_thread(
 2047:                 "upload-file-error",
 2048:                 username=conn.init.target_user, token=file_upload.token, error=error
 2049:             )
 2050:             self._close_connection(conn)
 2051:             return None
 2052: 
 2053:         return idx
 2054: 
 2055:     def _write_download_file(self, file_download, data, data_len):

### _process_file_input around line 2137
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
 2151:             conn.has_post_init_activity = True
 2152: 
 2153:     def _process_file_output(self, conn, msg):
 2154: 
 2155:         msg_class = msg.__class__


## slskmessages fixed-width definitions

### class FileTransferInit around line 3787 (3.3.10; same message shape in all lanes)
 3787: class FileTransferInit(FileMessage):
 3788:     """We send this to a peer via a 'F' connection to tell them that we want to
 3789:     start uploading a file. The token is the same as the one previously included in the
 3790:     TransferRequest peer message.
 3791: 
 3792:     Note that slskd and Nicotine+ <= 3.0.2 use legacy download requests, and send this
 3793:     message when initializing our file upload connection from their end.
 3794:     """
 3795: 
 3796:     __slots__ = ("token", "is_outgoing")
 3797: 
 3798:     def __init__(self, token=None, is_outgoing=False):
 3799:         FileMessage.__init__(self)
 3800:         self.token = token
 3801:         self.is_outgoing = is_outgoing
 3802: 
 3803:     def make_network_message(self):
 3804:         return self.pack_uint32(self.token)
 3805: 
 3806:     def parse_network_message(self, message):
 3807:         _pos, self.token = self.unpack_uint32(message)
 3808: 

### class FileOffset around line 3810 (3.3.10; same message shape in all lanes)
 3810: class FileOffset(FileMessage):
 3811:     """We send this to the uploading peer at the beginning of a 'F' connection,
 3812:     to tell them how many bytes of the file we've previously downloaded. If nothing
 3813:     was downloaded, the offset is 0.
 3814: 
 3815:     Note that Soulseek NS fails to read the size of an incomplete download if more
 3816:     than 2 GB of the file has been downloaded, and the download is resumed. In
 3817:     consequence, the client sends an invalid file offset of -1.
 3818:     """
 3819: 
 3820:     __slots__ = ("offset",)
 3821: 
 3822:     def __init__(self, sock=None, offset=None):
 3823:         FileMessage.__init__(self, sock=sock)
 3824:         self.offset = offset
 3825: 
 3826:     def make_network_message(self):
 3827:         return self.pack_uint64(self.offset)
 3828: 
 3829:     def parse_network_message(self, message):
 3830:         _pos, self.offset = self.unpack_uint64(message)
 3831: 
