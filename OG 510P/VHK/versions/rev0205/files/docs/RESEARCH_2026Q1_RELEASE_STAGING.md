# Research notes: release staging

The Linux automation ecosystem keeps reinforcing that startup and delivery are file-tree problems, not only runtime decisions. Desktop-entry/autostart flows want `.desktop` files in standard locations, service-managed text tools want user-service lifecycle, and remapper/helper lanes want daemon/service ownership.

That suggests a useful VHK product rule: once release lanes and deploy styles exist, the next artifact should not be another matrix. It should be a stage tree that gives maintainers one folder per lane containing the commands and payload paths they are expected to review, ship, or hand to another operator.
