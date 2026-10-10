# الشعار — Logo files

All files are generated from the approved Illustrator source (`source/sukna-w-khazinah_original-artboards.pdf`, artboard 3) by `python3 scripts/build_logo.py`. The geometry is the original 18 vector paths, re-based to a tight box (641.36 × 531.06, ratio 1.208). Rendered PNGs differ from the source by anti-aliasing only.

| Variant | Mark | Background | Use |
|---|---|---|---|
| `primary` | Sukna Green | Khazinah Yellow | Default lockup |
| `reverse` | Khazinah Yellow | Sukna Green | Green surfaces |
| `mono-black-on-white` | Black | White | Documents, one-colour print |
| `mark-green` | Sukna Green | transparent | White and light backgrounds |
| `mark-yellow` | Khazinah Yellow | transparent | Green, ink and dark photos |
| `mark-black` / `mark-white` | Black / White | transparent | One-colour print, engraving, dark photos |
| `mark-ink` | Ink #0B2A1E | transparent | Formal documents |
| `avatar-yellow` / `avatar-green` | — | square | Social profile pictures |

| Folder | Format |
|---|---|
| `svg/` | Web and apps (vector, `<title>` included) |
| `png/` | Transparent where there is no background; 512 / 1024 / 2048 / 4096px wide (avatars 400 / 1080 / 2048) |
| `pdf/` | Vector, RGB |
| `pdf-cmyk/` | Vector, CMYK for printers (suggested values; proof before a print run) |
| `ai/` | Adobe Illustrator, PDF-compatible `.ai` (fully editable vectors). `sukna-w-khazinah_original-artboards.ai` holds all three original artboards. |
| `master/` | Master SVG + JSON geometry (paths, unit D, clear space, angle) |

**Clear space:** 2D on every side (D = dot diameter ≈ 36 units ≈ 5.6% of the mark's width).
**Minimum width:** 120px on screen, 30mm in print, 40mm for embroidery or stamps.
