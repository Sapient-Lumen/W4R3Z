# rev0028 source trace — SEARCH-SEND-POLICY-01

Scope: inbound server/distributed search request handlers, response permission check, and plugin notification order.

## github-tag-3.3.10

Relevant line hits:

```text
475: def _file_search_request_server
481: def _file_search_request_distributed
661: def _process_search_request
698: core.shares.check_user_permission(username)
750: core.send_message_to_peer(username, FileSearchResponse
```

### `github-tag-3.3.10/pynicotine/search.py:475-486`

```python
475:     def _file_search_request_server(self, msg):
476:         """Server code 26."""
477: 
478:         self._process_search_request(msg.searchterm, msg.search_username, msg.token)
479:         core.pluginhandler.search_request_notification(msg.searchterm, msg.search_username, msg.token)
480: 
481:     def _file_search_request_distributed(self, msg):
482:         """Distrib code 3."""
483: 
484:         self._process_search_request(msg.searchterm, msg.search_username, msg.token)
485:         core.pluginhandler.distrib_search_notification(msg.searchterm, msg.search_username, msg.token)
486: 
```

### `github-tag-3.3.10/pynicotine/search.py:661-706`

```python
661:     def _process_search_request(self, search_term, username, token):
662:         """This section is accessed every time a search request arrives,
663:         several times per second.
664: 
665:         Please keep it as optimized and memory sparse as possible!
666:         """
667: 
668:         if not search_term:
669:             return
670: 
671:         if not config.sections["searches"]["search_results"]:
672:             # Don't return _any_ results when this option is disabled
673:             return
674: 
675:         if core.uploads.pending_shutdown:
676:             # Don't return results when waiting to quit after finishing uploads
677:             return
678: 
679:         local_username = core.users.login_username
680: 
681:         if username == local_username:
682:             if token not in self._own_tokens:
683:                 # We shouldn't send a search response if we initiated the search
684:                 # request, unless we're specifically searching our own username
685:                 return
686: 
687:             self._own_tokens.discard(token)
688: 
689:         max_results = config.sections["searches"]["maxresults"]
690: 
691:         if max_results <= 0:
692:             return
693: 
694:         if len(search_term) < config.sections["searches"]["min_search_chars"]:
695:             # Don't send search response if search term contains too few characters
696:             return
697: 
698:         permission_level, _reject_reason = core.shares.check_user_permission(username)
699: 
700:         if permission_level == PermissionLevel.BANNED:
701:             return
702: 
703:         if "words" not in core.shares.share_dbs:
704:             return
705: 
706:         word_index = core.shares.share_dbs["words"]
```

### `github-tag-3.3.10/pynicotine/search.py:750-762`

```python
750:         core.send_message_to_peer(username, FileSearchResponse(
751:             search_username=local_username,
752:             token=token,
753:             shares=fileinfos,
754:             freeulslots=core.uploads.is_new_upload_accepted(),
755:             ulspeed=core.uploads.upload_speed,
756:             inqueue=core.uploads.get_upload_queue_size(username),
757:             private_shares=private_fileinfos
758:         ))
759: 
760:         log.add_search(_('User %(user)s is searching for "%(query)s", found %(num)i results'), {
761:             "user": username,
762:             "query": original_search_term,
```

## github-branch-3.3.x

Relevant line hits:

```text
475: def _file_search_request_server
481: def _file_search_request_distributed
658: def _process_search_request
695: core.shares.check_user_permission(username)
747: core.send_message_to_peer(username, FileSearchResponse
```

### `github-branch-3.3.x/pynicotine/search.py:475-486`

```python
475:     def _file_search_request_server(self, msg):
476:         """Server code 26."""
477: 
478:         self._process_search_request(msg.searchterm, msg.search_username, msg.token)
479:         core.pluginhandler.search_request_notification(msg.searchterm, msg.search_username, msg.token)
480: 
481:     def _file_search_request_distributed(self, msg):
482:         """Distrib code 3."""
483: 
484:         self._process_search_request(msg.searchterm, msg.search_username, msg.token)
485:         core.pluginhandler.distrib_search_notification(msg.searchterm, msg.search_username, msg.token)
486: 
```

### `github-branch-3.3.x/pynicotine/search.py:658-703`

```python
658:     def _process_search_request(self, search_term, username, token):
659:         """This section is accessed every time a search request arrives,
660:         several times per second.
661: 
662:         Please keep it as optimized and memory sparse as possible!
663:         """
664: 
665:         if not search_term:
666:             return
667: 
668:         if not config.sections["searches"]["search_results"]:
669:             # Don't return _any_ results when this option is disabled
670:             return
671: 
672:         if core.uploads.pending_shutdown:
673:             # Don't return results when waiting to quit after finishing uploads
674:             return
675: 
676:         local_username = core.users.login_username
677: 
678:         if username == local_username:
679:             if token not in self._own_tokens:
680:                 # We shouldn't send a search response if we initiated the search
681:                 # request, unless we're specifically searching our own username
682:                 return
683: 
684:             self._own_tokens.discard(token)
685: 
686:         max_results = config.sections["searches"]["maxresults"]
687: 
688:         if max_results <= 0:
689:             return
690: 
691:         if len(search_term) < config.sections["searches"]["min_search_chars"]:
692:             # Don't send search response if search term contains too few characters
693:             return
694: 
695:         permission_level, _reject_reason = core.shares.check_user_permission(username)
696: 
697:         if permission_level == PermissionLevel.BANNED:
698:             return
699: 
700:         if "words" not in core.shares.share_dbs:
701:             return
702: 
703:         word_index = core.shares.share_dbs["words"]
```

### `github-branch-3.3.x/pynicotine/search.py:747-759`

```python
747:         core.send_message_to_peer(username, FileSearchResponse(
748:             search_username=local_username,
749:             token=token,
750:             shares=fileinfos,
751:             freeulslots=core.uploads.is_new_upload_accepted(),
752:             ulspeed=core.uploads.upload_speed,
753:             inqueue=core.uploads.get_upload_queue_size(username),
754:             private_shares=private_fileinfos
755:         ))
756: 
757:         log.add_search(_('User %(user)s is searching for "%(query)s", found %(num)i results'), {
758:             "user": username,
759:             "query": original_search_term,
```

## github-branch-master

Relevant line hits:

```text
643: def _file_search_request_server
649: def _file_search_request_distributed
826: def _process_search_request
863: core.shares.check_user_permission(username)
915: core.send_message_to_peer(username, FileSearchResponse
```

### `github-branch-master/pynicotine/search.py:643-654`

```python
643:     def _file_search_request_server(self, msg):
644:         """Server code 26."""
645: 
646:         self._process_search_request(msg.searchterm, msg.search_username, msg.token)
647:         core.pluginhandler.search_request_notification(msg.searchterm, msg.search_username, msg.token)
648: 
649:     def _file_search_request_distributed(self, msg):
650:         """Distrib code 3."""
651: 
652:         self._process_search_request(msg.searchterm, msg.search_username, msg.token)
653:         core.pluginhandler.distrib_search_notification(msg.searchterm, msg.search_username, msg.token)
654: 
```

### `github-branch-master/pynicotine/search.py:826-871`

```python
826:     def _process_search_request(self, search_term, username, token):
827:         """This section is accessed every time a search request arrives,
828:         several times per second.
829: 
830:         Please keep it as optimized and memory sparse as possible!
831:         """
832: 
833:         if not search_term:
834:             return
835: 
836:         if not config.sections["searches"]["search_results"]:
837:             # Don't return _any_ results when this option is disabled
838:             return
839: 
840:         if core.uploads.pending_shutdown:
841:             # Don't return results when waiting to quit after finishing uploads
842:             return
843: 
844:         local_username = core.users.login_username
845: 
846:         if username == local_username:
847:             if token not in self._own_tokens:
848:                 # We shouldn't send a search response if we initiated the search
849:                 # request, unless we're specifically searching our own username
850:                 return
851: 
852:             self._own_tokens.discard(token)
853: 
854:         max_results = config.sections["searches"]["maxresults"]
855: 
856:         if max_results <= 0:
857:             return
858: 
859:         if len(search_term) < config.sections["searches"]["min_search_chars"]:
860:             # Don't send search response if search term contains too few characters
861:             return
862: 
863:         permission_level, _reject_reason = core.shares.check_user_permission(username)
864: 
865:         if permission_level == PermissionLevel.BANNED:
866:             return
867: 
868:         if "words" not in core.shares.share_dbs:
869:             return
870: 
871:         word_index = core.shares.share_dbs["words"]
```

### `github-branch-master/pynicotine/search.py:915-927`

```python
915:         core.send_message_to_peer(username, FileSearchResponse(
916:             search_username=local_username,
917:             token=token,
918:             shares=fileinfos,
919:             freeulslots=core.uploads.is_new_upload_accepted(),
920:             ulspeed=core.uploads.upload_speed,
921:             inqueue=core.uploads.get_upload_queue_size(username),
922:             private_shares=private_fileinfos
923:         ))
924: 
925:         log.add_search(
926:             ngettext(
927:                 'User %(user)s is searching for "%(query)s", found %(num)s result',
```

## `github-tag-3.3.10/pynicotine/shares.py:875-911`

```python
875:     def check_user_permission(self, username, ip_address=None):
876:         """Check if this user is banned, geoip-blocked, and which shares it is
877:         allowed to access based on transfer and shares settings."""
878: 
879:         if core.network_filter.is_user_banned(username) or core.network_filter.is_user_ip_banned(username, ip_address):
880:             if config.sections["transfers"]["usecustomban"]:
881:                 ban_message = config.sections["transfers"]["customban"]
882:                 return PermissionLevel.BANNED, ban_message
883: 
884:             return PermissionLevel.BANNED, ""
885: 
886:         user_data = core.buddies.users.get(username)
887: 
888:         if user_data:
889:             if user_data.is_trusted:
890:                 return PermissionLevel.TRUSTED, ""
891: 
892:             return PermissionLevel.BUDDY, ""
893: 
894:         if ip_address is None or not config.sections["transfers"]["geoblock"]:
895:             return PermissionLevel.PUBLIC, ""
896: 
897:         country_code = core.network_filter.get_country_code(ip_address)
898: 
899:         # Please note that all country codes are stored in the same string at the first index
900:         # of an array, separated by commas (no idea why this decision was made...)
901: 
902:         if country_code and config.sections["transfers"]["geoblockcc"][0].find(country_code) >= 0:
903:             if config.sections["transfers"]["usecustomgeoblock"]:
904:                 ban_message = config.sections["transfers"]["customgeoblock"]
905:                 return PermissionLevel.BANNED, ban_message
906: 
907:             return PermissionLevel.BANNED, ""
908: 
909:         return PermissionLevel.PUBLIC, ""
910: 
911:     def get_shared_folders(self):
```

## `github-branch-3.3.x/pynicotine/shares.py:882-918`

```python
882:     def check_user_permission(self, username, ip_address=None):
883:         """Check if this user is banned, geoip-blocked, and which shares it is
884:         allowed to access based on transfer and shares settings."""
885: 
886:         if core.network_filter.is_user_banned(username) or core.network_filter.is_user_ip_banned(username, ip_address):
887:             if config.sections["transfers"]["usecustomban"]:
888:                 ban_message = config.sections["transfers"]["customban"]
889:                 return PermissionLevel.BANNED, ban_message
890: 
891:             return PermissionLevel.BANNED, ""
892: 
893:         # Since username spoofing can't be fully prevented in the Soulseek protocol, only give
894:         # our own username a 'public' permission level, regardless of buddy status. It's quite
895:         # common for users to add themselves to their buddy list, making their own username the
896:         # easiest/most obvious choice for someone to spoof.
897: 
898:         if username != core.users.login_username:
899:             user_data = core.buddies.users.get(username)
900: 
901:             if user_data:
902:                 if user_data.is_trusted:
903:                     return PermissionLevel.TRUSTED, ""
904: 
905:                 return PermissionLevel.BUDDY, ""
906: 
907:         if ip_address is None or not config.sections["transfers"]["geoblock"]:
908:             return PermissionLevel.PUBLIC, ""
909: 
910:         country_code = core.network_filter.get_country_code(ip_address)
911: 
912:         # Please note that all country codes are stored in the same string at the first index
913:         # of an array, separated by commas (no idea why this decision was made...)
914: 
915:         if country_code and config.sections["transfers"]["geoblockcc"][0].find(country_code) >= 0:
916:             if config.sections["transfers"]["usecustomgeoblock"]:
917:                 ban_message = config.sections["transfers"]["customgeoblock"]
918:                 return PermissionLevel.BANNED, ban_message
```

## `github-branch-master/pynicotine/shares.py:967-1003`

```python
967:     def check_user_permission(self, username, ip_address=None):
968:         """Check if this user is banned, geoip-blocked, and which shares it is
969:         allowed to access based on transfer and shares settings."""
970: 
971:         if core.network_filter.is_user_banned(username) or core.network_filter.is_user_ip_banned(username, ip_address):
972:             if config.sections["transfers"]["usecustomban"]:
973:                 ban_message = config.sections["transfers"]["customban"]
974:                 return PermissionLevel.BANNED, ban_message
975: 
976:             return PermissionLevel.BANNED, ""
977: 
978:         # Since username spoofing can't be fully prevented in the Soulseek protocol, only give
979:         # our own username a 'public' permission level, regardless of buddy status. It's quite
980:         # common for users to add themselves to their buddy list, making their own username the
981:         # easiest/most obvious choice for someone to spoof.
982: 
983:         if username != core.users.login_username:
984:             user_data = core.buddies.users.get(username)
985: 
986:             if user_data:
987:                 if user_data.is_trusted:
988:                     return PermissionLevel.TRUSTED, ""
989: 
990:                 return PermissionLevel.BUDDY, ""
991: 
992:         if ip_address is None or not config.sections["transfers"]["geoblock"]:
993:             return PermissionLevel.PUBLIC, ""
994: 
995:         country_code = core.network_filter.get_country_code(ip_address)
996: 
997:         # Please note that all country codes are stored in the same string at the first index
998:         # of an array, separated by commas (no idea why this decision was made...)
999: 
1000:         if country_code and config.sections["transfers"]["geoblockcc"][0].find(country_code) >= 0:
1001:             if config.sections["transfers"]["usecustomgeoblock"]:
1002:                 ban_message = config.sections["transfers"]["customgeoblock"]
1003:                 return PermissionLevel.BANNED, ban_message
```

