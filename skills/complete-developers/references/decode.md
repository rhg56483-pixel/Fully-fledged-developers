# Decode: from a short request to a precise prompt

Contents: why · the five moves · domain completion lists · Prompt Card · export modes · ask-or-assume · examples · traps

## Why

A five-word request ("سو لي موقع لمطعم") carries perhaps ten unstated decisions: who visits, on which device, in which language, what they must be able to do, what the owner already has, how it should feel. If you guess silently you rebuild later; if you interrogate the user you waste their patience. Decoding makes the decisions explicit once, in a few lines, then builds from them.

## The five moves

1. **Strip.** Write the literal ask in one clause, without adjectives. ("A website for a restaurant.")
2. **Find the job.** Who is the visitor, what are they trying to get done in under a minute, and what does success look like for the owner? ("Hungry local wants menu, hours, location and a way to order; owner wants more orders.")
3. **Complete.** Add what a professional in that domain would never forget (lists below). These go under MUST, marked *expected*, so the user can strike them.
4. **Bound.** Write WON'T. Exclusions stop scope creep and protect your budget.
5. **Mark uncertainty.** Everything you chose yourself goes under ASSUMED (reversible, with its consequence). Things that could invalidate a decision go under UNKNOWN. Never promote an assumption into a requirement, and never invent industry, brand, contacts, prices or credentials.

Language of the card follows the user's language. Reply in it; keep identifiers in English.

## Domain completion lists

Use as prompts for "what would a professional expect here?", not as mandatory scope.

| Domain | Often forgotten |
|---|---|
| Business site / landing | Primary action above the fold, contact and location, mobile-first, fast load, language and RTL, SEO basics (title, description, headings), social preview, analytics only if asked, legal/footer, editable content in one place |
| Store / booking | Catalogue or slots, cart/booking state, price and currency rules, confirmation and failure states, duplicate-submission guard, order record, payment is simulated unless a real provider and keys are supplied |
| Dashboard / admin | Roles and permissions, empty/loading/error states, filters and sorting, pagination, export, audit trail for destructive actions, responsive tables |
| App (mobile/web) | Onboarding, navigation model, offline/slow network, persistence, accessibility, settings, error recovery |
| Game | Playable core loop first, input, win/lose, feedback (sound, motion), difficulty ramp, save, performance budget, server authority if multiplayer |
| Roblox / Minecraft mod | Server/client split, validation of every client request, persistence limits, permissions, API version drift, cleanup on leave/unload, mobile controls |
| Bot / automation | Idempotency, rate limits, secrets in config, logging, retries with backoff, dry-run mode, what happens on failure |
| API / backend | Contract first, validation at the boundary, auth, error shape, pagination, versioning, config validation at startup |
| CLI / tool | Stable flag names, `--help`, machine-readable output option, exit codes, non-interactive mode, safe defaults |
| Bug / "it is slow" | Reproduction, baseline measurement, hypothesis, minimal fix, regression check |
| Design-only (logo, banner, poster) | Format and size, safe zone, supplied brand assets, text-free backgrounds so copy stays editable, export formats |

## Prompt Card

```
GOAL      <outcome from the user's point of view>
WHO/WHERE <audience; device; language/RTL; hosting or runtime>
MUST      <explicit> + <expected, marked (e)>
WON'T     <exclusions>
CONTENT   <given | placeholder: labelled>
LOOK      <archetype + dials | keep existing | brand file>
STACK     <existing | simplest fit + one-line reason>
DONE WHEN <observable checks, 3–6>
ASSUMED   <reversible defaults>      UNKNOWN <things that could change the plan>
```

Budget: about 120 words for medium work, up to 250 for large, one line for Spark. The card is your working prompt; the user does not need to copy it anywhere.

## Export modes

When the user wants a prompt *for another AI* (or to save), produce one of two forms and stop; do not build.

**Short**: the Prompt Card, polished into plain sentences, under 150 words.

**Full**: structured, copy-ready:
1. Task (one paragraph, outcome first)
2. Context (audience, device, language, existing assets)
3. Requirements (numbered, each independently checkable)
4. Design direction (archetype, 3 concrete traits, palette mood, type mood, one memorable element, what to avoid)
5. Technical constraints (stack, files, no external calls unless needed)
6. Output format (files, structure, how to run)
7. Acceptance checks
8. Non-goals

Leave out role-play filler ("you are a world-class…"), stacked imperatives and flattery. Specific constraints raise quality; adjectives do not.

## Ask or assume

Ask only if the answer changes the product or commits something irreversible (money, public posting, deleting data). Group questions (max three), plain words, offer a recommended default for each. Do not ask beginners "React or Vue?"; ask "موقع تعريفي، متجر، أم أداة يستخدمها الزائر؟" if that distinction matters. If the user says "اختر أنت" or cannot answer, proceed with stated defaults. If a question tool exists in the host, use it for the grouped questions.

## Examples (cards, not solutions)

**"سو لي موقع لمطعم"**
```
GOAL      زائر يعرف القائمة والأوقات والموقع ويطلب خلال أقل من دقيقة
WHO/WHERE سكان الحي، جوال أولاً، عربي RTL، استضافة ثابتة (HTML/CSS/JS)
MUST      قائمة طعام بأقسام، أوقات، خريطة/رابط موقع، زر واتساب للطلب (e)، معرض صور (e)
WON'T     دفع إلكتروني، حسابات، لوحة تحكم
CONTENT   اسم وقائمة وصور: placeholders معنونة "نموذج" حتى يزودني بها
LOOK      Atelier: archetype food-hospitality، warmth 4، motion 2
DONE WHEN يفتح على 360px بلا تمرير أفقي، التباين ≥4.5، كل زر يعمل أو يوضح سبب تعطله
ASSUMED   رقم واتساب وهمي واضح التسمية؛ UNKNOWN: هوية المطعم والألوان
```

**"make a todo app"** → GOAL: add, complete, delete tasks and keep them after reload. WHO: one person, phone or desktop. MUST: persistence in localStorage, empty state, keyboard add, undo delete (e). WON'T: accounts, sync. STACK: single HTML file. DONE WHEN: reload keeps data; 0 console errors.

**"my page is slow"** → Spark/Craft bug card: reproduce, measure baseline (what metric, where), hypothesis list ranked by cost to test, smallest fix, re-measure. No framework migration.

**"Roblox shop GUI"** → MUST: server-validated purchase (never trust the client's price), remote rate limit, DataStore save with retry budget (e), mobile-sized buttons, close/open state. WON'T: real-money flow unless Developer Products are specified.

## Traps

- Assuming the business type, brand name or location. Placeholders must be visibly placeholders.
- Turning "expected" items into hidden scope. Mark them, let the user strike them.
- Long cards. If the card is longer than the code it produces, cut it.
- Re-decoding every turn. Update the card only on a material change, then continue.
- Asking what you could decide reversibly.
