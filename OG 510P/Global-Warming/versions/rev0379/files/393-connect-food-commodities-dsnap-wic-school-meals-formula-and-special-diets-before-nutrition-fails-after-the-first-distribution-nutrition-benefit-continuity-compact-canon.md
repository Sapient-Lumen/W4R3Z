---
id: '393'
revision_added: rev0280
status: canon
object_type: service_continuity
domain_tags:
- nutrition
- D-SNAP
- WIC
- school_meals
- commodities
- formula
- special_diets
- food_access
service_floor:
- nutrition_benefit_continuity
- food_access_after_distribution
- special_diet_and_infant_feeding_support
hazard_tags:
- compound_hazard
- flood
- wildfire
- heat
- smoke
- storm
- outage
- displacement
- disease
clock_tags:
- emergency_clock
- recovery_clock
- benefit_clock
- learning_clock
actor_tags:
- food_agency
- SNAP_agency
- WIC_agency
- school_food_authority
- shelter_operator
- retailer
- food_bank
- case_manager
instrument_tags:
- commodity_distribution
- D-SNAP
- benefit_replacement
- retailer_authorization
- school_meal_waiver
- infant_feeding_support
- special_diet_referral
routes_to:
- '275'
- '276'
- '281'
- '339'
- '380'
- '386'
- '389'
- '396'
source_ids:
- S706
- S707
upstream_dependencies:
- food_supply
- retailers
- payment_rails
- transport
- schools
- shelters
- social_registries
- public_information
downstream_consequences:
- hunger
- health_decline
- child_learning_loss
- shelter_conflict
- debt_or_asset_sale
- aid_distribution_crowding
equity_lenses:
- children
- infants
- pregnant_people
- older_adults
- disabled_people
- people_with_medical_diets
- limited_english_households
- no_car_households
- culturally_distinct_food_needs
degraded_modes:
- paper_vouchers
- mobile_food_delivery
- shelf_stable_special_diet_kits
- offline_EBT_or_cashout
- school_meal_pickup
- community_food_hub
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- retailers_closed
- EBT_or_payment_rails_down
- benefit_replacement_confusing
- D-SNAP_not_activated
- formula_unavailable
- special_diets_ignored
- transport_to_food_site_missing
failure_modes:
- food_boxes_do_not_match_diet_or_culture
- first_meal_distribution_ends_but_income_loss_remains
- school_meals_lost_due_to_displacement
- infants_or_medically_restricted_people_excluded
- cash_benefit_exists_but_store_is_unreachable
proof_ledgers:
- commodity_distribution_log
- D-SNAP_activation_and_application_log
- retailer_operability_map
- benefit_replacement_log
- school_meal_continuity_log
- formula_and_special_diet_exception_log
- food_access_complaint_log
nutrition_benefit_continuity: commodities, D-SNAP, replacement benefits, retailers, school meals, WIC/formula, special
  diets, and transport are linked to household need and case status
---

# 393 — Connect food commodities, D-SNAP, WIC, school meals, formula, and special diets before nutrition fails after the first distribution

## Core claim

Food after a disaster is not just pallets. Nutrition continuity must connect commodities, retailers, benefits, kitchens, school meals, WIC or equivalent supports, infant feeding, special diets, culturally appropriate food, transport, and household cash. Otherwise the first distribution becomes a visible success while hunger persists.

USDA's Food and Nutrition Service describes disaster food assistance including USDA Foods and Disaster SNAP, which can be requested when retail food stores are operating in impacted areas [S706]. FNS also maintains D-SNAP planning resources for state agencies and partners [S707]. The cube's rule is to treat those programs as rails in a nutrition pathway, not as isolated boxes.

## The nutrition packet

The minimum packet includes:

- immediate shelter and mobile meals;
- household food-box or commodity distribution with special-diet exceptions;
- replacement benefits where food was lost;
- D-SNAP or equivalent disaster food benefits where authorized;
- retailer operability and EBT / payment status;
- school meals, childcare meals, and summer / emergency feeding;
- infant formula, lactation support, medical diets, refrigeration, and safe water;
- transport or delivery for no-car, disabled, rural, and isolated households.

## Anti-pallet rule

A stockpile is not nutrition access. The archive should count food as accessible only when the person can reach it, use it, store it, digest it, and replace it on the next cycle.

## Cube rule

All food, shelter, school, cash, and commodity packets should expose `nutrition_benefit_continuity`. Blank means the archive should assume food distribution was counted but household nutrition was not proven.

---
Citations point to `sources/register.md`.
