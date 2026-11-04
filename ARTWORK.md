# Particle profile artwork

The original supplied PNG remains byte-identical in `design/reference.png`.
The planet's visible surface and rim, the hills, and the small sun are fixed to
that reference. Only the orbital dust moves, including the stream passing in
front of the planet. Its original 120 samples, 33/34 ms frame durations, four-second
loop, point texture, and native 1136 × 1384 layout are retained.

## Serving and caching

The README displays two adjacent images with zero space between them:

- An ordinary, lossless animated WebP for rows 0–511. Its filename contains its
  content hash and stays unchanged during contribution refreshes.
- `assets/profile-body.svg` for rows 512–1383. It embeds a lossless reference
  bitmap and overlays actual public GitHub contribution data.

The 512-pixel boundary was verified in a browser at native resolution. It avoids
an observed image-resampling difference with an odd-height split. There are no
live displacement filters, scripts, simulations, or animated hills in the README.
Reduced-motion preferences select the small still hero instead of the animation.
`assets/profile.svg` and `profile-static.svg` are small, static full-layout views
for compatibility; the README does not download them.

The new normal-motion payload is approximately 17.30 MB / 16.50 MiB including the
gzipped static section, versus the previous 32.31 MB / 30.81 MiB gzip transfer:
about 46% less data. Direct image serving also lets the browser display incoming
frames before the complete file has downloaded. The body and activity updates
no longer invalidate the large animation asset.

Project/contact links remain in the README's expandable section. Links inside
image pixels are not separate clickable targets on GitHub.

## Verification

`design/bake-verification.json` records source/animation hashes and the codec
checks. All 120 decoded frames match the intended frozen-world capture exactly:
188,666,880 full-frame pixels compared, zero differences. The source reference
is also checked for the complete planet silhouette outside the passing dust,
and for the hills and sun. A separate comparison checked 63,639,360 pixels in
the untouched orbital regions against the previous animation, with zero changes.

Native-resolution browser comparison of the two-image layout found zero pixel
differences outside the separately refreshed activity panel. The native layout
height is 1384 pixels and the inter-image gap is zero.

In the controlled localhost test at 1 MiB/s, screencast image analysis observed
substantial hero artwork at 325 ms and moving orbital pixels at 467 ms, with the
file still downloading. The previous gzip-served SVG showed no artwork during
the 6.5-second observation. These are controlled observations, not a guarantee
of public-server timing. On a connection slower than the animation bitrate, the
initial loop can still buffer until enough data has arrived.

The source remains 30 fps. The Intel-GPU test had a median display interval of
32.74 ms. With GPU acceleration disabled and 6× main-thread throttling, median
intervals were about 33 ms; after a tab switch, 90 display draws were observed
in three seconds. Some initial software runs had longer pauses. Compositor draw
counts do not establish that every unique frame was presented, and main-thread
throttling does not emulate a whole low-end computer.
See `design/performance-verification.json` and `LOADING-RESEARCH.md`.

## Rebuild

The daily refresh uses Python's standard library only:

    python scripts/compose_profile.py --refresh-activity

It reuses the lossless bitmaps already embedded in the small static SVGs, so a
fresh checkout needs no GPU, browser package, or image encoder for this command.
Running without `--refresh-activity` composes from cached contribution data.

To deliberately rebuild the animation offline:

    python -m pip install -r scripts/requirements-render.txt -r scripts/requirements-bake.txt
    python -m playwright install chromium
    python scripts/render_orbits.py
    python scripts/bake_profile.py

Use `--channel chrome` to capture with installed Chrome. The baker captures the
original and frozen-world reference renderers, preserves original orbital pixels,
pins the complete planet rim, verifies all decoded frames, and creates the still
assets and manifest before composing the README. Its temporary directory can be
set with `--work-dir`. Local derived `design/reference.webp` and
`design/body-reference.webp` caches are ignored by Git; the checked-in SVGs carry
the same data for daily rebuilds. The original lookup renderer is used only offline.
