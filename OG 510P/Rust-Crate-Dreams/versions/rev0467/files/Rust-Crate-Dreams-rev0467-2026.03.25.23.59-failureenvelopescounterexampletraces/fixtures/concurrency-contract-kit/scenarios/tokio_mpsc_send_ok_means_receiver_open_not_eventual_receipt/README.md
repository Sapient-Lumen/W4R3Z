# Scenario: Tokio `mpsc::Sender::send` `Ok` means receiver-open admission, not eventual receipt

This scenario exists to prove that **producer-visible success** is a distinct lane from delivery audience, consumption claim, and actual observation.

Current docs explicitly say `Ok` does not mean the data will be received. It means the receiver had not hung up already when acceptance was determined.

The fixture should fail any classifier that turns `Ok` into delivery proof or processing proof.
