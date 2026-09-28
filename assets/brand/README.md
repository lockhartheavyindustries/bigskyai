# Big Sky AI brand files

| File | Size | Use |
| --- | --- | --- |
| `bigsky-mark.svg` | Vector (512 × 512 viewBox) | Master Big Sky AI mark: teal rounded square, cream and coral peaks, gold sun. Redrawn to match `../bigsky-favicon-192.png`. |
| `bigsky-x-profile.png` | 800 × 800 | X profile picture. Full-bleed teal, with the peaks and sun kept inside the circle X crops to. |
| `bigsky-x-header.png` | 1500 × 500 | X header banner. Share-card style, with all text kept clear of the profile picture at the bottom left and of mobile edge crops. |

Each PNG is rendered from the SVG of the same name in this folder:
`bigsky-x-profile.svg` and `bigsky-x-header.svg`. Colours are the site's
design tokens: teal `#063f3d`, cream `#fffaf0`, coral `#d96f49`, gold
`#d7ad57`.

To regenerate, from this folder, with `rsvg-convert` (librsvg) and the Arial
font installed:

```sh
rsvg-convert -w 800 -h 800 bigsky-x-profile.svg -o bigsky-x-profile.png
rsvg-convert -w 1500 -h 500 bigsky-x-header.svg -o bigsky-x-header.png
```
