---
id: '16'
revision_added: pre_rev0269
status: canon
object_type: doctrine
domain_tags: []
service_floor: []
hazard_tags: []
clock_tags: []
actor_tags: []
instrument_tags: []
routes_to:
- '267'
- '287'
- '288'
- '297'
- '298'
- '299'
- '300'
source_ids:
- S16
- S17
- S28
- S51
- S52
- S53
- S54
- S161
- S162
- S431
- S432
- S437
- S438
- S441
- S502
- S515
- S525
upstream_dependencies: []
downstream_consequences: []
equity_lenses: []
degraded_modes: []
evidence_grade: mixed
speculation_level: mixed
---
# 16 — Buildings, Retrofits, and Clean Heat

## Claim

Buildings are not a minor subtopic under efficiency. They are a **core climate lane** because they combine:
- large direct and indirect emissions
- long asset lives and lock-in risk
- heating, cooling, appliance, and cooking demand
- health, comfort, and affordability
- resilience during heat, cold, smoke, and outages

UNEP’s latest buildings review says buildings and construction consume **32% of global energy** and contribute **34% of global CO2 emissions** [S28]. IEA’s 2025 efficiency work says buildings account for around **30% of global energy demand** and about **20% of the growth in total energy demand since 2019** [S51].

## Why the archive upgrades buildings

The archive already treated cooling, industrial materials, and clean electricity as central. But buildings were still scattered across those files instead of appearing as one coherent lane.

That matters because buildings split into two distinct strategic problems:

1. **Advanced economies:** much of the 2050 stock already exists, so the main task is retrofit and clean heat. IEA’s 2025 buildings work says **80% of the 2050 building stock in advanced economies has already been built** [S54].
2. **Emerging and developing economies:** floor area is still expanding quickly, so the main task is to avoid locking in bad design, weak envelopes, inefficient cooling, and polluting cooking systems. IEA says **80% of floor-area growth to 2050 is expected in developing economies**, and many of these economies still lack robust building and energy codes [S54].

A serious climate archive therefore needs explicit doctrine for **existing-stock retrofits, efficient new construction, heat pumps, appliance standards, and clean cooking**.

## House doctrine

### 1. Envelope first, equipment second
The cheapest heating or cooling demand is the demand avoided through insulation, airtightness, shading, passive design, reflective surfaces, ventilation, and better windows. Replacing boilers or ACs without improving the envelope leaves structural waste in place.

### 2. New buildings should be built right the first time
In fast-growing markets, weak building codes create decades of avoidable demand. IEA says building energy codes currently apply to only **around half of new floor area in emerging economies** [S51]. The archive therefore treats stronger codes, enforcement, and urban design as core climate policy, not technical housekeeping.

### 3. Heat pumps are the central clean-heat technology
IEA describes heat pumps as the central technology in the transition to secure and sustainable heating [S52]. Yet they still meet only **around 10% of global heating needs in buildings**, and the global stock would need to **almost triple by 2030** to cover **at least 20% of global heating needs** in a net-zero-consistent pathway [S52].

### 4. Buildings need flexibility, not just efficiency
Connected controls, smart tariffs, thermal storage, and demand response make buildings easier to run on clean power and reduce peak stress. IEA’s 2025 toolkit specifically recommends connected controls, updated building codes, and tariff reform so heat pumps help the grid rather than merely add load [S53].

### 5. Retrofit delivery is an institutional problem
The bottleneck is rarely the physics of insulation. It is split incentives, financing, workforce shortages, landlord-tenant problems, fragmented contractors, and household hassle. The archive therefore favors one-stop shops, standard retrofit packages, public and concessional finance, social-housing-first deployment, and installer training rather than boutique subsidy schemes [S53][S54]. It now adds a timing corollary too: building policy should be designed around **trigger points** such as sale, rental, major renovation, refinancing, re-roofing, and equipment failure, because OECD’s 2025 property work shows that sales and rental trigger points can embed performance compliance in routine transaction cycles, and IEA’s 2025 buildings toolkit says replacing fossil-fuel boilers with heat pumps can sharply cut energy use at the moment equipment is already being changed [S161][S162].

### 6. Buildings doctrine must differ by region
- In colder, richer countries: retrofit existing stock, replace fossil heating, and reform the gas-versus-electricity price gap [S51][S53].
- In hotter, urbanizing countries: efficient new construction, passive cooling, efficient ACs and fans, urban heat reduction, and stronger grid planning matter more [S16][S17][S51].
- In lower-income settings still reliant on traditional biomass: clean cooking belongs inside the buildings lane because it improves health, reduces energy poverty, and avoids locking in inefficient fuel use [S51].

### 7. Public buildings should lead
Schools, hospitals, public housing, and municipal buildings should be early retrofit and clean-heat targets because they create visible benefit, reduce public energy bills, improve resilience, and help scale supply chains.

## Minimum package for buildings

A serious climate program should include at least:
- mandatory ratcheting building energy codes for new construction
- large-scale retrofit programs for existing stock, with special attention to low-income and rental housing
- rapid heat-pump deployment with connected controls where appropriate
- appliance and equipment standards for heating, cooling, water heating, and cooking
- financing reform: low-cost loans, grants, on-bill approaches, green mortgages, and public retrofit vehicles
- workforce expansion for installers, auditors, designers, and inspectors
- public-building retrofits as anchor demand
- explicit clean-cooking programs where biomass and dirty fuels still dominate

## What the archive rejects

- treating “green buildings” as mainly a premium niche for new elite construction
- solving heat only by swapping appliances while leaving bad envelopes untouched
- locking in new gas infrastructure for buildings on the theory that it can be cleaned up later
- separating cooling, heating, cooking, resilience, and affordability into unrelated policy silos
- assuming retrofit rates rise automatically without delivery institutions and finance

## Compression

**Buildings are where climate policy becomes lived reality. Solve buildings badly and the world locks in waste, peak demand, fossil heat, and thermal vulnerability for decades. Solve them well and the same sector delivers emissions cuts, affordability, resilience, and health at once.**

## Rev0262 addendum — buildings policy must prove habitability, affordability, and non-displacement

Rev0262 separates a frequent confusion. A technically good building retrofit is not automatically a good housing outcome. The retrofit must also preserve or improve habitability, affordability, accessibility, tenure security, and household continuity.

Buildings packets should therefore add housing fields: renter protections, landlord compliance, indoor heat / cold and clean-air performance, mold and moisture control, accessibility, utility affordability, public-housing priority, informal-settlement relevance, repair-market capacity, and anti-displacement conditions on public subsidies. See `287` and `288` [S431][S432][S437][S438][S441].

## Rev0267 buildings bridge — habitability during outages

Building retrofits now have an outage metric. A retrofit is stronger when it keeps homes, schools, shelters, care sites, and workplaces survivable for longer without grid power, reduces critical cooling / heating load, protects elevators and medical devices where relevant, and lowers bills that otherwise turn into shutoff risk. Use `297` and `298` for the critical-load and backup-power proof. [S502] [S515]

## Rev0268 buildings bridge — retrofits should reduce future debris and mold

Building doctrine now includes disaster-debris prevention and mold-safe design: floodable materials, drying paths, elevated equipment, resilient roofs, fire-safe assemblies, deconstruction planning, material passports, and repairable components reduce future debris and cleanup burden. Pair with `299`, `300`, and `267`. [S525]

---
Citations point to `sources/register.md`.
