# Arabic and RTL craft

Contents: direction and layout · typography · numerals and mixed text · icons and motion · content and copy · testing · engines that do not shape Arabic

## Direction and layout

- Set direction at the root: `<html lang="ar" dir="rtl">`. For a bilingual page set `lang` and `dir` on each section or element that differs, not on `body` alone.
- Use **logical properties**: `margin-inline-start`, `padding-inline`, `inset-inline-end`, `text-align: start`, `border-start-start-radius`. Avoid `left/right` for layout. In Tailwind use `ms-*`, `me-*`, `ps-*`, `pe-*`, `start-*`, `end-*`.
- Flex and grid reverse automatically under `dir="rtl"`; do not add `row-reverse` on top of it.
- Mirror the layout, not the content: navigation, progress, back/next, sidebars and reading order flip. Logos, photographs, video controls, charts' time axes (usually), phone numbers and code do not.
- Keep one codebase: switch language by changing `lang`/`dir` and strings, not by duplicating CSS.

## Typography

- Arabic needs more room: body size about 1.05–1.15× the Latin size (16 px Latin → 17–18 px Arabic), leading **1.7–1.9**, headings 1.3–1.5. Cramped leading clips dots and diacritics.
- **Never letter-space Arabic.** `letter-spacing` breaks the connecting strokes. No italics or faux-bold; use a real weight. No uppercase labels (the script has no case).
- Measure about 55–60 characters. Justified text creates uneven gaps; prefer `text-align: start`.
- Font pairing: choose the Arabic face first, then a Latin partner with a similar x-height and stroke contrast. Neutral modern: IBM Plex Sans Arabic, Tajawal, Almarai, Readex Pro, Noto Kufi Arabic. Geometric: Cairo, Changa, Reem Kufi. Text/book: Noto Naskh Arabic, Amiri. Display/heritage: El Messiri, Lalezar. Confirm the families exist and which weights are available before requesting them.
- Declare a combined stack so Latin fragments do not fall back to a mismatched face: `font-family: "Tajawal", "DM Sans", system-ui, sans-serif;`.
- Test with real text that includes tall letters, dots above and below, and long words; pangram sample: «نص حكيم له سر قاطع وذو شأن عظيم مكتوب على ثوب أخضر ومغلف بجلد أزرق».

## Numerals and mixed text

- Decide numerals once: Western (0–9) is common in Gulf UI and for prices; Eastern Arabic-Indic (٠–٩) is common in editorial. Do not mix within one context. Use `font-variant-numeric: tabular-nums` for columns of figures.
- Embedded Latin or numbers inside Arabic sentences can reorder punctuation. Wrap fragments with `<bdi>` or `<span dir="ltr">`; for user-generated text use `dir="auto"` or `unicode-bidi: plaintext`.
- Phone numbers, emails, URLs, file names and code stay LTR (`dir="ltr"`, right-aligned if needed). Currency: put the unit consistently ("١٢٫٥٠ ر.س" or "SAR 12.50") and test where the sign lands.
- Use real Arabic punctuation where the style calls for it (، ؛ ؟) and the correct quotation marks (« »).

## Icons and motion

- Flip directional icons (arrows, chevrons, back, send, progress, list indents) with `[dir="rtl"] .icon-dir { transform: scaleX(-1); }`. Do not flip symbols with fixed meaning (clocks, checkmarks, media transport controls), brand marks, or images of real objects.
- Slide-in panels, carousels, swipe gestures, progress bars and skeleton shimmer run in the reading direction.
- Chevrons in breadcrumbs point toward the next item (left in RTL).

## Content and copy

- Write Arabic natively; do not translate English UI strings word for word. Address the user in a consistent register (neutral Modern Standard or a clear, friendly Gulf-flavoured tone if the brief wants it) and keep it for the whole product.
- Buttons name the result: «احفظ التغييرات» not «إرسال»; keep the same verb across the flow.
- Allow 20–30 % extra width for translated strings; avoid fixed-width buttons and truncation of names.
- Date and calendar: ask whether Hijri, Gregorian or both are needed; use `Intl.DateTimeFormat('ar-SA')` style APIs and test the result. Week starts on Saturday or Sunday depending on the market.
- Sorting and search: use locale-aware collation (`localeCompare('ar')`); normalise alef variants, taa marbuta/haa and diacritics (tashkeel) when matching user input.

## Testing checklist

- [ ] `dir`/`lang` set; no `left/right` in layout CSS
- [ ] Reading order, tab order and focus order match visual order
- [ ] Mixed Arabic/Latin/number strings render in the intended order
- [ ] Dots and diacritics are not clipped; leading is generous
- [ ] Directional icons and animations flip; handed icons do not
- [ ] Long names, 3-line titles and translated labels do not overflow
- [ ] Screen reader announces Arabic with the Arabic voice (`lang` on foreign fragments)

## Engines that do not shape Arabic

Some runtimes (for example certain in-game text renderers such as Minecraft Bedrock labels, and several canvas or bitmap-font pipelines) draw Arabic letters in isolated form and left-to-right. Detect it by rendering "مرحبا": disconnected letters or reversed order mean no shaping. Options, in order of preference: use a text object or font that supports shaping; pre-render strings to images/textures for fixed UI; or convert strings to **presentation forms** (contextual glyphs U+FE70–U+FEFF) with letters reordered for the display direction. If you convert, do it at build time with a tested script, keep the original string alongside, test every string including lam-alef ligatures (لا) and numbers, and tell the user it is a workaround.
