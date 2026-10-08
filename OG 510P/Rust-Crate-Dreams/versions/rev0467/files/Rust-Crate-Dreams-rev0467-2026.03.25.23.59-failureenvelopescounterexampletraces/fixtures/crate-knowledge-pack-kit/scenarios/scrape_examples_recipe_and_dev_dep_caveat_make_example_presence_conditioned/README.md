# Scenario: scrape-examples recipe and dev-dependency caveat make example presence conditioned

Problem:
A tool sees scraped examples in docs output and is about to assume those examples are always present whenever the crate is documented.

What this scenario proves:
Example presence can depend on recipe details such as target-level scraping enablement and dev-dependency posture.

Good outcome:
The bundle marks the example surface as recipe-bound and records the scrape-mode caveat instead of silently upgrading it to universal example truth.
