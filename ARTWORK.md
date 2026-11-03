# Reference-based orbital particle artwork

The owner's supplied 1136 × 1384 reference is stored unchanged in `design/reference.png`. It supplies the actual planet crescent, irregular dust ribbons, hill folds, small sun, typography, cards and logos. These are no longer approximated with a newly drawn globe or mountain silhouette.

Source grain follows radius-dependent elliptical streamlines around the planet. The streamlines have different local angular speeds; they do not rotate together as one rigid layer. Hill grain travels along the traced ridge, and the small sun turns about its center. Continuously replaced moving cohorts make the four-second cycle seamless while keeping the reference's density and lighting.

The cached lookup atlas was rendered on an NVIDIA GeForce RTX 4050 Laptop GPU. It contains 120 synchronized frames at 30 fps. A coarse/fine sampling pair preserves subpixel travel instead of quantizing the grain to large steps. The original raster is sampled directly, retaining its fine point texture. No scripts execute in the GitHub README, and no fluid/noise deformation is used.

The planet, orbital space and small sun use separate source/output masks so the orbit cannot pull text into the dust, duplicate the sun in the wind, or move the globe's silhouette. Typography, metadata, cards and footer icons stay fixed. Reduced-motion preferences show the supplied reference.

The activity grid uses actual public contribution levels and is refreshed daily. Working project/contact links remain in the README's compact expandable section, because links inside an SVG image are not separate clickable targets on GitHub.

Regenerate the profile from the cached orbital atlas (Python standard library only):

    python scripts/compose_profile.py

Refresh activity and compose:

    python scripts/compose_profile.py --refresh-activity

Re-render the orbital atlas with an NVIDIA CUDA GPU:

    python -m pip install -r scripts/requirements-render.txt
    python scripts/render_orbits.py
    python scripts/compose_profile.py

Verification: the supplied PNG is byte-identical to its input; GitHub serves and animates the embedded atlas; a browser comparison of 2,514,834 channels in fixed artwork regions found zero changed channels. The RTX rasterization test matched its CPU counterpart within one intensity level and rendered the test frame about 18 times faster. The production lookup atlas rendered and encoded in about two seconds on the RTX 4050.
