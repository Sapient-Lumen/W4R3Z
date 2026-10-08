# Funding transparency and legal structure

**Track:** A (Deployable core)


Governance failure often comes from money and legal leverage, not cryptography.

## Threats

* donor capture
* vendor capture via "free" managed services
* jurisdictional coercion (subpoenas, gag orders)

## Requirements

### FUND-1 Funding disclosure
Witness operators MUST publish periodic **Funding Transparency Reports** (schema `FundingTransparencyReport.json`) including:

* funding sources (bucketed where necessary for privacy)
* non-financial support (cloud credits, staff secondments)
* material contracts with election vendors

### FUND-2 Structural independence
Witness operators SHOULD be incorporated in a structure that supports independence (e.g., non-profit with independent board). Jurisdictional concentration SHOULD be avoided.

### FUND-3 Liability and safe harbor
The governance charter SHOULD define safe harbor for good-faith monitoring disclosures and protect monitors/witnesses from retaliatory actions.