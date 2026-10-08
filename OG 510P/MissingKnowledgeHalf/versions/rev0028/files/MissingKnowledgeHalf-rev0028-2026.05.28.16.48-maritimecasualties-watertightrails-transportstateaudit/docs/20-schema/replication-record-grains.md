# Replication record grains

Revision: rev0012

The cube now separates several replication grains:

| Grain | Description | Rev0012 examples |
| --- | --- | --- |
| single-protocol RRR | One original finding or protocol, many labs, shared vetted protocol | `MKH-REP-0001`, `MKH-REP-0006` |
| multi-effect many-labs map | Many target effects, many samples/settings | `MKH-REP-0007`, `MKH-REP-0008` |
| replication-program parent | A field/program-level parent with many intended experiments | `MKH-REP-0005`, `MKH-REP-0009` |
| successful-control replication | A robust effect record included to calibrate the failure lane | `MKH-REP-0010` |
| infrastructure rail | Publication, coordination, or findability machinery | `MKH-INF-0020` through `MKH-INF-0023` |

Each promoted REP record must include `original_sampling_frame`, `replication_metrics`, and `status_cautions` inside `type_payload`.
