# Scenario: Flume cloned receivers still compete for single delivery

This scenario exists to prove that **cloneable receivers** do not automatically imply broadcast semantics.

Current docs say cloning a Flume receiver does not turn the channel into a broadcast channel and each message will only be received by a single receiver.

The fixture should fail any classifier that equates receiver cloning with multi-receiver fanout.
