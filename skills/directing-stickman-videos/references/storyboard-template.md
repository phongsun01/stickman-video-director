# Director's Proposal Contract

Use this contract for Phase A. Present a readable production proposal and stop for confirmation before writing model prompts. Refer to `references/style-catalog.md` for style specifications.

Style 3 (Prehistoric Hand-Drawn / Dark Comedy) is also supported. Before planning it, read `prehistoric-dark-comedy.md`; its cast-card, earthy palette, setup/escalation/payoff and reaction-pause rules take precedence over generic pacing guidance. Include distinguishable cast cards and a location/prop continuity plan in Phase A. Treat the story as fictional analogy, not invented historical fact.

Style 4 (Cozy Storytelling / 治愈故事风) uses `cozy-storytelling.md`. In Phase A name a different recognizable main setting for each new ten-second segment by default, plus wide/close/moving shots inside it. Lock character design, important props and narration; scenery changes intentionally. Respect an explicit single-location request or approved callback. Do not call this style hand-drawn or require the same table/room across all segments.

Style 5 (Historical Cartoon / 历史卡通风) uses `historical-cartoon.md`. Include its era pack, complete cast cards, location/prop states, exact VO and shared `voice-continuity.md` profile in Phase A. Keep the drawing grammar while adapting clothing, architecture, palette and music to the era. Its narrative-short ending and physical-action pacing take precedence over generic pacing guidance; reactions may pause deliberately. Separate historical facts from invented comic scenes.

## Rewrite the source

Create natural narration in the resolved `narration_language` under [narration language and timing](narration-language.md). Fit each clip by estimated or measured reading time, with pauses; use English word counts only as an English drafting heuristic.

- Preserve the source's core claim, names, numbers, and factual meaning.
- Strengthen a weak opening with an immediate hook.
- Remove repetition and secondary branches from long sources.
- Expand short sources with a relevant example, progression, reframe, or callback.
- Prefer clear spoken language to literal translation.
- Simplify wording before increasing speaking speed.
- Do not invent research, statistics, quotations, product claims, or factual details.

Use the user's language for planning explanations. Keep speech in `narration_language`; provide a reference translation only when useful.

## Header contract

Present these items in order:

1. Title in the publishing/narration language and a reference title when useful
2. Core message and opening hook
3. Chosen aspect ratio (`16:9` or `9:16`), target duration (in 10s multiples), and visual style/theme (Style 1 Classic Light/Dark, Style 2A Modern Studio Tech, or Style 2B Cinematic Story)
4. Narrator's complete video-level voice profile from `voice-continuity.md` (identity/age, accent, timbre, register, resonance, texture, delivery, pace and recording treatment), `narration_language`, compatible accent, and estimated/measured reading duration
5. Up to three saturated accent colors (for Style 1) or visual palette/environment mood (for Style 2), named in ordinary language, and what each represents
6. BGM direction, emotional turn, tone, and narrative arc

Default the narrator only after required setup is complete: propose a source-appropriate female, male or other coherent voice profile for approval, not a mandatory universal baritone. Expand short preferences such as "male voice" into the complete fields in `voice-continuity.md`. Different videos may choose different voices, but one video's clips share its frozen profile. Separate the narrative emotional arc from stable vocal identity and delivery. Infer tone and palette from the source when the user did not specify them.

## Narrative structure

Apply [Director narrative and pacing](director-story-pacing.md). Name the purpose-appropriate structure and ending in the proposal; do not impose the five-stage commentary pattern on every source.

## Storyboard contract

Produce exactly N approximately ten-second rows (where N = target duration in seconds / 10; default: 6 rows for 60s):

| Time | Narrative purpose | Stick-figure scene | Motion, camera, and transition | VO (`narration_language`) | Reference translation | BGM / SFX |
|---|---|---|---|---|---|---|

Give each row a different narrative job aligned with the chosen narrative structure. Fit spoken lines to the clip’s natural reading time while keeping sentence boundaries natural.

## Visual density

Apply [Director narrative and pacing](director-story-pacing.md): default to one principal action and one supporting emphasis per row. Record timed setup, action and result as appropriate, including purposeful holds. No minimum device count or fixed visual-change interval applies.

## Palette and text

Keep the background and stick figure monochrome according to the selected theme (for Style 1), or use high-key studio grid / cinematic lighting (for Style 2). Use no more than three saturated accent colors across the video. Assign semantic meaning such as anxiety, danger, energy, discovery, or success.

Name colors only with ordinary descriptive language. Do not use hexadecimal, RGB, HSL, Pantone, or other technical color notation anywhere in the proposal or production prompts.

Default the generated video to no visible words, letters, numbers, captions, subtitles, interface copy, or technical annotations. Make message bubbles, content cards, meters, clocks, and notifications icon-only. After the storyboard, optionally list concise short overlays in the publishing language for post-production, including their target clips and safe placement; never carry those overlays into the video-generation prompts.

## Composition by aspect ratio

- `16:9`: use left-center-right staging, lateral tracking, horizontal match cuts, and deliberate negative space. Reserve clean space for optional post-production overlays when useful.
- `9:16`: use foreground/background depth, vertical reveals, stacked motion, foreground passes, and interface-safe overlay space.

Changing ratio requires new staging, camera paths, transition geometry, and overlay-safe negative space. Changing theme or style requires updated color balance and contrast checks.

## Continuity

End each row with a visible interface that the next row inherits: a pose, moving object, filled frame, travel direction, shape, or camera motion. Name both sides of every connection in the proposal. For Style 4, an approved location cut or time jump may replace literal background matching: state what continues (character, prop, direction or story action) and what changes (place/time). Do not spend all N clips at the same desk unless explicitly requested.

## Confirmation ending

End Phase A by asking the user to:

- approve the current proposal and generate the N Omni Flash prompts;
- revise a named scene or narration passage; or
- change a global setting such as aspect ratio, duration, style, theme, palette, voice, or tone.

Do not include final model prompts. A global change invalidates approval and requires a revised Phase A.

## Phase A checks

- Source, aspect ratio (`16:9` or `9:16`), duration, and style/theme are known.
- Script uses the purpose-appropriate structure selected under `director-story-pacing.md`.
- Final clip delivers the intended takeaway, payoff or relevant CTA; discussion is optional.
- Narration fits the clip at a natural pace under `narration-language.md`; estimated and measured durations are distinguished.
- Exactly N storyboard rows have distinct narrative purposes (N = duration / 10).
- Every row has readable timed action, supporting emphasis, audio and a planned transition.
- Action density serves comprehension; purposeful holds are identified.
- No more than three saturated accent colors are used (for Style 1) or clean palette rules followed (for Style 2).
- No technical color notation is present.
- Any proposed text is clearly separated as a post-production overlay and absent from generated scenes.
- Every adjacent pair has a named continuity connection.
- The ending returns to the central message and CTA.
- No unsupported factual detail was added.
- One complete voice profile is proposed for the whole video, independent of visual style; scene-specific audio notes do not contradict it. Any approved multiple speakers have separate stable profiles and explicit line assignments.
