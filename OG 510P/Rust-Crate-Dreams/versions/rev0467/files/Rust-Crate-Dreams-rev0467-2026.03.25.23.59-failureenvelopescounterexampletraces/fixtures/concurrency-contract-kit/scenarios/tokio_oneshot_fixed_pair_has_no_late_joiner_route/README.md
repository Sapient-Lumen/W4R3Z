# Scenario: Tokio `oneshot` is a fixed sender/receiver pair

This scenario exists to prove that some surfaces make join-start semantics effectively inapplicable because the consumer pair is fixed at creation.

Current docs say the channel function creates a Sender and Receiver handle pair that form the channel.

The fixture should fail any classifier that invents resubscribe or multi-receiver late-join semantics.
