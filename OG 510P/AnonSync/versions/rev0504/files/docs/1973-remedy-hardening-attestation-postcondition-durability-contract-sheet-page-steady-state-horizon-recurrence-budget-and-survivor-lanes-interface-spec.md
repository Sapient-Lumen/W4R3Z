# Remedy-hardening-attestation postcondition-durability contract sheet page — steady-state horizon, recurrence budget, and survivor lanes

## Purpose

This page is the compact contract for deciding whether a target state that is already realized is likely to stay realized for the intended slice across the next governing horizon.
It exists so the product can distinguish `realized now only`, `realized but fragile`, `realized for current cohort only`, `realized but future-arrival unsafe`, `realized but reconnect-or-replay vulnerable`, `stable through named horizon`, `durable for governed slice`, and `broader permanence blocked`.

## Core fields

- postcondition-durability identifier
- source postcondition-realization receipt identifier
- governing realization sentence
- target postcondition sentence
- governed slice identifier
- steady-state horizon identifier or duration
- future-arrival cohort definition
- reconnecting-lane inventory
- hidden-or-cleared device inventory
- paused or delayed-lane inventory
- replay or overwrite hazard inventory
- restore-or-rearchive hazard inventory
- path-churn or duplication hazard inventory
- ghost-or-placeholder regression inventory
- durability witness class summary
- recurrence budget summary
- current postcondition-durability class
- highest currently safe durability sentence
- strongest blocked stronger sentence
- next fact that upgrades durability standing now
- next fact that collapses durability standing now

## Postcondition-durability classes

The page must model at least these distinct classes:

- realized now only, durability unreviewed
- realized, but durability witnesses missing
- realized for currently visible cohort only
- realized, but future-arrival inheritance risk open
- realized, but reconnect or hidden-returner risk open
- realized, but replay or overwrite risk open
- realized, but restore or rearchive risk open
- realized, but path-churn or duplicate-path risk open
- realized, but placeholder or ghost regression risk open
- stable within named steady-state horizon for named slice only
- durable for governed slice within named horizon
- broader permanence or universal durability blocked

## Minimum required comparisons

The page must force explicit comparison between:

- current visible cohort and future-arrival cohort
- current connected world and reconnecting or returning worlds
- bytes-present outcome and placeholder-only outcome
- first restoration and restore survival after rescan
- hidden-from-view devices and actually retired devices
- stable-within-named-horizon and permanent-or-global durability

## Hard rules

- `realized now` must never silently upgrade to `durable`.
- `hidden from view` must never silently upgrade to `gone`.
- `paused` must never silently upgrade to `state frozen`.
- `restored once` must never silently upgrade to `restore will survive replay or rescan`.
- `folder visible on linked devices` must never silently upgrade to `future-arrival behavior already governed safely`.
- `no current contradiction` must never silently upgrade to `recurrence-resistant`.

