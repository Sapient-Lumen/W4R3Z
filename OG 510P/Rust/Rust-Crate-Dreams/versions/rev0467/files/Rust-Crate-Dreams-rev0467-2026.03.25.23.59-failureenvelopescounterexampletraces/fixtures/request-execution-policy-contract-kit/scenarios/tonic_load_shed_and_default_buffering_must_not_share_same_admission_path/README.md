# Scenario — tonic load shed and default buffering must not share the same admission path

`tonic` documents that enabling load shedding changes not-ready handling from buffering to immediate `resource_exhausted` rejection.
This scenario keeps that split explicit.
