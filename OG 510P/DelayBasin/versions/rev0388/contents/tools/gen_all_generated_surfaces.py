import pathlib

from generated_surface_lib import GENERATED_SURFACES, refresh_generated_surfaces

ROOT = pathlib.Path(__file__).resolve().parents[1]
refresh_generated_surfaces(ROOT, include_release_integrity=True)
print(f"wrote {len(GENERATED_SURFACES)} generated surfaces")
