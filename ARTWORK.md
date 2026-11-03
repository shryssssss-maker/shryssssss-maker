# Profile artwork

Original procedural particle artwork for Shreyas Singh's GitHub profile.

The desktop and mobile heroes use a stippled hemisphere, rotating annular dust populations, projected latitude particles and grazing streams. The footer uses layered particle ridgelines, drifting motes and travelling wind highlights. All motion uses native SVG animation; no scripts, embedded HTML, remote fonts, trackers or image-generation services are needed.

The README uses relative asset paths and a `picture` element for the mobile composition. Project links and descriptions remain ordinary HTML/Markdown. GitHub's own live contribution calendar remains beneath the profile README rather than being replaced by a decorative imitation.

Regenerate with Python 3:

```sh
python scripts/generate_artwork.py
```

Assets are deterministic. The images have accessible titles/descriptions and README alternative text. A reduced-motion media query shows static rings and hides the moving surface particles, crossing streams and footer wind.

Project/contact text was checked against the owner's `portf`, `NyayAI`, `ARTERY`, and `cache-simulator` repositories. Education, location and coffee detail follow the supplied reference.
