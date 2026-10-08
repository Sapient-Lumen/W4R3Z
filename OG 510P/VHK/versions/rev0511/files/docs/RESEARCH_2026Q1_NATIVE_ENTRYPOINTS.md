# Research: native entrypoints and desktop actions

Notes folded into the current native-install pass:

- Desktop Entry additional actions are a good fit for VHK because they let one
  installed app surface both a default palette entrypoint and a few focused
  quick actions without pretending every launcher supports rich nested UI.
- XDG cache is the right default home for a materialized reviewed bundle
  because the extracted tree is derived from the shipped zip and can be rebuilt
  when that bundle changes.
- This keeps the native install lane closer to a real Linux application shape:
  one launcher path, one desktop file, a few app actions, and one cacheable
  working tree instead of a permanent dependency on a mutable source checkout.
