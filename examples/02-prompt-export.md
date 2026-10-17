# Example 2: a short request turned into a prompt (export mode)

The user wants a prompt to paste into another AI, not a build. The skill decodes, then exports and stops.

**User:** سو لي بروميت للعبة تفحيط

**Short export (≈100 words)**

> لعبة تفحيط للجوال على Roblox. سيارة خلفية الدفع بتوجيه حاد ودفرنس مقفول وتوازن يمنع الانقلاب؛ انزلاق قابل للتحكم، عدّاد نقاط للانجراف، ودخان إطارات. تحكم باللمس بأزرار كبيرة. الخادم هو المرجع: النقاط والجوائز تُحسب في الخادم ولا تُصدّق أرقام العميل. بدون متجر أو دفع حقيقي. اكتب الكود مقسماً: إعداد السيارة (Tune)، سكربت التحكم، سكربت النقاط. المعيار: السيارة لا تنقلب في منعطف حاد بسرعة قصوى، والنقاط ترتفع فقط أثناء انزلاق حقيقي.

**Full export (structure)**

```
1  Task          outcome first, one paragraph
2  Context       platform, device, language, existing assets
3  Requirements  numbered, each checkable (drift physics, scoring, input, server authority)
4  Design        HUD layout, colours, feedback (smoke, camera shake) — 3 concrete traits
5  Technical     which scripts, where they live, no external calls
6  Output        file list + where to paste each script
7  Acceptance    observable checks (no flip at max speed; score only while sliding)
8  Non-goals     real-money purchases, multiplayer matchmaking
```

Note what is absent: no "you are a world-class developer", no stacked imperatives. Constraints and checks do the work.
