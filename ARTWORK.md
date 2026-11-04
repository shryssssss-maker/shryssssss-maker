# Reference artwork and lossless animation

The owner's supplied 1136 × 1384 PNG remains unchanged in `design/reference.png`.
The particle paths, planet lighting, hills, sun, timing, and four-second loop are
the same as the previous lookup-filter animation: 120 frames at 30 fps.

The published SVG now contains one embedded **lossless animated WebP** atlas.
Two clipped uses of that shared image show the hero and hills in their original
positions. There are **no runtime SVG filters, displacement maps, scripts, or
particle calculations**. Typography, cards, logos, and source texture remain
at native resolution. The contribution panel still refreshes daily from actual
public GitHub activity. The README serves the static source when reduced motion
is requested; project/contact links remain in its expandable section.

## Visual verification

Each frame was captured in Chrome 156.0.8078.80 at native resolution, using the
original GPU-generated lookup frame as a static input to the original filter
pipeline. This preserves the pipeline's exact raster result rather than
approximating the motion with a new simulation.

All 120 decoded lossless frames were reconstructed into the full layout and
compared with those captures: **188,666,880 pixels, zero changed pixels**.
Native-resolution browser screenshots of the replacement composition at frames
0, 60, and 119 also had zero differences outside the separately refreshed
contribution panel. The encoder preserves the 33/34 ms frame durations and
infinite looping. Checksums and durations are in `design/bake-verification.json`.
Pixel equality refers to these native-resolution captured frames; browsers can
resample images differently at other display scales.

## Performance verification

On the owner's i7-13650HX laptop, Chrome 156 used Intel UHD via ANGLE/D3D11.
The original GitHub desktop layout produced about 11–13 display draws per second
with typical intervals around 89 ms. The replacement, tested at the full native
1136 × 1384 size, produced 153 display draws in five seconds (median 31.5 ms).
In a separate headless Chrome run with GPU acceleration disabled and main-thread
CPU throttling set to 6×, it produced 147 draws in five seconds (median 31.9 ms).
Draw counts measure compositor activity, not a promise about every unique frame.
The hosted GitHub preview produced 150 display draws in five seconds at 838 px
wide (median 33.4 ms, 95th percentile 46.6 ms), and screenshots confirmed motion.
Main-thread throttling does not emulate an entire weaker CPU or GPU. These tests
support much better playback but do not guarantee every low-end PC.

The cost is a larger initial download: the SVG is 40.73 MiB, including a 29.29 MiB
lossless WebP. Lossless animated WebP was chosen after
comparing it with lossless APNG (about 77 MB). No palette reduction, lossy
compression, resolution reduction, or dropped source frames was used.

## Rebuild

Daily contribution refresh and composition use only Python's standard library:

    python scripts/compose_profile.py --refresh-activity

Compose without fetching contribution data:

    python scripts/compose_profile.py

The baked WebP embedded in the checked-in SVG makes these commands independent
of GPU/browser tooling. The compositor reuses that embedded resource. An optional
local `design/baked-orbits.webp` overrides it after a new offline bake; this
duplicate binary is ignored by Git.
To intentionally regenerate the motion, install the optional offline dependencies:

    python -m pip install -r scripts/requirements-render.txt -r scripts/requirements-bake.txt
    python -m playwright install chromium
    python scripts/render_orbits.py
    python scripts/bake_profile.py
    python scripts/compose_profile.py

`bake_profile.py --channel chrome` uses installed Google Chrome instead.
The baker checks every decoded frame before replacing the cached animation.
The original renderer is retained in `scripts/compose_live_filters.py` for the
offline capture step; it is not used by the README or the scheduled refresh.
