# hot-lib-reloader load counters name library generations, not full route coverage

This scenario freezes the fact that hot-lib-reloader can name successive shadow-library loads with a `load_counter`.
That is valuable generation naming, but it still does not prove which callbacks, tasks, or retained trait objects have switched to the new generation.
