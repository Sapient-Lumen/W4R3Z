# rev0038 PB-01 source trace

Line anchors from the archived source lanes; this compact cube does not embed the source trees.

## github-tag-3.3.10

`pynicotine/slskproto.py` sha256: `7faf9082bd41593ec1c85dd0b876c44f17ae89a12d49b337413b937798b0350c`

- line 611: `def _add_init_message(self, init):`
- line 700: `def _process_conn_messages(self, init):`
- line 865: `def _replace_existing_connection(self, init):`
- line 1518: `def _process_peer_init_message(self, conn, msg_type, msg_size, in_buffer, start_offset, end_offset):`
- line 1583: `def _process_peer_init_input(self, conn):`
- line 2521: `def _process_conn_incoming_messages(self, conn):`
- line 2549: `"promoting to primary connection", (init.conn_type, init.target_user))`
- line 1866: `def _process_file_init_message(self, conn, in_buffer):`
- line 2062: `def _accept_child_peer_connection(self, conn):`

## github-branch-3.3.x

`pynicotine/slskproto.py` sha256: `b468bf99f3c035830ab0b0694220b84e35b03a70d92a49337dc11c7693a15bec`

- line 657: `def _add_init_message(self, init):`
- line 752: `def _process_conn_messages(self, init):`
- line 917: `def _replace_existing_connection(self, init):`
- line 1597: `def _process_peer_init_message(self, conn, msg_type, msg_size, in_buffer, start_offset, end_offset):`
- line 1666: `def _process_peer_init_input(self, conn):`
- line 2578: `def _process_conn_incoming_messages(self, conn):`
- line 2606: `"promoting to primary connection", (init.conn_type, init.target_user))`
- line 1951: `def _process_file_init_message(self, conn, in_buffer):`
- line 2145: `def _accept_child_peer_connection(self, conn):`

## github-branch-master

`pynicotine/slskproto.py` sha256: `46addf59c69e2b2ede74ccc99657d1df2a78aaedba07861b7ea1a41ad58dbb7e`

- line 667: `def _add_init_message(self, init):`
- line 773: `def _process_conn_messages(self, init):`
- line 935: `def _replace_existing_connection(self, init):`
- line 1639: `def _process_peer_init_message(self, conn, msg_type, msg_size, msg_content):`
- line 1708: `def _process_peer_init_input(self, conn):`
- line 2702: `def _process_conn_incoming_messages(self, conn):`
- line 2730: `"promoting to primary connection", (init.conn_type, init.target_user))`
- line 1993: `def _process_file_init_message(self, conn, in_buffer):`
- line 2182: `def _accept_child_peer_connection(self, conn):`
