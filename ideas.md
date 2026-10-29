# Idea shortlist and scoring

On 29 Oct 2026 ten independent agents each proposed one idea from the
rules and judging rubric (each got a different starting angle). I scored them
with the real rubric: Impact 30%, Meta tooling 25%, Demo 25%, Technical depth
20%, each 0 to 10. Scores are judgment, not measurement.

| Idea | Impact | Meta tooling | Demo | Tech | Weighted | Solo 5-day risk |
|---|---|---|---|---|---|---|
| Sketch2Sim | 6 | 9 | 9 | 8 | 7.9 | Medium-high (reading sketches) |
| Flakewatch | 7 | 8 | 7 | 9 | 7.65 | Medium |
| ShopFront Studio | 7 | 9 | 8 | 6 | 7.55 | Low |
| FixIt Crew | 7 | 8 | 8 | 7 | 7.5 | Medium-high (parts search) |
| Kirana Khata / Ledger Voice (same idea, two agents) | 8 | 7 | 7 | 6 | 7.1 | Low-medium |
| Lab Notebook Autopilot | 5 | 7 | 7 | 8 | 6.6 | Low |
| FitCheck | 6 | 7 | 7 | 6 | 6.5 | High |
| Heirloom Voices | 5 | 8 | 8 | 5 | 6.5 | Medium |
| Fridge Door | 6 | 7 | 6 | 6 | 6.25 | Medium |

## Leading pick: Sketch2Sim (to be confirmed by Anish)

Photograph a hand-drawn mechanism (ramps, levers, pivots, springs, a ball, a
bell) and an agent turns it into a running physics simulation, tests whether
it reaches the goal, and redraws a fixed version when it fails.

- Theme: Push the Frontier (understand and control a physical system). Indie.
- Models and jobs:
  - SAM 3.1 segments each drawn part into exact shapes and positions.
  - Muse Spark (multimodal) labels the parts, reads handwritten notes
    ("10 kg", "goal: ring the bell") and outputs a JSON scene.
  - Muse Spark Open (Fireworks or Baseten) runs the repair loop: reads the
    simulation log, edits the scene JSON, tries again.
  - Muse Voice Transcribe: spoken goals ("make it ring the bell faster").
  - Muse Image: a clean illustration of the finished, working machine.
- 3-minute demo: hold up a napkin sketch. Masks light up over each part. The
  scene runs as a live simulation. The ball falls short. The agent lists its
  attempts ("ramp too shallow, raising 12 degrees, adding a lever"). On try 3
  the bell rings. Split screen of the original sketch and the fixed version,
  then the Muse Image render. A second sketch uses a voice command.
- Bonus prizes it targets: Best Agentic Use-Case (closed loop with a
  verifier), Best Open Weight Models (repair loop on Spark Open), Most Viral
  (sketch-to-working-machine clips), Best Creative Build (small).
- 5-day plan (from the idea agent):
  - Day 1: Flask app, image upload, SAM 3.1 plus Spark to scene JSON.
  - Day 2: pymunk simulator and canvas renderer (scene JSON to frames).
  - Day 3: agent loop with simulator feedback and success checks.
  - Day 4: voice, Muse Image render, UI polish, gallery of 5 tested sketches.
  - Day 5: record video, write README, public repo (hosting optional).
- Risks and answers:
  - Messy handwriting misread: allow about 6 part types (ball, ramp, lever,
    pivot, spring, bell), pre-test on real sketches.
  - Flaky demo: deterministic simulation, cap the loop at 3 or 4 tries, keep
    a recorded backup run.
  - Looks like a toy if fixes are trivial: pick goals that need real
    reasoning.
  - Open-model latency: cap iterations, cache a backup run.
  - Impact is the weak score (students, teachers, makers).

### Day 1 gate (about 1 hour)

From India, with the credits: run 5 real sketches through SAM and Spark and
check they come back as correct scenes; check Voice Transcribe and Muse
Image work through the API. If sketch reading is poor after day 1, switch to
ShopFront Studio (lower risk), with Flakewatch as another backup.

## Backups, in short

- ShopFront Studio: a shop owner sends a Hindi voice note and a product photo.
  Voice Transcribe, Spark (plan), SAM 3.1 (cut-out), Muse Image (studio
  scenes), Spark Open (listing captions), and a Spark self-check that retries
  if the product look changed. Bonuses: Creative, Open Weights, Viral.
  Risk: "another AI photoshoot app", so lean on voice-first local language.
- Flakewatch: upload a screen recording of a bug, get a written repro, a
  failing Playwright test and a draft patch. Spark reads frames, SAM marks UI
  elements, Spark Open writes the test, a runner loops until it fails like the
  video. Bonuses: Agentic, Open Weights. Needs a safe sandbox and a controlled
  demo app.
- FixIt Crew: video of a broken thing, an agent finds the faulty part (SAM
  crop, read the label), looks for the spare, verifies its own match, outputs
  a repair plan. Bonus: Agentic, Creative, Viral. Risk: parts search needs a
  real source; avoid electrical and gas repairs.
- Kirana Khata / Ledger Voice: handwritten credit notebook or voice notes
  into customer ledgers and polite reminders in local languages. Many other
  entrants are likely to build a khata app, so originality is low.
