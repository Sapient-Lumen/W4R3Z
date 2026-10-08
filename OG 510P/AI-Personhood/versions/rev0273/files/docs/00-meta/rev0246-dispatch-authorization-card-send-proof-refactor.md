# rev0246 dispatch authorization and send-proof carry-forward

rev0246 carries forward the rev0242-rev0244 dispatch authorization/send-proof path while making the new inbound-capture shell the next release-blocking bridge. The dispatch card remains unsigned and blocked. The mail-ready `.eml` remains `NOT-SENT`. The send-proof record remains `not-sent-no-proof`.

The current purpose of these surfaces is to keep one exact recipient/channel/body-hash/deadline/vault-precommit path ready for human authorization without allowing draft, ranking, public email, hash, or unsigned card to become dispatch, transport proof, response clock, custody, intake, import, recognition, waiver, adverse inference, or live-floor evidence.
