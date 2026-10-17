# Example 1: "سو لي موقع لمطعم" (Atelier lane)

An illustrative walk-through of the loop on a five-word request. It shows the shape of the work product at each step; it is not a benchmark.

## 1. Decode: the Prompt Card

```
GOAL      زائر يعرف القائمة والأوقات والموقع ويطلب خلال أقل من دقيقة
WHO/WHERE سكان الحي، جوال أولاً (390px)، عربي RTL، استضافة ثابتة HTML/CSS/JS
MUST      قائمة بأقسام وأسعار، أوقات، رابط الموقع، زر واتساب للطلب (e)، معرض صور (e)
WON'T     دفع إلكتروني، حسابات، لوحة تحكم
CONTENT   اسم/قائمة/صور: placeholders معنونة "نموذج"
LOOK      Atelier · food-hospitality · boldness 3, density 2, motion 2, warmth 5
STACK     ملف HTML واحد + CSS متغيرات؛ لا مكتبات
DONE WHEN لا تمرير أفقي عند 360px · التباين ≥4.5 · كل زر يعمل أو يوضح سبب تعطله · RTL سليم
ASSUMED   رقم واتساب وهمي بتسمية واضحة     UNKNOWN هوية المطعم وألوانه
```

## 2. Draw: three thumbnails (different structure, not decoration)

```
A  "Menu-first"                 B  "Photo-led"                 C  "Order-now bar"
┌────────────────┐             ┌────────────────┐             ┌────────────────┐
│ name      ☰    │             │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │             │ name      ☰    │
│ ── today ──    │             │ ▒▒ dish photo ▒│             │ headline       │
│ [ order ]      │             │ name  [ order ]│             │ ~~~~~~         │
│ المقبلات ..... 12│            │ ───────────────│             │ ┌─ sticky ───┐ │
│ الأطباق ..... 28│            │ menu (tabs)    │             │ │[order][map]│ │
└────────────────┘             └────────────────┘             └────────────────┘
```

**Chosen: A.** The visitor's job is "see the menu and order"; B hides prices below the fold. The memorable move is the printed-card menu with leader dots.

## 3. Charter (generated, contrast-verified)

`python scripts/charter.py --archetype food-hospitality --rtl --name "Sample restaurant"` produces, among other sections:

## Colour (contrast verified on opaque colours)
| Token | Light | Dark |
|---|---|---|
| bg | `#FFF9F1` | `#140D04` |
| surface | `#FFFEFC` | `#1E160A` |
| surface-2 | `#FCF1E1` | `#271F13` |
| border | `#E8DCCD` | `#382F23` |
| text | `#241806` | `#F8EDDD` |
| text-muted | `#6B6254` | `#AEA394` |
| primary | `#B4532A` | `#E57F56` |
| on-primary | `#FFFFFF` | `#181006` |
| accent | `#009390` | `#19C3BF` |
| focus | `#B25128` | `#FF9971` |
| success | `#17843F` | `#6FD087` |
| warning | `#986600` | `#E8AA4E` |
| danger | `#B54B43` | `#FF968A` |

Key pairs (ratio light / dark):
- text on bg: 16.61 / 16.66
- text on surface: 17.24 / 15.45
- muted on bg: 5.73 / 7.77
- muted on surface-2: 5.37 / 6.55
- on-primary on primary: 4.99 / 6.72
- accent on bg (graphic): 3.6 / 8.81
- focus on bg (graphic): 4.89 / 9.23
- danger on bg: 4.95 / 9.17

## Type
- Display: "El Messiri", "Fraunces", sans-serif
- Body: "Tajawal", "DM Sans", system-ui, sans-serif
- Scale ratio 1.3; base 1.1rem; body leading 1.8, headings 1.4; measure 58ch; letter-spacing 0 (never track Arabic).
- Fonts: https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&family=El+Messiri:wght@400;500;600;700&family=Tajawal:wght@400;500;700&display=swap (confirm availability before shipping)
## 4. Plan (slices)

1. Skeleton: header, hero with order button, menu section (placeholders), RTL on. *Check: opens at 360px, no horizontal scroll.*
2. Menu card with leader dots and category jump links. *Check: long dish name wraps cleanly.*
3. Hours, map link, WhatsApp button (labelled sample number). *Check: links resolve, button states visible.*
4. Gallery with honest placeholders; reduced-motion respected. *Check: keyboard and focus order.*
5. QA: squint, grayscale, 200% zoom, contrast script. *Report each as passed / failed / not run.*

## 5. Delivery reply (shape)

> موقع المطعم جاهز في `index.html` (افتحه مباشرة). **تم التحقق:** لا تمرير أفقي عند 360 و768 و1280 (passed)، التباين بالسكربت (passed)، الأزرار والروابط (passed)، فحص بصري على متصفح (not run: لا يوجد متصفح هنا). **نموذجي:** الاسم والقائمة والصور ورقم الواتساب. **افتراضات:** ألوان طينية دافئة. **الخطوة التالية:** أرسل لي القائمة والشعار وأضيفهما.
