---
name: dopagaki-generator
description: Turns the given content (script, bullet points, file, or URL) into an auto-playing interactive web presentation (a single 16:9 HTML file) packed with the over-the-top "dopagaki" style popular on Japanese social media (Japanese video games × pachinko × Japanese anime opening sequences × short video × MAD/AMV). Screen-record the auto-play in a browser and it becomes a social media video. Use for requests like "make it dopagaki", "turn this into a dopagaki-style presentation", "make an insanely flashy motion presentation", "make a hype video for social media", or in Japanese 「ドパガキにして」「ドパガキ風のプレゼンにして」「超派手なモーションプレゼンを作って」「SNS用の煽り演出動画にして」.
---

# Dopagaki Generator

"Dopagaki" (ドパガキ) is Japanese internet slang for kids hooked on dopamine-heavy content; here it names a hyper-stimulating visual style borrowed from Japanese video games, Japanese pachinko machines, Japanese anime opening sequences, and short-form video. The style references below mean those Japanese conventions specifically.

## Usage

- Take the presentation content from the arguments (text / file path / URL). If none is given, ask for the content before starting.
- **Do not start building right away. First present a structure plan and get the user's confirmation** (see "Structure check" below). Skip the confirmation and go straight to implementation only when the user has explicitly said no confirmation is needed (e.g. "no need to confirm", "build it without checking with me", 「確認不要」, 「確認なしで作って」).
- Implement it following the "Direction spec" below. How you implement it (libraries, how the timeline is held, how effects are built) is up to you and should fit the content.
- The output is a single HTML file that opens directly in a browser. Save it where the user specifies; otherwise save to `.dopagaki/<YYYYMMDD>-<slug>.html`. Commit only when the user asks.
- Numbers that appear in the spec (`87`, `RANK S`, `COMBO ×12`, etc.) are examples of the effect patterns. Do not present numbers that are not in the source content as if they were facts.
- After implementing, actually play it in a browser and confirm that it runs to the end without any interaction, that no console errors appear, and that the important text is readable at the key moments.
- On delivery, tell the user the file path, total duration, control keys, and how to record it (go fullscreen and screen-record). If the user cannot open the file directly (e.g. remote execution), publish it as an Artifact and share the URL (load the `artifact-design` skill before publishing).
- Write the on-screen text in the language of the source content.

## Structure check

Once you have the content, design the structure and show it to the user before writing any HTML. Summarize the following as a table or list that can be reviewed at a glance:

- Title (theme) and the conclusion message that will be shown biggest at the end
- Estimated total duration
- For each slide (cut), in playback order: number / approximate seconds / directing genre (§13) / central message / main wording and numbers taken from the source / the payoff (what appears, and how, at REVEAL and IMPACT)
- The hook for the first 1–3 seconds, and the flow of the final result sequence
- What you cut or condensed from the source, and anything you are unsure of (numbers you could not verify, points open to interpretation, etc.)

After presenting it, do not proceed to implementation; wait for the reply. If the user asks for changes, show the revised structure again, and start implementing only once they approve (e.g. "OK", "go ahead and build it"). Leave the second-by-second timeline and effect details out of the structure plan; decide those during implementation.

## Direction spec

Implement the given content as a **hyper-stimulating, over-directed, auto-playing interactive web presentation** that incorporates the "dopagaki" style of expression popular on Japanese social media.

Do not make it just "flashy slides."

**Fuse video techniques that create strong eye guidance and anticipation — Japanese video games, Japanese pachinko, Japanese anime openings, short videos, MAD/AMV — and make the presentation itself a single piece of video work.**

Assume that, in the end, it will auto-play in a browser and simply recording the screen will produce a finished social media video.

### 1. Core concept

The goal is **not "a normal presentation made flashy," but "a presentation built out of the directing of Japanese video games, Japanese pachinko, Japanese anime OPs, and short videos."**

Make the baseline not "a bit flashy" but **"so overloaded with stimulation that it's laughable."**

Grab the viewer's eyes the moment they see the screen, make them anticipate what happens next, and create a big catharsis at the moment important information appears.

### 2. The four pillars of direction

Actively fuse the following four kinds of visual expression.

- **GAME** (Japanese video games — arcade, JRPG, rhythm and fighting games): SCORE / COMBO / LEVEL / RANK / HP・POWER / gauges / CLEAR / PERFECT / LEVEL UP / result screen / status UI / mission complete
- **PACHINKO** (Japanese pachinko/pachislot machines — their LCD "hype" sequences): foreshadowing effects / hype build-up / suspense-stretching "tame" (the held breath before the payoff) / countdowns / cut-ins / screen flashes / "super hot" style emphasis / escalation sequences / sudden giant text / build-up just before a "reach" / the hold right before the result / success or failure result effects
  - However, do not copy specific effects from existing works; instead use **the structure of "raise anticipation, then explode the result."**
- **ANIME OP** (Japanese TV anime opening sequences): giant title logos / character-intro-style introductions of elements / rapid cut switching / diagonal compositions / strong perspective / zooms that feel like the camera is diving in / rotation / split screens / masses of typography / light, particles, sparks / a sudden surge like entering the chorus / a powerful final presentation of the title or theme
- **SHORT VIDEO / MAD / AMV**: a strong hook in the first 1–3 seconds / giant captions / instant zooms / fast cuts you can feel the beat in / flashes / glitches / screen shake / speed ramps / a momentary freeze followed by a sudden burst / rapid-fire display of multiple pieces of information / a different visual treatment for every cut

### 3. Most important: AUTO play

**The default mode is AUTO.** It must progress automatically from start to finish without the user doing anything. Do not require clicks.

Give each slide, and each effect within a slide, a clear timeline. The basic shape is for effects to progress automatically like this:

`INTRO` → `TEASE` → `BUILD UP` → `REVEAL` → `IMPACT` → `RESULT` → `TRANSITION`

Implement click and keyboard controls as auxiliary controls such as pause / resume / previous / next.

**The auto-playing state itself is the finished work.**

### 4. Make "information appearing" an event in itself

Do not show all the information from the start. Direct "what is about to appear." For example:

`???` → blackout → small text `Is that really true?` → countdown `3` `2` `1` → high-speed zoom → giant number `87` → screen flash → `CRITICAL!!` → gauge MAX → `LEVEL UP!!`

Build it so that **the moment information appears is more entertaining than the information itself.**

### 5. Something is always happening

Avoid fully static states as much as possible.

- In the background, animate particles, light, grids, noise, flowing lines, radial lines, fine UI, numbers, small notifications, etc.
- In the foreground, have giant text, cards, badges, gauges, numbers, icons, labels, popups, etc. appear and change with staggered timing.

As a rule, **some visual event happens every few seconds.**

### 6. At important moments, "destroy the screen"

When an important number or conclusion appears, do not use an ordinary fade or slide-in; use **a big effect that uses the entire screen.** For example:

number counts up → momentary stop → a "tame" that feels like silence → screen flash → giant number → zoom → screen shake → particle explosion → `CRITICAL!!!` → gauge MAX → `LEVEL UP!!!` → fast transition to the next piece of information

For the "this is the most important part" moment, use a clearly stronger effect than anything before it.

### 7. Make numbers as flashy as possible

When there are numbers, do not treat them as plain text.

For example, count up rapidly like `27` → `31` → `42` → `58` → `73` → `87` → `100!!!`, and link scaling, glow, flashes, particles, combos, gauges, background changes, and screen shake to it.

Likewise with graphs: do not just display bars or lines; make it an event where **"the number grows → the graph follows → the screen reacts."**

### 8. Incorporate pachinko-style "hype"

Do not show the conclusion right away. Before important information, build the structure **anticipation → hype → tame → escalation → result.** For example:

`If this changes……` → small foreshadowing → background changes → UI that suggests something is about to happen → countdown → giant cut-in → result

Design it to **drag things out a little before the result is shown.** But do not use the same pattern every time.
Note: do not lazily reuse literal pachinko effects such as spinning reels.

### 9. Anime-OP-style "rapid cuts"

Use rapid cuts like a Japanese anime opening both between slides and within slides. For example, switch in a short time between:

title → person/concept → number → shape → keyword → background → giant text → logo → result

Actively use split screens, diagonal layouts, perspective, camera zooms, rotation, fast pans, and so on.

### 10. A short-video-style opening

The first 1–3 seconds are the most important. Do not open with an ordinary title slide.

Show right away a giant number, a big question, a punchy line of copy, a warning, a surprising result, a strong visual, explosive typography, etc.

**Make viewers think "What is this?" within the first few seconds.**

### 11. Screen density

Fill the screen boldly. Place different information in the background, middle ground, and foreground, and stack the layers. For example, a multi-layer structure like:

- Background: grids, light, particles, giant numbers
- Middle ground: gauges, cards, shapes, graphs
- Foreground: giant text, key numbers, UI, notifications

However, the truly important body text, numbers, and conclusions must always be readable.

### 12. Effects

Actively use the following:

Glow / Bloom / Flash / Particle / Spark / Noise / Glitch / Scanline / chromatic-aberration-style effects / motion-blur-style effects / Zoom / Shake / Rotation / Scale / Distortion / Radial burst / Speed line / Screen split / Light sweep

But do not use all of them all the time; **create contrast in intensity.**

Create an ebb and flow like:

quiet moment → anticipation → explosion → afterglow → acceleration again

### 13. Change the "directing genre" for each slide

Do not give every slide the same game UI. For example:

1. A short-video-style punchy hook
2. Pachinko-style hype
3. Anime-OP-style rapid cuts
4. A game status screen
5. A VS showdown
6. A number count-up
7. COMBO / FEVER
8. Masses of information + rapid editing
9. The final result

Make it **a structure whose visual development keeps changing.**

### 14. Screen transitions

Plain fades are forbidden. Actively use:

fast zoom / pan / rotation / flash / glitch / blackout / color inversion / split screen / parts scattering / transitions where the screen seems to shatter / transitions where the next screen flies in

Make the slide change itself an event.

### 15. The final result

Do not end with an ordinary "summary" slide. Fuse **a Japanese game's final result screen + a Japanese anime OP's final cut + a pachinko jackpot-style climax.** For example:

`MISSION COMPLETE` → giant number `87` → `RANK S` → `COMBO ×12` → `NEW RECORD` → full-screen flash → finally, the most important message displayed huge

Make the final effect the biggest in the entire work.

### 16. Information design

No matter how flashy it gets, **prioritize making the content understandable.** Give each slide one central message.

Rather than cramming in lots of small body text, design in the order **what to convey → what matters most → what effect would convey it most powerfully.**

Use flashiness not as decoration but **to visualize the importance of information.**

### 17. Technical requirements for video capture

- HTML / CSS / JavaScript
- 16:9
- Plays directly in a browser
- AUTO play is the default state
- Per-slide duration is configurable
- Each animation is managed on a timeline
- The whole thing auto-plays to the end
- Pause / resume
- Move forward / back
- Keyboard controls
- Click controls
- CSS Animation
- Web Animations API
- SVG / Canvas
- Use GSAP etc. as needed
- Avoid depending on video assets
- Generate effects with CSS / SVG / Canvas / JavaScript wherever possible
- Keep text as HTML
- Control numbers, gauges, and graphs with JavaScript
- Effects must not break when screen-recorded
- Avoid dropped frames as much as possible
- Structure it so timings and text are easy to change later

### 18. AUTO timeline

Do not simply display each slide; **design it as a performance along a time axis.** For example:

```text
0.0s   background starts
0.3s   small UI appears
0.8s   text appears
1.5s   number count starts
2.5s   gauge rises
3.2s   momentary stop
3.5s   giant effect
4.0s   flash
4.5s   result shown
6.0s   to next slide
```

In this way, **design down to "what happens when."**

### 19. Final direction

The finished product should work **not as presentation material, but as an auto-playing motion piece fusing "Japanese game × pachinko × Japanese anime OP × short video × MAD/AMV."**

Overdo the directing so much that viewers think "Is this a presentation?" and "What's going to happen next?"

However, always keep these three rules:

- **The more important the information, the stronger the effect**
- **Never sacrifice content for flashiness**
- **It must work end to end on AUTO play alone**
