# Icon asset direction

## Decision

Use two asset sources:

- Standard UI icons: use a mature free SVG set, preferably Lucide or Tabler.
- Kalmyk cultural icons: keep them custom, generated first as raster references and then redrawn/cleaned as SVG or Figma components.

Reason: generic UI icons should not be custom-drawn. Cultural symbols should not come from random stock sites because the license and cultural accuracy are risky.

## Generated References

Saved outputs:

- `output/imagegen/icons/kalmyk-cultural-icon-sheet-01.png`
- `output/imagegen/icons/kalmyk-cultural-icon-sheet-02.png`
- `output/imagegen/icons/crops/*.png`

Use `kalmyk-cultural-icon-sheet-02.png` as the preferred reference. It removes the meander-style border from v1 and stays closer to the Kalmykia emblem/costume references:

- red/yellow sunburst;
- zala fan/tassel;
- white lotus with red outline;
- clean blue/gold emblem arcs;
- juvenile saiga badge;
- black-red-gold costume collar badge;
- dictionary/book/audio/path/reward/streak support icons.

## Figma Placement

Installed a first raster test pass into the Style C editable board:

- Figma board: `Style C editable v1 - mascot-first direction`, node `48:2`
- home screen: path nodes and review word icons;
- lesson screen: audio prompt and word speaker icons;
- dictionary screen: word-category icons and drawer icon;
- bottom navigation: simple vector glyphs were added over the existing icon backgrounds so nav no longer reads as empty squares.

The low-contrast lotus crop was replaced in small slots with the more readable zala flower symbol. Keep the lotus for larger emblem-style compositions unless it is redrawn with heavier outlines.

## Reject / Watch

- Do not use v1 top-right arc icon as-is: it contains a meander-like border and risks reading as the wrong cultural ornament.
- Do not use generic "Central Asian" ornaments unless they are verified against Kalmyk references.
- Do not treat the generated raster icons as final production assets in tiny UI controls. This Figma pass is a readability test; production should use simplified SVG/Figma components.

## Implementation Notes

- Use Lucide/Tabler for normal app controls: home, search, audio, profile, book, check, close, arrow, settings.
- Use custom cultural icons as larger reward/category/badge illustrations.
- Build final Figma components for: sunburst, zala, lotus, blue arcs, saiga badge, costume collar badge, reward medal, streak flame.
- Keep cultural icons out of tiny text pills unless the label layout reserves enough space.

## Source Checks

- Lucide license: https://lucide.dev/license
- Tabler Icons license: https://github.com/tabler/tabler-icons/blob/main/LICENSE
- Iconify icon license notes: https://iconify.design/docs/icons/license.html
- SVG Repo licensing: https://www.svgrepo.com/page/licensing/
