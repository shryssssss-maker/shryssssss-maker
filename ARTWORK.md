# Profile artwork

The profile is one continuous 1136 × 1384 SVG, matching the supplied reference's layout: terminal introduction, serif name, particle planet, four metadata groups, four project cards, a two-row technology grid beside real GitHub activity, and particle hills with footer icons.

The planet has rotating orbital filaments, diffuse dust, moving surface particles and grazing streams. Wind follows the hills' ridgelines. Motion runs inside GitHub's image rendering without scripts, external fonts, embedded HTML or third-party image widgets. Reduced-motion preferences show static rings and hide moving surface particles, streams and wind.

GitHub does not expose links inside an embedded SVG image as separate clickable targets. The README's compact, collapsed “Project & contact links” section provides working native links and readable project names without breaking up the reference layout.

Activity squares use actual public GitHub contribution levels. Their daily refresh updates the checked-in data and the complete SVG. Future dates are omitted. The graph's pattern is intentionally allowed to differ from the reference, whose squares are example data.

Regenerate with Python 3 (standard library only):

    python scripts/compose_profile.py

Refresh public activity and regenerate:

    python scripts/compose_profile.py --refresh-activity

Logos are from Simple Icons 13.21.0. See design/CREDITS.md. The remaining vector/particle artwork is original code.
