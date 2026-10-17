# Atelier: design that feels made by a person

Contents: what "human" means · dials · archetypes · the two-pass method · tells of generic design · craft rules · critique protocol · premium details

## What "human-made" means

People who design well do five things a template generator does not:

1. **They start from the subject.** A bakery, a clinic and a drift game share nothing visually; the materials, vocabulary and rituals of the subject supply the look. Ask "what is the most characteristic thing in this world?" and let the first screen show it.
2. **They commit to one idea.** One memorable move (a type treatment, a layout break, a texture, an interaction) and quiet discipline around it. Boldness spread everywhere reads as noise.
3. **They use hierarchy before decoration.** Size, weight, space and alignment carry structure; borders, shadows and gradients are the last resort.
4. **They write the words.** Real, specific copy beats placeholder adjectives; headings say what the page offers.
5. **They check it with their eyes.** Squint, shrink, rotate the phone, paste in a long name.

## Dials (1–5)

| Dial | 1 | 5 | Effects |
|---|---|---|---|
| **boldness** | quiet, restrained | loud, expressive | type scale contrast, colour saturation, layout asymmetry, corner sharpness |
| **density** | airy, spacious | compact, data-rich | type ratio, section padding, grid tightness |
| **motion** | still | lively | durations, entrance effects, hover depth |
| **warmth** | cool, precise | warm, human | neutral tint, corner radius, copy tone |

Pick archetype defaults, adjust dials from the brief ("فاخر" → boldness 2, density 1, motion 2; "حماسي" → boldness 5, motion 5), say the final values in one line. `python scripts/charter.py --archetype <id> --dials boldness=2,density=1` turns them into verified tokens.

## Archetypes

Starting points, not templates. Each lists the single move that makes it feel specific, and what to avoid.

<!-- archetypes:start -->
| id | best for | mood | memorable move | avoid |
|---|---|---|---|---|
| `food-hospitality` | restaurants, cafes, bakeries | appetising, warm, tactile | a menu that reads like a printed card, prices aligned with leader dots | stock-photo mosaics, neon, cold greys |
| `luxury-retail` | perfume, oud, jewellery, fashion | quiet, precious, unhurried | one oversized product on a calm ground with hairline rules | discount banners, loud gradients, crowded grids |
| `fintech-trust` | payments, banking, invoicing | precise, calm, credible | numbers as the hero, tabular figures, generous alignment | handshake stock photos, crypto neon, vague claims |
| `saas-tool` | dashboards, productivity, B2B tools | clear, efficient, friendly | a real fragment of the product UI in the hero, not an abstract blob | three identical feature cards, purple glow blobs, fake logos |
| `editorial-news` | blogs, magazines, documentation | authoritative, literate, calm | strong typographic hierarchy on a column grid with a pull quote | endless card feeds, tiny grey text, ad-style banners |
| `portfolio-creative` | personal sites, studios, case studies | confident, personal, expressive | case studies as large image sequences with short captions | template grids, generic skill bars, stock icons |
| `education-kids` | children's learning, family apps | playful, safe, big | large tactile shapes and one friendly illustrated guide | small text, dense menus, harsh reds |
| `health-calm` | clinics, wellness, mindfulness | reassuring, soft, human | generous space and one human-scale photograph | clinical stock imagery, alarming reds used as decoration |
| `real-estate` | property listings, developers | solid, aspirational, clear | full-bleed property imagery with a floor-plan overlay | cluttered filters first, tiny photos, loud badges |
| `game-neon-arcade` | action games, esports, HUDs | electric, fast, nocturnal | HUD-style framing with one scanline texture used once | glow on everything, low-contrast text on glow |
| `game-cozy-cartoon` | casual games, Roblox-style menus | chunky, friendly, bouncy | thick outlines and chunky buttons with a real pressed state | thin type, hairline borders, flat grey panels |
| `heritage-arabic` | cultural events, Ramadan, Gulf identity | dignified, rhythmic, warm | a geometric pattern used as structure (frame, divider, 6% ground), not clip-art | crescent-and-lantern clip-art, gold gradient text |
| `tech-developer` | docs, CLIs, open-source projects | exact, calm, technical | a real terminal or code sample with copy-to-clipboard in the hero | matrix-green hacker cliches, decorative code that does not run |
| `event-invite` | weddings, launches, invitations | ceremonial, intimate, elegant | the date and names set as a typographic centrepiece | busy backgrounds, more than two ornaments |
| `nonprofit-community` | charities, mosques, associations | sincere, steady, open | real people and stories first, one steady donation action | guilt imagery, stock smiles, five competing buttons |
<!-- archetypes:end -->

## The two-pass method

**Pass 1: plan (about 25 lines).** Name the subject, audience and primary job. Choose archetype and dials. Write the charter (generate with `charter.py`): 4–6 named colours with roles, two type voices and their jobs, spacing and radius rhythm, motion rule. Sketch the layout in ASCII (see `draw.md`), including the one memorable move.

**Challenge.** Ask: would I produce this same page for any similar brief? If yes, change the part that is generic (the hero treatment, the section order, the type pairing) and say in one line what changed and why. Check against "tells of generic design" below.

**Pass 2: build.** Code from the charter tokens only (CSS variables), never raw hex scattered through components. Keep selectors flat and low-specificity so section spacing and CTA styles do not fight each other.

## Tells of generic design, and what to do instead

| Tell | Instead |
|---|---|
| Purple-to-blue gradient hero with a glowing blob | Start from the subject's real colours and a plain ground; one purposeful accent |
| Three identical icon-cards in a row | Different layouts for different content: one large item, a list, a table, a quote |
| Everything centred | Left- (RTL: right-) aligned reading, with a deliberate centred moment |
| Giant headline with one word recoloured | Let the headline's scale, weight and line breaks carry the voice |
| Emoji or stock icons as decoration | One icon family with matched stroke, used only where they clarify |
| All-caps tracked labels above every heading | Labels only when they encode information; sentence case |
| Glass panels and blur on every surface | Solid surfaces; use blur once, for a reason (overlay, sticky bar) |
| Same 16px radius and shadow on everything | A radius scale tied to element size; elevation only where things float |
| "Revolutionize your workflow" copy | Plain statements of what the thing does for whom |
| Fake logos, metrics, testimonials | Real proof or none; clearly labelled sample content |
| Inter/Roboto because it is safe | A pairing chosen for the language and mood (see charter) |
| Perfect symmetry everywhere | Optical alignment; allow one asymmetry that guides the eye |
| Dark mode as an afterthought inversion | Re-derive dark tokens; dark surfaces need their own contrast checks |
| Autoplay motion on everything | Motion that explains state change; respect reduced-motion |

The brief's own words always win: if the user asks for glass, neon or gradients, deliver them well. The list is about defaults, not bans.

## Craft rules

**Type.** At most two voices, clearly distinct, chosen for the script they set. Establish a scale (charter) and use only its steps. Body measure 60–70 characters (Arabic about 55–60). Heading leading tighter than body. Treat display type as an image: set line breaks by hand, check rag.

**Colour.** Neutral ground tinted toward the brand, one primary for actions, one accent used sparingly, status colours reserved for status. Text pairs ≥4.5:1, large text and essential graphics ≥3:1; verify with `contrast.py`. Never carry meaning by colour alone.

**Space and layout.** A 4px base with a small scale; generous, *varied* section rhythm (tight inside groups, loose between). Group by proximity before boxing. Align to a shared edge; let one element break the grid on purpose. Preserve priorities across breakpoints instead of shrinking the desktop.

**Imagery and texture.** Prefer supplied real images; otherwise honest placeholders. Use CSS shapes, SVG or subtle grain/pattern for atmosphere, not stock mosaics. Photographs need a consistent treatment (crop ratio, tone). Keep generated or decorative visuals free of baked-in text.

**Motion.** Use it to explain: enter, exit, confirm, relate. 120–320 ms for UI, ease-out for entering, transform and opacity only. One signature motion, not twenty. Provide a still equivalent under `prefers-reduced-motion`.

**Components and states.** Every interactive element has default, hover, focus-visible, active, disabled, loading and error. Hit targets ≥44px. Forms: visible labels, inline errors that keep the input, sensible autocomplete and input types.

**Microcopy.** Buttons name the result ("Save changes", "اطلب الآن"); errors say what happened and how to fix it; empty states invite one action; the same action keeps the same word through the whole flow. No apology, no hype, no filler.

## Critique protocol (run before delivery, fix what fails)

1. **Squint test:** blur your eyes (or reduce the render 50%). Is the primary action and main content still the loudest thing?
2. **Grayscale test:** does hierarchy survive without colour?
3. **Five-second read:** what is this, who is it for, what do I do next? Answerable from the first screen.
4. **Remove one accessory:** delete the least necessary decoration. Keep the deletion if nothing is lost.
5. **Stress content:** a 40-character name, a 3-line title, 0 items, 500 items, a failed request.
6. **Devices:** 360 px, 768 px, 1280 px; thumb reach on mobile; 200% zoom; keyboard-only focus order.
7. **Dark and RTL:** both re-checked, not assumed.

If you can render, look at the real render; if you cannot, say the visual check was not run.

## Premium ("فاخر") details

Luxury is restraint plus precision: fewer elements with more space; one refined type pairing with considered line breaks; hairline rules instead of boxes; a palette of two or three tones; tactile, slow-but-short motion (180–320 ms) on hover and reveal; consistent image treatment; optical alignment of icons and text; pixel-exact spacing; no clutter badges; copy edited to the bone. Preview it at every breakpoint; flaws show first in the details.
