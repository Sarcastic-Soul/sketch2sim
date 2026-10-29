# AGENTS.md: Meta Global AI Developer Hackathon

Solo entry, Indie track. Read `README.md` (event details, rules, rubric, prizes)
and `ideas.md` (scored shortlist, leading pick Sketch2Sim) first.

## Deadline

Submissions due Nov 4, 9:00 PM ET (Nov 5, 7:30 AM IST). Aim to have the
demo video recorded by the evening of Nov 3 (IST). No late submissions.

## Hard rules from the event

- Everything shown must be built during the event (Oct 27 to Nov 4). Keep
  commits dated inside that window and the git history honest.
- The GitHub repo must be public. Never commit `.env`, API keys or real
  secrets. Use `.env.example`.
- Must really use Meta's models (Meta Model API and/or open-weight Muse Spark
  Open or Glimmer). Muse Code and the muse.ai app are not available in India.
- Avoid the banned and generic project types listed in README.md.
- The demo video (3 minutes max, YouTube) is the main thing judges watch. It
  must clearly show what was built this week.

## Working rules

- Credits: $150 on Meta Model API. A card must be on file. Keep a spend
  limit alert at $150. Cache model results during development so we do not
  burn credits on repeat calls.
- Open-weights route: Baseten model name is `meta-models/muse-spark-open-1026`.
- Keep the project runnable locally with a README that works in a few
  commands. A hosted copy is optional; if hosted, add rate limits.
- Plain English in comments, commits, README and the demo script.
- Commit messages: conventional style (`feat:`, `fix:`, `docs:`). Never add a
  `Co-Authored-By` trailer or any AI attribution line. Commits are authored by
  the user alone. Git email `anishisbusy@gmail.com` if none is set.
- Never publish an Artifact. Local files only.
- UI work: load the `design-guardrails` skill first. Phosphor or Heroicons,
  never Lucide. No blue or purple gradients, no gradient text.

## Next steps

1. Anish adds a card on https://dev.meta.ai (Billing), sets a spend alert,
   creates an API key.
2. Day 1 gate: confirm SAM 3.1, Muse Spark vision, Voice Transcribe and Muse
   Image work through the API from India. Decide between Sketch2Sim and the
   backups in ideas.md.
3. Build in the 5-day order in ideas.md. Keep a backup demo run recorded.
4. Write the submission answers (project description, how we used Meta
   products, why Meta's models matter, feedback on Meta and partners) as we
   go, in `submission.md`.
5. Record the 3-minute demo, upload to YouTube, post the demo on X for the
   Most Viral prize, submit before the deadline.
