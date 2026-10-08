# rev0024 source trace — TRANSFER-CONTROL-PATH-BUDGET-01

External source bundle: `Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z.zip`.

The snippets below are line-oriented traces from the three archived source lanes. They show the shared shape used by U-271, U-274, and U-256: protocol parsers decode peer-supplied virtual path strings directly; upload/folder handlers then perform lookup/logging/response construction before a small semantic path/component budget is applied.

## github-tag-3.3.10
### pynicotine/slskmessages.py:3434-3454
```text
  3434	class FolderContentsRequest(PeerMessage):
  3435	    """Peer code 36.
  3436	
  3437	    We ask the peer to send us the contents of a single folder.
  3438	    """
  3439	
  3440	    __slots__ = ("dir", "token", "legacy_client")
  3441	
  3442	    def __init__(self, directory=None, token=None, legacy_client=False):
  3443	        PeerMessage.__init__(self)
  3444	        self.dir = directory
  3445	        self.token = token
  3446	        self.legacy_client = legacy_client
  3447	
  3448	    def make_network_message(self):
  3449	        msg = bytearray()
  3450	        msg += self.pack_uint32(self.token)
  3451	        msg += self.pack_string(self.dir, is_legacy=self.legacy_client)
  3452	
  3453	        return msg
  3454	
```

### pynicotine/slskmessages.py:3540-3567
```text
  3540	        PeerMessage.__init__(self)
  3541	        self.direction = direction
  3542	        self.token = token
  3543	        self.file = file  # virtual file
  3544	        self.filesize = filesize
  3545	
  3546	    def make_network_message(self):
  3547	        msg = bytearray()
  3548	        msg += self.pack_uint32(self.direction)
  3549	        msg += self.pack_uint32(self.token)
  3550	        msg += self.pack_string(self.file)
  3551	
  3552	        if self.direction == TransferDirection.UPLOAD:
  3553	            msg += self.pack_uint64(self.filesize)
  3554	
  3555	        return msg
  3556	
  3557	    def parse_network_message(self, message):
  3558	        pos, self.direction = self.unpack_uint32(message)
  3559	        pos, self.token = self.unpack_uint32(message, pos)
  3560	        pos, self.file = self.unpack_string(message, pos)
  3561	
  3562	        if self.direction == TransferDirection.UPLOAD:
  3563	            pos, self.filesize = self.unpack_uint64(message, pos)
  3564	
  3565	
  3566	class TransferResponse(PeerMessage):
  3567	    """Peer code 41.
```

### pynicotine/slskmessages.py:3625-3745
```text
  3625	class QueueUpload(PeerMessage):
  3626	    """Peer code 43.
  3627	
  3628	    This message is used to tell a peer that an upload should be queued
  3629	    on their end. Once the recipient is ready to transfer the requested
  3630	    file, they will send a TransferRequest to us.
  3631	    """
  3632	
  3633	    __slots__ = ("file", "legacy_client")
  3634	
  3635	    def __init__(self, file=None, legacy_client=False):
  3636	        PeerMessage.__init__(self)
  3637	        self.file = file
  3638	        self.legacy_client = legacy_client
  3639	
  3640	    def make_network_message(self):
  3641	        return self.pack_string(self.file, is_legacy=self.legacy_client)
  3642	
  3643	    def parse_network_message(self, message):
  3644	        _pos, self.file = self.unpack_string(message)
  3645	
  3646	
  3647	class PlaceInQueueResponse(PeerMessage):
  3648	    """Peer code 44.
  3649	
  3650	    The peer replies with the upload queue placement of the requested
  3651	    file.
  3652	    """
  3653	
  3654	    __slots__ = ("filename", "place")
  3655	
  3656	    def __init__(self, filename=None, place=None):
  3657	        PeerMessage.__init__(self)
  3658	        self.filename = filename
  3659	        self.place = place
  3660	
  3661	    def make_network_message(self):
  3662	        msg = bytearray()
  3663	        msg += self.pack_string(self.filename)
  3664	        msg += self.pack_uint32(self.place)
  3665	
  3666	        return msg
  3667	
  3668	    def parse_network_message(self, message):
  3669	        pos, self.filename = self.unpack_string(message)
  3670	        pos, self.place = self.unpack_uint32(message, pos)
  3671	
  3672	
  3673	class UploadFailed(PeerMessage):
  3674	    """Peer code 46.
  3675	
  3676	    This message is sent whenever a file connection of an active upload
  3677	    closes. Soulseek NS clients can also send this message when a file
  3678	    cannot be read. The recipient either re-queues the upload (download
  3679	    on their end), or ignores the message if the transfer finished.
  3680	    """
  3681	
  3682	    __slots__ = ("file",)
  3683	
  3684	    def __init__(self, file=None):
  3685	        PeerMessage.__init__(self)
  3686	        self.file = file
  3687	
  3688	    def make_network_message(self):
  3689	        return self.pack_string(self.file)
  3690	
  3691	    def parse_network_message(self, message):
  3692	        _pos, self.file = self.unpack_string(message)
  3693	
  3694	
  3695	class UploadDenied(PeerMessage):
  3696	    """Peer code 50.
  3697	
  3698	    This message is sent to reject QueueUpload attempts and previously
  3699	    queued files. The reason for rejection will appear in the transfer
  3700	    list of the recipient.
  3701	    """
  3702	
  3703	    __slots__ = ("file", "reason")
  3704	
  3705	    def __init__(self, file=None, reason=None):
  3706	        PeerMessage.__init__(self)
  3707	        self.file = file
  3708	        self.reason = reason
  3709	
  3710	    def make_network_message(self):
  3711	        msg = bytearray()
  3712	        msg += self.pack_string(self.file)
  3713	        msg += self.pack_string(self.reason)
  3714	
  3715	        return msg
  3716	
  3717	    def parse_network_message(self, message):
  3718	        pos, self.file = self.unpack_string(message)
  3719	        pos, self.reason = self.unpack_string(message, pos)
  3720	
  3721	
  3722	class PlaceInQueueRequest(PeerMessage):
  3723	    """Peer code 51.
  3724	
  3725	    This message is sent when asking for the upload queue placement of a
  3726	    file.
  3727	    """
  3728	
  3729	    __slots__ = ("file", "legacy_client")
  3730	
  3731	    def __init__(self, file=None, legacy_client=False):
  3732	        PeerMessage.__init__(self)
  3733	        self.file = file
  3734	        self.legacy_client = legacy_client
  3735	
  3736	    def make_network_message(self):
  3737	        return self.pack_string(self.file, is_legacy=self.legacy_client)
  3738	
  3739	    def parse_network_message(self, message):
  3740	        _pos, self.file = self.unpack_string(message)
  3741	
  3742	
  3743	class UploadQueueNotification(PeerMessage):
  3744	    """Peer code 52.
  3745	
```

### pynicotine/uploads.py:862-908
```text
   862	    def _queue_upload(self, msg):
   863	        """Peer code 43.
   864	
   865	        Peer remotely queued a download (upload here). This is the
   866	        modern replacement to a TransferRequest with direction 0
   867	        (download request). We will initiate the upload of the queued
   868	        file later.
   869	        """
   870	
   871	        username = msg.username
   872	        virtual_path = msg.file
   873	        real_path = core.shares.virtual2real(virtual_path)
   874	        allowed, reason, size = self._check_queue_upload_allowed(username, msg.addr, virtual_path, real_path, msg)
   875	
   876	        log.add_transfer("Upload request for file %s from user: %s, allowed: %s, "
   877	                         "reason: %s", (virtual_path, username, allowed, reason))
   878	
   879	        if not allowed:
   880	            if reason and reason != TransferRejectReason.QUEUED:
   881	                core.send_message_to_peer(username, UploadDenied(virtual_path, reason))
   882	
   883	            return
   884	
   885	        transfer = self.transfers.get(username + virtual_path)
   886	        folder_path = os.path.dirname(real_path)
   887	
   888	        if transfer is not None:
   889	            self._unfail_transfer(transfer)
   890	
   891	            transfer.folder_path = folder_path
   892	            transfer.size = size
   893	
   894	            if transfer.status == TransferStatus.FINISHED:
   895	                transfer.current_byte_offset = None
   896	                transfer.speed = transfer.avg_speed = transfer.time_elapsed = transfer.time_left = 0
   897	        else:
   898	            transfer = Transfer(username, virtual_path, folder_path, size)
   899	            self._append_transfer(transfer)
   900	
   901	        self._enqueue_transfer(transfer)
   902	        self._update_transfer(transfer)
   903	
   904	        # Must be emitted after the final update to prevent inconsistent state
   905	        core.pluginhandler.upload_queued_notification(username, virtual_path, real_path)
   906	
   907	        self._check_upload_queue()
   908	
```

### pynicotine/uploads.py:909-991
```text
   909	    def _transfer_request(self, msg):
   910	        """Peer code 40."""
   911	
   912	        username = msg.username
   913	
   914	        if msg.direction != TransferDirection.DOWNLOAD:
   915	            return
   916	
   917	        response = self._transfer_request_uploads(msg)
   918	
   919	        if response is None:
   920	            return
   921	
   922	        log.add_transfer("Responding to legacy upload request %s for file %s from user %s, "
   923	                         "allowed: %s, reason: %s",
   924	                         (response.token, msg.file, username, response.allowed, response.reason))
   925	
   926	        core.send_message_to_peer(username, response)
   927	
   928	    def _transfer_request_uploads(self, msg):
   929	        """Remote peer is requesting to download a file through your upload
   930	        queue.
   931	
   932	        Note that the QueueUpload peer message has replaced this method
   933	        of requesting a download in most clients.
   934	        """
   935	
   936	        username = msg.username
   937	        virtual_path = msg.file
   938	        token = msg.token
   939	
   940	        log.add_transfer("Received legacy upload request %s for file %s from user %s",
   941	                         (token, virtual_path, username))
   942	
   943	        # Is user allowed to download?
   944	        real_path = core.shares.virtual2real(virtual_path)
   945	        allowed, reason, size = self._check_queue_upload_allowed(username, msg.addr, virtual_path, real_path, msg)
   946	
   947	        if not allowed:
   948	            if reason:
   949	                return TransferResponse(allowed=False, reason=reason, token=token)
   950	
   951	            return None
   952	
   953	        # All checks passed, user can queue file!
   954	        transfer = self.transfers.get(username + virtual_path)
   955	        folder_path = os.path.dirname(real_path)
   956	
   957	        if transfer is not None:
   958	            self._unfail_transfer(transfer)
   959	
   960	            transfer.folder_path = folder_path
   961	            transfer.size = size
   962	
   963	            if transfer.status == TransferStatus.FINISHED:
   964	                transfer.current_byte_offset = None
   965	                transfer.speed = transfer.avg_speed = transfer.time_elapsed = transfer.time_left = 0
   966	        else:
   967	            transfer = Transfer(username, virtual_path, folder_path, size)
   968	            self._append_transfer(transfer)
   969	
   970	        if not self.is_new_upload_accepted() or username in self.active_users:
   971	            self._enqueue_transfer(transfer)
   972	            self._update_transfer(transfer)
   973	
   974	            # Must be emitted after the final update to prevent inconsistent state
   975	            core.pluginhandler.upload_queued_notification(username, virtual_path, real_path)
   976	
   977	            return TransferResponse(allowed=False, reason=TransferRejectReason.QUEUED, token=token)
   978	
   979	        # All checks passed, starting a new upload.
   980	        current_size = self._get_current_file_size(real_path)
   981	
   982	        if current_size is not None:
   983	            transfer.size = current_size
   984	
   985	        self._activate_transfer(transfer, token)
   986	        self._update_transfer(transfer)
   987	
   988	        # Must be emitted after the final update to prevent inconsistent state
   989	        core.pluginhandler.upload_queued_notification(username, virtual_path, real_path)
   990	
   991	        return TransferResponse(allowed=True, token=token, filesize=size)
```

### pynicotine/uploads.py:1187-1249
```text
  1187	    def _place_in_queue_request(self, msg):
  1188	        """Peer code 51."""
  1189	
  1190	        username = msg.username
  1191	        virtual_path = msg.file
  1192	        upload = self.queued_users.get(username, {}).get(virtual_path)
  1193	
  1194	        if upload is None:
  1195	            return
  1196	
  1197	        is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  1198	        is_privileged_queue = self.is_privileged(username)
  1199	        privileged_queued_users = {k: len(v) for k, v in self.queued_users.items() if self.is_privileged(k)}
  1200	        queue_position = 0
  1201	
  1202	        if is_fifo_queue:
  1203	            if is_privileged_queue != self._privileged_position_requested or upload not in self._queue_positions:
  1204	                self._queue_position_users.clear()
  1205	
  1206	                if is_privileged_queue:
  1207	                    self._queue_positions.clear()
  1208	                    position = 1
  1209	
  1210	                    for i_upload in self.queued_transfers:
  1211	                        if i_upload.username in privileged_queued_users:
  1212	                            self._queue_positions[i_upload] = position
  1213	                            position += 1
  1214	                else:
  1215	                    self._queue_positions = {
  1216	                        i_upload: position
  1217	                        for position, i_upload in enumerate(self.queued_transfers, start=1)
  1218	                    }
  1219	
  1220	            queue_position = self._queue_positions[upload]
  1221	        else:
  1222	            user_queue_positions = self._queue_position_users[username]
  1223	
  1224	            if upload not in user_queue_positions:
  1225	                self._queue_positions.clear()
  1226	                user_queue_positions.update({
  1227	                    i_upload: position
  1228	                    for position, i_upload in enumerate(self.queued_users[username].values(), start=1)
  1229	                })
  1230	
  1231	            if is_privileged_queue:
  1232	                num_queued_users = len(privileged_queued_users)
  1233	            else:
  1234	                # Cycling through privileged users first
  1235	                queue_position += sum(
  1236	                    num_queued_uploads for num_queued_uploads in privileged_queued_users.values())
  1237	                num_queued_users = len(self.queued_users)
  1238	
  1239	            queue_position += num_queued_users + user_queue_positions[upload]
  1240	
  1241	        self._privileged_position_requested = is_privileged_queue
  1242	
  1243	        if queue_position > 0:
  1244	            core.send_message_to_peer(
  1245	                username, PlaceInQueueResponse(virtual_path, queue_position))
  1246	
  1247	        # Update queue position in our list of uploads
  1248	        upload.queue_position = queue_position
  1249	        self._update_transfer(upload, update_parent=False)
```

### pynicotine/shares.py:1193-1215
```text
  1193	    def _folder_contents_request(self, msg):
  1194	        """Peer code 36."""
  1195	
  1196	        ip_address, _port = msg.addr
  1197	        username = msg.username
  1198	        folder_path = msg.dir
  1199	        permission_level, _reject_reason = self.check_user_permission(username, ip_address)
  1200	        folder_data = None
  1201	
  1202	        if permission_level != PermissionLevel.BANNED:
  1203	            folder_data = self.share_dbs.get("public_streams", {}).get(folder_path)
  1204	
  1205	            if (folder_data is None
  1206	                    and (config.sections["transfers"]["reveal_buddy_shares"]
  1207	                         or permission_level in {PermissionLevel.BUDDY, PermissionLevel.TRUSTED})):
  1208	                folder_data = self.share_dbs.get("buddy_streams", {}).get(folder_path)
  1209	
  1210	            if (folder_data is None
  1211	                    and (config.sections["transfers"]["reveal_trusted_shares"]
  1212	                         or permission_level == PermissionLevel.TRUSTED)):
  1213	                folder_data = self.share_dbs.get("trusted_streams", {}).get(folder_path)
  1214	
  1215	        core.send_message_to_peer(
```


## github-branch-3.3.x
### pynicotine/slskmessages.py:3465-3485
```text
  3465	class FolderContentsRequest(PeerMessage):
  3466	    """Peer code 36.
  3467	
  3468	    We ask the peer to send us the contents of a single folder.
  3469	    """
  3470	
  3471	    __slots__ = ("dir", "token", "legacy_client")
  3472	
  3473	    def __init__(self, directory=None, token=None, legacy_client=False):
  3474	        PeerMessage.__init__(self)
  3475	        self.dir = directory
  3476	        self.token = token
  3477	        self.legacy_client = legacy_client
  3478	
  3479	    def make_network_message(self):
  3480	        msg = bytearray()
  3481	        msg += self.pack_uint32(self.token)
  3482	        msg += self.pack_string(self.dir, is_legacy=self.legacy_client)
  3483	
  3484	        return msg
  3485	
```

### pynicotine/slskmessages.py:3571-3605
```text
  3571	    slskd and Seeker still use this method for downloading, so we need to
  3572	    ensure we still understand such requests.
  3573	    """
  3574	
  3575	    __slots__ = ("direction", "token", "file", "filesize")
  3576	
  3577	    def __init__(self, direction=None, token=None, file=None, filesize=None):
  3578	        PeerMessage.__init__(self)
  3579	        self.direction = direction
  3580	        self.token = token
  3581	        self.file = file  # virtual file
  3582	        self.filesize = filesize
  3583	
  3584	    def make_network_message(self):
  3585	        msg = bytearray()
  3586	        msg += self.pack_uint32(self.direction)
  3587	        msg += self.pack_uint32(self.token)
  3588	        msg += self.pack_string(self.file)
  3589	
  3590	        if self.direction == TransferDirection.UPLOAD:
  3591	            msg += self.pack_uint64(self.filesize)
  3592	
  3593	        return msg
  3594	
  3595	    def parse_network_message(self, message):
  3596	        pos, self.direction = self.unpack_uint32(message)
  3597	        pos, self.token = self.unpack_uint32(message, pos)
  3598	        pos, self.file = self.unpack_string(message, pos)
  3599	
  3600	        if self.direction == TransferDirection.UPLOAD:
  3601	            pos, self.filesize = self.unpack_uint64(message, pos)
  3602	
  3603	
  3604	class TransferResponse(PeerMessage):
  3605	    """Peer code 41.
```

### pynicotine/slskmessages.py:3670-3790
```text
  3670	class QueueUpload(PeerMessage):
  3671	    """Peer code 43.
  3672	
  3673	    This message is used to tell a peer that an upload should be queued
  3674	    on their end. Once the recipient is ready to transfer the requested
  3675	    file, they will send a TransferRequest to us.
  3676	    """
  3677	
  3678	    __slots__ = ("file", "legacy_client")
  3679	
  3680	    def __init__(self, file=None, legacy_client=False):
  3681	        PeerMessage.__init__(self)
  3682	        self.file = file
  3683	        self.legacy_client = legacy_client
  3684	
  3685	    def make_network_message(self):
  3686	        return self.pack_string(self.file, is_legacy=self.legacy_client)
  3687	
  3688	    def parse_network_message(self, message):
  3689	        _pos, self.file = self.unpack_string(message)
  3690	
  3691	
  3692	class PlaceInQueueResponse(PeerMessage):
  3693	    """Peer code 44.
  3694	
  3695	    The peer replies with the upload queue placement of the requested
  3696	    file.
  3697	    """
  3698	
  3699	    __slots__ = ("filename", "place")
  3700	
  3701	    def __init__(self, filename=None, place=None):
  3702	        PeerMessage.__init__(self)
  3703	        self.filename = filename
  3704	        self.place = place
  3705	
  3706	    def make_network_message(self):
  3707	        msg = bytearray()
  3708	        msg += self.pack_string(self.filename)
  3709	        msg += self.pack_uint32(self.place)
  3710	
  3711	        return msg
  3712	
  3713	    def parse_network_message(self, message):
  3714	        pos, self.filename = self.unpack_string(message)
  3715	        pos, self.place = self.unpack_uint32(message, pos)
  3716	
  3717	
  3718	class UploadFailed(PeerMessage):
  3719	    """Peer code 46.
  3720	
  3721	    This message is sent whenever a file connection of an active upload
  3722	    closes. Soulseek NS clients can also send this message when a file
  3723	    cannot be read. The recipient either re-queues the upload (download
  3724	    on their end), or ignores the message if the transfer finished.
  3725	    """
  3726	
  3727	    __slots__ = ("file",)
  3728	
  3729	    def __init__(self, file=None):
  3730	        PeerMessage.__init__(self)
  3731	        self.file = file
  3732	
  3733	    def make_network_message(self):
  3734	        return self.pack_string(self.file)
  3735	
  3736	    def parse_network_message(self, message):
  3737	        _pos, self.file = self.unpack_string(message)
  3738	
  3739	
  3740	class UploadDenied(PeerMessage):
  3741	    """Peer code 50.
  3742	
  3743	    This message is sent to reject QueueUpload attempts and previously
  3744	    queued files. The reason for rejection will appear in the transfer
  3745	    list of the recipient.
  3746	    """
  3747	
  3748	    __slots__ = ("file", "reason")
  3749	
  3750	    def __init__(self, file=None, reason=None):
  3751	        PeerMessage.__init__(self)
  3752	        self.file = file
  3753	        self.reason = reason
  3754	
  3755	    def make_network_message(self):
  3756	        msg = bytearray()
  3757	        msg += self.pack_string(self.file)
  3758	        msg += self.pack_string(self.reason)
  3759	
  3760	        return msg
  3761	
  3762	    def parse_network_message(self, message):
  3763	        pos, self.file = self.unpack_string(message)
  3764	        pos, self.reason = self.unpack_string(message, pos)
  3765	
  3766	
  3767	class PlaceInQueueRequest(PeerMessage):
  3768	    """Peer code 51.
  3769	
  3770	    This message is sent when asking for the upload queue placement of a
  3771	    file.
  3772	    """
  3773	
  3774	    __slots__ = ("file", "legacy_client")
  3775	
  3776	    def __init__(self, file=None, legacy_client=False):
  3777	        PeerMessage.__init__(self)
  3778	        self.file = file
  3779	        self.legacy_client = legacy_client
  3780	
  3781	    def make_network_message(self):
  3782	        return self.pack_string(self.file, is_legacy=self.legacy_client)
  3783	
  3784	    def parse_network_message(self, message):
  3785	        _pos, self.file = self.unpack_string(message)
  3786	
  3787	
  3788	class UploadQueueNotification(PeerMessage):
  3789	    """Peer code 52.
  3790	
```

### pynicotine/uploads.py:854-900
```text
   854	    def _queue_upload(self, msg):
   855	        """Peer code 43.
   856	
   857	        Peer remotely queued a download (upload here). This is the
   858	        modern replacement to a TransferRequest with direction 0
   859	        (download request). We will initiate the upload of the queued
   860	        file later.
   861	        """
   862	
   863	        username = msg.username
   864	        virtual_path = msg.file
   865	        real_path = core.shares.virtual2real(virtual_path)
   866	        allowed, reason, size = self._check_queue_upload_allowed(username, msg.addr, virtual_path, real_path, msg)
   867	
   868	        log.add_transfer("Upload request for file %s from user: %s, allowed: %s, "
   869	                         "reason: %s", (virtual_path, username, allowed, reason))
   870	
   871	        if not allowed:
   872	            if reason and reason != TransferRejectReason.QUEUED:
   873	                core.send_message_to_peer(username, UploadDenied(virtual_path, reason))
   874	
   875	            return
   876	
   877	        transfer = self.transfers.get(username + virtual_path)
   878	        folder_path = os.path.dirname(real_path)
   879	
   880	        if transfer is not None:
   881	            self._unfail_transfer(transfer)
   882	
   883	            transfer.folder_path = folder_path
   884	            transfer.size = size
   885	
   886	            if transfer.status == TransferStatus.FINISHED:
   887	                transfer.current_byte_offset = None
   888	                transfer.transferred_bytes_total = 0
   889	                transfer.speed = transfer.avg_speed = transfer.time_elapsed = transfer.time_left = 0
   890	        else:
   891	            transfer = Transfer(username, virtual_path, folder_path, size)
   892	            self._append_transfer(transfer)
   893	
   894	        self._enqueue_transfer(transfer)
   895	        self._update_transfer(transfer)
   896	
   897	        # Must be emitted after the final update to prevent inconsistent state
   898	        core.pluginhandler.upload_queued_notification(username, virtual_path, real_path)
   899	
   900	        self._check_upload_queue()
```

### pynicotine/uploads.py:984-1068
```text
   984	
   985	        log.add_transfer("Received response for upload with token: %s, allowed: %s, "
   986	                         "reason: %s, file size: %s", (token, msg.allowed, reason, msg.filesize))
   987	
   988	        upload = self.active_users.get(username, {}).get(token)
   989	
   990	        if upload is None:
   991	            log.add_transfer("Received unknown upload response: %s", msg)
   992	            return
   993	
   994	        if upload.sock is not None:
   995	            log.add_transfer("Upload with token %s already has an existing file connection", token)
   996	            return
   997	
   998	        if reason is not None:
   999	            if reason in TransferStatus.__dict__.values() or reason == TransferRejectReason.DISALLOWED_EXTENSION:
  1000	                # Don't allow internal statuses as reason
  1001	                reason = TransferRejectReason.CANCELLED
  1002	
  1003	            self._abort_transfer(upload, status=reason)
  1004	
  1005	            if reason == TransferRejectReason.COMPLETE:
  1006	                # A complete download of this file already exists on the user's end
  1007	                self._finish_transfer(upload, already_exists=True)
  1008	
  1009	            elif reason == TransferRejectReason.CANCELLED:
  1010	                self._auto_clear_transfer(upload)
  1011	
  1012	            self._check_upload_queue()
  1013	            return
  1014	
  1015	        core.send_message_to_peer(upload.username, FileTransferInit(token=token, is_outgoing=True))
  1016	        self._check_upload_queue()
  1017	
  1018	    def _transfer_timeout(self, transfer):
  1019	
  1020	        if transfer.request_timer_id is None:
  1021	            return
  1022	
  1023	        log.add_transfer("Upload %s with token %s for user %s timed out",
  1024	                         (transfer.virtual_path, transfer.token, transfer.username))
  1025	
  1026	        super()._transfer_timeout(transfer)
  1027	        self._check_upload_queue()
  1028	
  1029	    def _upload_file_error(self, username, token, error):
  1030	        """Networking thread encountered a local file error for upload."""
  1031	
  1032	        upload = self.active_users.get(username, {}).get(token)
  1033	
  1034	        if upload is None:
  1035	            return
  1036	
  1037	        if isinstance(error, ValueError):
  1038	            status = TransferStatus.CANCELLED
  1039	            error = f"Remote client does not support large file transfers: {error}"
  1040	        else:
  1041	            status = TransferStatus.LOCAL_FILE_ERROR
  1042	
  1043	        self._abort_transfer(upload, status=status)
  1044	
  1045	        log.add(_("Upload I/O error: %s"), error)
  1046	        self._check_upload_queue()
  1047	
  1048	    def _file_transfer_init(self, msg):
  1049	        """We are requesting to start uploading a file to a peer."""
  1050	
  1051	        if not msg.is_outgoing:
  1052	            # Transfer init message received from another peer, ignore
  1053	            return
  1054	
  1055	        username = msg.username
  1056	        token = msg.token
  1057	        upload = self.active_users.get(username, {}).get(token)
  1058	
  1059	        if upload is None or upload.sock is not None:
  1060	            log.add_transfer("Sending file upload init message with unknown token %s, closing connection", token)
  1061	            core.send_message_to_network_thread(CloseConnection(msg.sock))
  1062	            return
  1063	
  1064	        virtual_path = upload.virtual_path
  1065	        sock = upload.sock = msg.sock
  1066	        need_update = True
  1067	        upload_started = False
  1068	
```

### pynicotine/uploads.py:1175-1242
```text
  1175	    def _place_in_queue_request(self, msg):
  1176	        """Peer code 51."""
  1177	
  1178	        username = msg.username
  1179	        virtual_path = msg.file
  1180	        upload = self.queued_users.get(username, {}).get(virtual_path)
  1181	
  1182	        if upload is None:
  1183	            return
  1184	
  1185	        is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  1186	        is_privileged_queue = self.is_privileged(username)
  1187	        privileged_queued_users = {k: len(v) for k, v in self.queued_users.items() if self.is_privileged(k)}
  1188	        queue_position = 0
  1189	
  1190	        if is_fifo_queue:
  1191	            if is_privileged_queue != self._privileged_position_requested or upload not in self._queue_positions:
  1192	                self._queue_position_users.clear()
  1193	
  1194	                if is_privileged_queue:
  1195	                    self._queue_positions.clear()
  1196	                    position = 1
  1197	
  1198	                    for i_upload in self.queued_transfers:
  1199	                        if i_upload.username in privileged_queued_users:
  1200	                            self._queue_positions[i_upload] = position
  1201	                            position += 1
  1202	                else:
  1203	                    self._queue_positions = {
  1204	                        i_upload: position
  1205	                        for position, i_upload in enumerate(self.queued_transfers, start=1)
  1206	                    }
  1207	
  1208	            queue_position = self._queue_positions[upload]
  1209	        else:
  1210	            user_queue_positions = self._queue_position_users[username]
  1211	
  1212	            if upload not in user_queue_positions:
  1213	                self._queue_positions.clear()
  1214	                user_queue_positions.update({
  1215	                    i_upload: position
  1216	                    for position, i_upload in enumerate(self.queued_users[username].values(), start=1)
  1217	                })
  1218	
  1219	            if is_privileged_queue:
  1220	                num_queued_users = len(privileged_queued_users)
  1221	            else:
  1222	                # Cycling through privileged users first
  1223	                queue_position += sum(
  1224	                    num_queued_uploads for num_queued_uploads in privileged_queued_users.values())
  1225	                num_queued_users = len(self.queued_users)
  1226	
  1227	            queue_position += num_queued_users + user_queue_positions[upload]
  1228	
  1229	        self._privileged_position_requested = is_privileged_queue
  1230	
  1231	        if queue_position > 0:
  1232	            core.send_message_to_peer(
  1233	                username, PlaceInQueueResponse(virtual_path, queue_position))
  1234	
  1235	        # Update queue position in our list of uploads
  1236	        upload.queue_position = queue_position
  1237	        self._update_transfer(upload, update_parent=False)
```

### pynicotine/shares.py:1216-1243
```text
  1216	    def _folder_contents_request(self, msg):
  1217	        """Peer code 36."""
  1218	
  1219	        ip_address, _port = msg.addr
  1220	        username = msg.username
  1221	        folder_path = msg.dir
  1222	        permission_level, _reject_reason = self.check_user_permission(username, ip_address)
  1223	        folder_data = None
  1224	
  1225	        if permission_level != PermissionLevel.BANNED:
  1226	            folder_data = self.share_dbs.get("public_streams", {}).get(folder_path)
  1227	
  1228	            if (folder_data is None
  1229	                    and (config.sections["transfers"]["reveal_buddy_shares"]
  1230	                         or permission_level in {PermissionLevel.BUDDY, PermissionLevel.TRUSTED})):
  1231	                folder_data = self.share_dbs.get("buddy_streams", {}).get(folder_path)
  1232	
  1233	            if (folder_data is None
  1234	                    and (config.sections["transfers"]["reveal_trusted_shares"]
  1235	                         or permission_level == PermissionLevel.TRUSTED)):
  1236	                folder_data = self.share_dbs.get("trusted_streams", {}).get(folder_path)
  1237	
  1238	        core.send_message_to_peer(
  1239	            username, FolderContentsResponse(directory=folder_path, token=msg.token, shares=folder_data))
```


## github-branch-master
### pynicotine/slskmessages.py:3607-3631
```text
  3607	class FolderContentsRequest(PeerMessage):
  3608	    """Peer code 36.
  3609	
  3610	    We ask the peer to send us the contents of a single folder.
  3611	    """
  3612	
  3613	    __slots__ = ("dir", "token", "legacy_client")
  3614	
  3615	    def __init__(self, directory=None, token=None, legacy_client=False, *, msg_content=None):
  3616	        PeerMessage.__init__(self, msg_content)
  3617	        self.dir = directory
  3618	        self.token = token
  3619	        self.legacy_client = legacy_client
  3620	
  3621	    def make_network_message(self):
  3622	        msg = bytearray()
  3623	        msg += self.pack_uint32(self.token)
  3624	        msg += self.pack_string(self.dir, is_legacy=self.legacy_client)
  3625	
  3626	        return msg
  3627	
  3628	    def parse_network_message(self):
  3629	        self.token = self.unpack_uint32()
  3630	        self.dir = self.unpack_string()
  3631	
```

### pynicotine/slskmessages.py:3633-3715
```text
  3633	class FolderContentsResponse(PeerMessage):
  3634	    """Peer code 37.
  3635	
  3636	    A peer responds with the contents of a particular folder (with all
  3637	    subfolders) after we've sent a FolderContentsRequest.
  3638	    """
  3639	
  3640	    __slots__ = ("dir", "token", "list")
  3641	    __excluded_attrs__ = {"list"}
  3642	
  3643	    def __init__(self, directory=None, token=None, shares=None, *, msg_content=None):
  3644	        PeerMessage.__init__(self, msg_content)
  3645	        self.dir = directory
  3646	        self.token = token
  3647	        self.list = shares
  3648	
  3649	    def parse_network_message(self):
  3650	        decompressor = zlib.decompressobj()
  3651	        max_uncompressed_size = 134217728  # 128 MiB
  3652	
  3653	        self._offset = 0
  3654	        message_bytes = decompressor.decompress(self._message, 8)
  3655	        self._message = memoryview(message_bytes)
  3656	        self.token = self.unpack_uint32()
  3657	        dir_len = self.unpack_uint32()
  3658	
  3659	        self._offset = 4  # Skip token
  3660	        self._message = memoryview(message_bytes + decompressor.decompress(decompressor.unconsumed_tail, dir_len))
  3661	        self.dir = self.unpack_string()
  3662	
  3663	        if self.username + self.dir not in self.allowed_responses:
  3664	            return
  3665	
  3666	        # Optimization: only decompress the rest of the message when needed
  3667	        self._offset = 0
  3668	        self._message = memoryview(decompressor.decompress(decompressor.unconsumed_tail, max_uncompressed_size))
  3669	
  3670	        if not decompressor.unconsumed_tail:
  3671	            self._parse_remaining_network_message()
  3672	
  3673	    def _parse_remaining_network_message(self):
  3674	        ndir = self.unpack_uint32()
  3675	        folders = {}
  3676	
  3677	        for _ in range(ndir):
  3678	            directory = self.unpack_string().replace("/", "\\")
  3679	            nfiles = self.unpack_uint32()
  3680	
  3681	            ext = None
  3682	            folders[directory] = []
  3683	
  3684	            for _ in range(nfiles):
  3685	                code = self.unpack_uint8()
  3686	                name = self.unpack_string()
  3687	                size = self.unpack_file_size()
  3688	                ext_len = self.unpack_uint32()  # Obsolete, ignore
  3689	                self._offset += ext_len
  3690	                attrs = self.unpack_file_attributes()
  3691	
  3692	                folders[directory].append((code, name, size, ext, attrs))
  3693	
  3694	            if nfiles > 1:
  3695	                folders[directory].sort(key=itemgetter(1))
  3696	
  3697	        self.list = folders
  3698	
  3699	    def make_network_message(self):
  3700	        msg = bytearray()
  3701	        msg += self.pack_uint32(self.token)
  3702	        msg += self.pack_string(self.dir)
  3703	
  3704	        if self.list is not None:
  3705	            msg += self.pack_uint32(1)
  3706	            msg += self.pack_string(self.dir)
  3707	
  3708	            # We already saved the folder contents as a bytearray when scanning our shares
  3709	            msg += self.list
  3710	        else:
  3711	            # No folder contents
  3712	            msg += self.pack_uint32(0)
  3713	
  3714	        return zlib.compress(msg, ZLIB_COMPRESSION_LEVEL)
  3715	
```

### pynicotine/slskmessages.py:3717-3944
```text
  3717	class TransferRequest(PeerMessage):
  3718	    """Peer code 40.
  3719	
  3720	    This message is sent by a peer once they are ready to start
  3721	    uploading a file. A TransferResponse message is expected from the
  3722	    recipient, either allowing or rejecting the upload attempt.
  3723	
  3724	    This message was formerly used to send a download request (direction
  3725	    0) as well, but Nicotine+ >= 3.0.3, Museek+ and the official clients
  3726	    use the QueueUpload message for this purpose today.  Clients like
  3727	    slskd and Seeker still use this method for downloading, so we need to
  3728	    ensure we still understand such requests.
  3729	    """
  3730	
  3731	    __slots__ = ("direction", "token", "file", "filesize")
  3732	
  3733	    def __init__(self, direction=None, token=None, file=None, filesize=None, *, msg_content=None):
  3734	        PeerMessage.__init__(self, msg_content)
  3735	        self.direction = direction
  3736	        self.token = token
  3737	        self.file = file  # virtual file
  3738	        self.filesize = filesize
  3739	
  3740	    def make_network_message(self):
  3741	        msg = bytearray()
  3742	        msg += self.pack_uint32(self.direction)
  3743	        msg += self.pack_uint32(self.token)
  3744	        msg += self.pack_string(self.file)
  3745	
  3746	        if self.direction == TransferDirection.UPLOAD:
  3747	            msg += self.pack_uint64(self.filesize)
  3748	
  3749	        return msg
  3750	
  3751	    def parse_network_message(self):
  3752	        self.direction = self.unpack_uint32()
  3753	        self.token = self.unpack_uint32()
  3754	        self.file = self.unpack_string()
  3755	
  3756	        if self.direction == TransferDirection.UPLOAD:
  3757	            self.filesize = self.unpack_uint64()
  3758	
  3759	
  3760	class TransferResponse(PeerMessage):
  3761	    """Peer code 41.
  3762	
  3763	    Response to TransferRequest - We either accept the transfer request,
  3764	    or tell the reason for rejecting it.
  3765	
  3766	    Note that accepting a download request is discouraged, since it allows
  3767	    a possibly spoofed peer to initialize the file transfer connection
  3768	    from their end. Reject the download request with a 'Queued' reason, add
  3769	    the ile to the upload queue, and start the next upload as usual, since
  3770	    it ensures a connection attempt to a valid user address provided by the
  3771	    server.
  3772	    """
  3773	
  3774	    __slots__ = ("allowed", "token", "reason", "filesize")
  3775	
  3776	    def __init__(self, allowed=None, reason=None, token=None, filesize=None, *, msg_content=None):
  3777	        PeerMessage.__init__(self, msg_content)
  3778	        self.allowed = allowed
  3779	        self.token = token
  3780	        self.reason = reason
  3781	        self.filesize = filesize
  3782	
  3783	    def make_network_message(self):
  3784	        msg = bytearray()
  3785	        msg += self.pack_uint32(self.token)
  3786	        msg += self.pack_bool(self.allowed)
  3787	
  3788	        if self.reason is not None:
  3789	            msg += self.pack_string(self.reason)
  3790	
  3791	        if self.filesize is not None:
  3792	            msg += self.pack_uint64(self.filesize)
  3793	
  3794	        return msg
  3795	
  3796	    def parse_network_message(self):
  3797	        self.token = self.unpack_uint32()
  3798	        self.allowed = self.unpack_bool()
  3799	
  3800	        if not self.has_remaining_content():
  3801	            return
  3802	
  3803	        if self.allowed:
  3804	            self.filesize = self.unpack_uint64()
  3805	        else:
  3806	            self.reason = self.unpack_string()
  3807	
  3808	
  3809	class PlaceholdUpload(PeerMessage):
  3810	    """Peer code 42.
  3811	
  3812	    OBSOLETE, no longer used
  3813	    """
  3814	
  3815	    __slots__ = ("file",)
  3816	
  3817	    def __init__(self, file=None, *, msg_content=None):
  3818	        PeerMessage.__init__(self, msg_content)
  3819	        self.file = file
  3820	
  3821	    def make_network_message(self):
  3822	        return self.pack_string(self.file)
  3823	
  3824	    def parse_network_message(self):
  3825	        self.file = self.unpack_string()
  3826	
  3827	
  3828	class QueueUpload(PeerMessage):
  3829	    """Peer code 43.
  3830	
  3831	    This message is used to tell a peer that an upload should be queued
  3832	    on their end. Once the recipient is ready to transfer the requested
  3833	    file, they will send a TransferRequest to us.
  3834	    """
  3835	
  3836	    __slots__ = ("file", "legacy_client")
  3837	
  3838	    def __init__(self, file=None, legacy_client=False, *, msg_content=None):
  3839	        PeerMessage.__init__(self, msg_content)
  3840	        self.file = file
  3841	        self.legacy_client = legacy_client
  3842	
  3843	    def make_network_message(self):
  3844	        return self.pack_string(self.file, is_legacy=self.legacy_client)
  3845	
  3846	    def parse_network_message(self):
  3847	        self.file = self.unpack_string()
  3848	
  3849	
  3850	class PlaceInQueueResponse(PeerMessage):
  3851	    """Peer code 44.
  3852	
  3853	    The peer replies with the upload queue placement of the requested
  3854	    file.
  3855	    """
  3856	
  3857	    __slots__ = ("filename", "place")
  3858	
  3859	    def __init__(self, filename=None, place=None, *, msg_content=None):
  3860	        PeerMessage.__init__(self, msg_content)
  3861	        self.filename = filename
  3862	        self.place = place
  3863	
  3864	    def make_network_message(self):
  3865	        msg = bytearray()
  3866	        msg += self.pack_string(self.filename)
  3867	        msg += self.pack_uint32(self.place)
  3868	
  3869	        return msg
  3870	
  3871	    def parse_network_message(self):
  3872	        self.filename = self.unpack_string()
  3873	        self.place = self.unpack_uint32()
  3874	
  3875	
  3876	class UploadFailed(PeerMessage):
  3877	    """Peer code 46.
  3878	
  3879	    This message is sent whenever a file connection of an active upload
  3880	    closes. Soulseek NS clients can also send this message when a file
  3881	    cannot be read. The recipient either re-queues the upload (download
  3882	    on their end), or ignores the message if the transfer finished.
  3883	    """
  3884	
  3885	    __slots__ = ("file",)
  3886	
  3887	    def __init__(self, file=None, *, msg_content=None):
  3888	        PeerMessage.__init__(self, msg_content)
  3889	        self.file = file
  3890	
  3891	    def make_network_message(self):
  3892	        return self.pack_string(self.file)
  3893	
  3894	    def parse_network_message(self):
  3895	        self.file = self.unpack_string()
  3896	
  3897	
  3898	class UploadDenied(PeerMessage):
  3899	    """Peer code 50.
  3900	
  3901	    This message is sent to reject QueueUpload attempts and previously
  3902	    queued files. The reason for rejection will appear in the transfer
  3903	    list of the recipient.
  3904	    """
  3905	
  3906	    __slots__ = ("file", "reason")
  3907	
  3908	    def __init__(self, file=None, reason=None, *, msg_content=None):
  3909	        PeerMessage.__init__(self, msg_content)
  3910	        self.file = file
  3911	        self.reason = reason
  3912	
  3913	    def make_network_message(self):
  3914	        msg = bytearray()
  3915	        msg += self.pack_string(self.file)
  3916	        msg += self.pack_string(self.reason)
  3917	
  3918	        return msg
  3919	
  3920	    def parse_network_message(self):
  3921	        self.file = self.unpack_string()
  3922	        self.reason = self.unpack_string()
  3923	
  3924	
  3925	class PlaceInQueueRequest(PeerMessage):
  3926	    """Peer code 51.
  3927	
  3928	    This message is sent when asking for the upload queue placement of a
  3929	    file.
  3930	    """
  3931	
  3932	    __slots__ = ("file", "legacy_client")
  3933	
  3934	    def __init__(self, file=None, legacy_client=False, *, msg_content=None):
  3935	        PeerMessage.__init__(self, msg_content)
  3936	        self.file = file
  3937	        self.legacy_client = legacy_client
  3938	
  3939	    def make_network_message(self):
  3940	        return self.pack_string(self.file, is_legacy=self.legacy_client)
  3941	
  3942	    def parse_network_message(self):
  3943	        self.file = self.unpack_string()
  3944	
```

### pynicotine/uploads.py:911-970
```text
   911	    def _queue_upload(self, msg):
   912	        """Peer code 43.
   913	
   914	        Peer remotely queued a download (upload here). This is the
   915	        modern replacement to a TransferRequest with direction 0
   916	        (download request). We will initiate the upload of the queued
   917	        file later.
   918	        """
   919	
   920	        username = msg.username
   921	        virtual_path = msg.file
   922	        allowed, reason, real_path, size = self._check_queue_upload_allowed(username, msg.addr, virtual_path, msg)
   923	        is_backslash_path = False
   924	        is_lowercase_path = False
   925	
   926	        if reason == TransferRejectReason.FILE_NOT_SHARED:
   927	            real_path_index = core.shares.get_lowercase_path_index(virtual_path)
   928	
   929	            if real_path_index is not None:
   930	                # Soulseek NS client erroneously converted the virtual path to lowercase.
   931	                # Retrieve the real path anyway.
   932	                real_path = core.shares.file_path_index[real_path_index]
   933	                allowed, size = core.shares.file_is_shared(username, virtual_path, real_path)
   934	                is_lowercase_path = True
   935	
   936	                if allowed:
   937	                    reason = None
   938	            else:
   939	                # Possibly a file path with a backslash sentinel that should be substituted
   940	                allowed, real_path_reverted, size = self._check_backslash_path_exists(username, virtual_path)
   941	
   942	                if allowed:
   943	                    is_backslash_path = True
   944	                    real_path = real_path_reverted
   945	                    reason = None
   946	
   947	        log.add_transfer("Upload request for file %s from user: %s, allowed: %s, "
   948	                         "reason: %s", (virtual_path, username, allowed, reason))
   949	
   950	        if not allowed:
   951	            if reason and reason != TransferRejectReason.QUEUED:
   952	                core.send_message_to_peer(username, UploadDenied(virtual_path, reason))
   953	
   954	            return
   955	
   956	        transfer = self.transfers.get(username + virtual_path)
   957	        folder_path = os.path.dirname(real_path)
   958	
   959	        if transfer is not None:
   960	            self._unfail_transfer(transfer)
   961	
   962	            transfer.folder_path = folder_path
   963	            transfer.size = size
   964	
   965	            if transfer.status == TransferStatus.FINISHED:
   966	                transfer.current_byte_offset = None
   967	                transfer.transferred_bytes_total = 0
   968	                transfer.speed = transfer.avg_speed = transfer.time_elapsed = transfer.time_left = 0
   969	        else:
   970	            transfer = Transfer(username, virtual_path, folder_path, size)
```

### pynicotine/uploads.py:984-1068
```text
   984	    def _transfer_request(self, msg):
   985	        """Peer code 40."""
   986	
   987	        username = msg.username
   988	
   989	        if msg.direction != TransferDirection.DOWNLOAD:
   990	            return
   991	
   992	        response = self._transfer_request_uploads(msg)
   993	
   994	        if response is None:
   995	            return
   996	
   997	        log.add_transfer("Responding to legacy upload request %s for file %s from user %s, "
   998	                         "allowed: %s, reason: %s",
   999	                         (response.token, msg.file, username, response.allowed, response.reason))
  1000	
  1001	        core.send_message_to_peer(username, response)
  1002	
  1003	        if response.reason == TransferRejectReason.QUEUED:
  1004	            self._check_upload_queue()
  1005	
  1006	    def _transfer_request_uploads(self, msg):
  1007	        """Remote peer is requesting to download a file through your upload
  1008	        queue.
  1009	
  1010	        Note that the QueueUpload peer message has replaced this method
  1011	        of requesting a download in most clients.
  1012	        """
  1013	
  1014	        username = msg.username
  1015	        virtual_path = msg.file
  1016	        token = msg.token
  1017	        is_backslash_path = False
  1018	
  1019	        log.add_transfer("Received legacy upload request %s for file %s from user %s",
  1020	                         (token, virtual_path, username))
  1021	
  1022	        # Is user allowed to download?
  1023	        allowed, reason, real_path, size = self._check_queue_upload_allowed(username, msg.addr, virtual_path, msg)
  1024	
  1025	        if reason == TransferRejectReason.FILE_NOT_SHARED:
  1026	            # Possibly a file path with a backslash sentinel that should be substituted
  1027	            allowed, real_path_reverted, size = self._check_backslash_path_exists(username, virtual_path)
  1028	
  1029	            if allowed:
  1030	                is_backslash_path = True
  1031	                real_path = real_path_reverted
  1032	                reason = None
  1033	
  1034	        if not allowed:
  1035	            if reason:
  1036	                return TransferResponse(allowed=False, reason=reason, token=token)
  1037	
  1038	            return None
  1039	
  1040	        # All checks passed, user can queue file!
  1041	        transfer = self.transfers.get(username + virtual_path)
  1042	        folder_path = os.path.dirname(real_path)
  1043	
  1044	        if transfer is not None:
  1045	            self._unfail_transfer(transfer)
  1046	
  1047	            transfer.folder_path = folder_path
  1048	            transfer.size = size
  1049	
  1050	            if transfer.status == TransferStatus.FINISHED:
  1051	                transfer.current_byte_offset = None
  1052	                transfer.transferred_bytes_total = 0
  1053	                transfer.speed = transfer.avg_speed = transfer.time_elapsed = transfer.time_left = 0
  1054	        else:
  1055	            transfer = Transfer(username, virtual_path, folder_path, size)
  1056	            self._append_transfer(transfer)
  1057	
  1058	        transfer.is_backslash_path = is_backslash_path
  1059	
  1060	        self._enqueue_transfer(transfer, show_notification=True)
  1061	        self._update_transfer(transfer)
  1062	
  1063	        # Must be emitted after the final update to prevent inconsistent state
  1064	        core.pluginhandler.upload_queued_notification(username, virtual_path, real_path)
  1065	
  1066	        return TransferResponse(allowed=False, reason=TransferRejectReason.QUEUED, token=token)
  1067	
  1068	    def _transfer_response(self, msg):
```

### pynicotine/uploads.py:1272-1334
```text
  1272	    def _place_in_queue_request(self, msg):
  1273	        """Peer code 51."""
  1274	
  1275	        username = msg.username
  1276	        virtual_path = msg.file
  1277	        upload = self.queued_users.get(username, {}).get(virtual_path)
  1278	
  1279	        if upload is None:
  1280	            return
  1281	
  1282	        is_fifo_queue = config.sections["transfers"]["fifoqueue"]
  1283	        is_privileged_queue = self.is_privileged(username)
  1284	        privileged_queued_users = {k: len(v) for k, v in self.queued_users.items() if self.is_privileged(k)}
  1285	        queue_position = 0
  1286	
  1287	        if is_fifo_queue:
  1288	            if is_privileged_queue != self._privileged_position_requested or upload not in self._queue_positions:
  1289	                self._queue_position_users.clear()
  1290	
  1291	                if is_privileged_queue:
  1292	                    self._queue_positions.clear()
  1293	                    position = 1
  1294	
  1295	                    for i_upload in self.queued_transfers:
  1296	                        if i_upload.username in privileged_queued_users:
  1297	                            self._queue_positions[i_upload] = position
  1298	                            position += 1
  1299	                else:
  1300	                    self._queue_positions = {
  1301	                        i_upload: position
  1302	                        for position, i_upload in enumerate(self.queued_transfers, start=1)
  1303	                    }
  1304	
  1305	            queue_position = self._queue_positions[upload]
  1306	        else:
  1307	            user_queue_positions = self._queue_position_users[username]
  1308	
  1309	            if upload not in user_queue_positions:
  1310	                self._queue_positions.clear()
  1311	                user_queue_positions.update({
  1312	                    i_upload: position
  1313	                    for position, i_upload in enumerate(self.queued_users[username].values(), start=1)
  1314	                })
  1315	
  1316	            if is_privileged_queue:
  1317	                num_queued_users = len(privileged_queued_users)
  1318	            else:
  1319	                # Cycling through privileged users first
  1320	                queue_position += sum(
  1321	                    num_queued_uploads for num_queued_uploads in privileged_queued_users.values())
  1322	                num_queued_users = len(self.queued_users)
  1323	
  1324	            queue_position += num_queued_users + user_queue_positions[upload]
  1325	
  1326	        self._privileged_position_requested = is_privileged_queue
  1327	
  1328	        if queue_position > 0:
  1329	            core.send_message_to_peer(
  1330	                username, PlaceInQueueResponse(virtual_path, queue_position))
  1331	
  1332	        # Update queue position in our list of uploads
  1333	        upload.queue_position = queue_position
  1334	        self._update_transfer(upload, update_parent=False)
```

### pynicotine/shares.py:1361-1384
```text
  1361	    def _folder_contents_request(self, msg):
  1362	        """Peer code 36."""
  1363	
  1364	        ip_address, _port = msg.addr
  1365	        username = msg.username
  1366	        folder_path = msg.dir
  1367	        permission_level, _reject_reason = self.check_user_permission(username, ip_address)
  1368	        folder_data = None
  1369	
  1370	        if permission_level != PermissionLevel.BANNED:
  1371	            folder_data = self.share_dbs.get("public_streams", {}).get(folder_path)
  1372	
  1373	            if (folder_data is None
  1374	                    and (config.sections["transfers"]["reveal_buddy_shares"]
  1375	                         or permission_level in {PermissionLevel.BUDDY, PermissionLevel.TRUSTED})):
  1376	                folder_data = self.share_dbs.get("buddy_streams", {}).get(folder_path)
  1377	
  1378	            if (folder_data is None
  1379	                    and (config.sections["transfers"]["reveal_trusted_shares"]
  1380	                         or permission_level == PermissionLevel.TRUSTED)):
  1381	                folder_data = self.share_dbs.get("trusted_streams", {}).get(folder_path)
  1382	
  1383	        core.send_message_to_peer(
  1384	            username, FolderContentsResponse(directory=folder_path, token=msg.token, shares=folder_data))
```


