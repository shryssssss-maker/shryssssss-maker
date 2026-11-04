# Faster loading with a fixed planet and landscape

Research and experiments: 5 November 2026. This revisits the previous report with
the newly requested static planet, hills, and sun. Previous codec measurements
on the fully animated world were not assumed to apply to this new content.

## Decision

Retain offline, lossless rendering. Animate only the original orbital dust; serve
the hero directly as WebP and serve the fixed lower section independently.
This addresses both encoded size and when the browser can show the first frame,
and prevents daily contribution changes from replacing the animation's URL.
The final animation is 16,938,704 bytes. The static body is about 366 KB over gzip.
Together they are about 46.4% smaller than the previous 32,306,086-byte transfer.
No resolution reduction, palette quantization, near-lossless compression, new
simulation, or frame dropping was used.

## Fresh comparisons

All sample codecs below received the same first twelve native 1136 × 512 frames
from the final scene, with the original 33/34 ms timings.

| Candidate | Sample bytes | Pixel/timing result | Decision |
| --- | ---: | --- | --- |
| WebP lossless, method 4, minimum-size mode | 1,722,136 for the first 12 frame chunks plus shared headers | Full 120-frame output checked: zero differences, exact durations | Selected |
| AVIF, libavif 1.4.2 / AOM, lossless 8-bit RGB identity, speed 6 | 3,879,478 | Twelve frames decoded exactly | Larger; not selected |
| AVIF, lossless 10-bit reversible YCgCo mode, speed 4 | 1,824,656 | Frame 1 changed pixels; fresh official decoder also reproduced the mismatch | Rejected under strict pixel equality |
| JPEG XL, official libjxl 0.12.0, lossless, effort 5 | 2,650,014 | Lossless encoder configuration; larger sample | Not selected; no full-scene performance test justified |

The WebP number is a prefix byte cost from the full sequence, not an independently
optimized twelve-frame file. These experiments reject the tested alternatives;
they do not establish that every possible codec configuration would be worse.

## Primary technical evidence

- Google's [WebP FAQ](https://developers.google.com/speed/webp/faq#does_webp_support_progressive_or_interlaced_display)
  distinguishes incremental decoding from progressive/interlaced quality passes.
  The latter is not offered by WebP. Incoming data can still be used for display.
  A [WebP developer discussion](https://groups.google.com/a/webmproject.org/g/webp-discuss/c/UHSFurkFZGU)
  explains the CPU/memory reason for that design. The real-browser stream test,
  rather than that statement alone, established that the candidate can appear
  and move before its transfer completes.
- The [WebP container specification](https://developers.google.com/speed/webp/docs/riff_container)
  defines frame dimensions, durations, blending, disposal, and looping. The
  [encoder options](https://developers.google.com/speed/webp/docs/gif2webp) explain
  minimum-size encoding and its keyframe/seek tradeoff. Tab-return playback was
  tested because periodic keyframe removal can matter for recovery.
- The [libwebp animation encoder](https://github.com/webmproject/libwebp/blob/main/src/mux/anim_encode.c)
  already optimizes changing rectangles and transparent carryover pixels.
  Therefore a generic instruction to store only differences is insufficient.
- [Official AVIF encoder options](https://github.com/AOMediaCodec/libavif/blob/main/doc/avifenc.1.md)
  were checked against the downloaded official 1.4.2 CLI. RGB identity and
  reversible-color-transform paths were actually encoded and decoded; merely
  asking an export tool for quality 100 was not treated as proof of RGB equality.
- GitHub's Markdown API removed an explicit autoplay/muted/loop video tag in a
  rendering probe. This corroborates the restrictions in the
  [GitHub rendering pipeline](https://github.com/github/markup). A normal video
  with a poster could not be adopted as an equivalent autoplay README image.
- [SVG image-context restrictions](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image#restrictions)
  prevent simply moving the embedded animation to an external image URL inside
  the same SVG. The solution changes the README's image structure instead.

## Discussions and papers

The [Reddit color-matching discussion](https://www.reddit.com/r/ffmpeg/comments/1frqbu6/animated_webp_color_matching/)
was a useful warning to verify the RGB/color-conversion path. Its suggested
commands were not treated as proof of losslessness. A
[Stack Overflow discussion](https://stackoverflow.com/questions/76670222/redisplaying-an-already-loaded-animated-webp-image-from-the-beginning)
highlighted cache-busting costs and animation restart behavior; stable content
filenames and tab-return tests address those concerns here.

Jake Archibald's [X discussion of animated AVIF](https://x.com/jaffathecake/status/1798289240004137194)
raised transparency/container efficiency concerns. This scene's tested AVIF
samples had no alpha, so those concerns were not used to predict their sizes.
The measured encodes above drove the decision.

The [JPEG XL committee draft](https://arxiv.org/pdf/1908.03565) describes animation
and progressive frame organization, including partial-decoding previews. That
does not establish a smaller or faster result for this particular lossless
sequence; the new sample encode was larger. This is a historical committee
draft, not the current normative standard.

[NeuralLVC](https://arxiv.org/html/2604.03353v1) explores learned temporal
conditioning for lossless compression. Its video evaluation uses native YUV420,
whereas this task requires preserving the original RGB pixels. Its paper also
distinguishes image and video domains. A custom learned decoder is not a native
README image format and cannot simply be deployed in a sanitized GitHub page.
No reported research compression ratio was applied to this artwork.

## Checks and practical limits

The updated scene checks all 120 frames, 188,666,880 full-frame pixels, exact
durations, a still 141-pixel-radius globe silhouette outside the foreground dust,
and the original static hills/sun. A separate orbital comparison checked
63,639,360 original pixels with zero changes.

Browser layout checks found zero gap and a native total height of 1384 pixels.
A 512-pixel split passed the native pixel comparison; an odd-height split caused
an observed browser resampling difference and was rejected.

The controlled 1 MiB/s screencast test observed artwork at 325 ms and moving dust
at 467 ms while the file was incomplete. The old gzip-served SVG remained blank
through the 6.5-second observation. These timestamps come from image analysis of
screencast frames, not the browser's First Contentful Paint metric or a public
GitHub speed guarantee. CDN latency, caching, and connection quality vary.

The stored animation remains 30 fps. Software-rendered tests with 6× main-thread
throttling had median intervals near 33 ms, some initial pauses, and 90 display
draws in three seconds after a tab switch. This is not a whole-machine low-end
emulator or proof that every source frame was presented. A slow connection may
buffer the initial loop; a lossless four-second sequence cannot deliver all its
bytes faster than the connection permits. See `design/performance-verification.json`.
