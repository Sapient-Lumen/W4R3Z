# Precedent proof page: doctrine adopted, exception allowed, and overrule path interface spec

## Purpose

After the archive learned how to review and distinguish precedent, it still needed one proof page that answers:

> what doctrine now actually governs this class of case, what exceptions are allowed, and how would a later operator know whether they are allowed to overrule it?

## Core decision

AnonSync must expose one first-class **Precedent proof** page whenever doctrine is materially adopted, narrowed, distinguished, overruled, or sunset.

## Fixed page order

1. **Doctrine summary card**
2. **Binding-weight proof card**
3. **Scope and exception card**
4. **Version-window card**
5. **Overrule-path card**
6. **Decision sentence**

### 1) Doctrine summary card

Required rows:

- governing doctrine sentence
- source ruling ids
- current doctrine class
- doctrine owner
- adoption time
- current status

Supported `doctrine_class` values:

- `case-only`
- `local-precedent`
- `estate-precedent`
- `temporary-interim-doctrine`
- `sunset-doctrine`

### 2) Binding-weight proof card

Required rows:

- adopted binding weight
- why that weight is justified
- unresolved contradiction if any
- what would lower the weight
- what would strengthen the weight

Hard rule:

The proof must explain *why* the doctrine weight is safe.
Weight may not be ceremonial.

### 3) Scope and exception card

Required rows:

- covered case class
- explicit exclusions
- allowed exception path
- required distinction facts for exception
- weaker surviving sentence outside scope

Hard rule:

Exceptions may not remain folklore.
If doctrine can be bypassed, the proof must publish the gate and the narrower surviving sentence.

### 4) Version-window card

Required rows:

- version window covered
- world or lane window covered
- known sunset trigger
- known supersession trigger
- freshness or rereview target

Hard rule:

Every precedent proof must declare its version and world window.
There is no timeless doctrine by accident.

### 5) Overrule-path card

Required rows:

- who may propose overrule
- who may approve overrule
- required evidence for overrule
- interim-hold behavior
- recall obligations for dependent cases

Hard rule:

Overrule is a first-class path, not a hidden social maneuver.

### 6) Decision sentence

Render one sentence only:

- `Doctrine for [case class] is currently [doctrine class] with [binding weight], covers [scope], and may be overruled only through [overrule path].`

## Required interactions

- **Publish doctrine**
- **Attach exclusion**
- **Define exception gate**
- **Set rereview date**
- **Open overrule path**

## Failure state

If doctrine is still only case-specific, show:

- `No reusable doctrine published yet. This ruling remains case-only and may not be cited as binding.`
