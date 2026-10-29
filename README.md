# Meta Global AI Developer Hackathon (Cerebral Valley)

Everything we know about the event, gathered on 29 Oct 2026. Source: the
participant guide on the event page (pasted by Anish), plus web searches.
Event page: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/details
(needs a login). Submission is on the same page ("Submit Project").

## Key dates

Event times are in Eastern Time (ET). US clocks go back on Nov 1, so IST is
ET + 9.5 hours until Oct 31 and ET + 10.5 hours from Nov 1. The event page
itself shows the end as Nov 5, 7:30 AM IST, which matches 9:00 PM ET on Nov 4.

- Oct 26: kickoff. Building period Oct 27 to Nov 4.
- Live sessions (12:00 PM ET): Oct 27 Agents 101, Oct 28 Agents 102, Oct 30
  Fireworks session on Muse open models. Office hours in Discord, 10-11 AM ET,
  weekdays (text only, in #office-hours).
- Nov 3: last full day for submission questions and technical help.
- **Nov 4, 9:00 PM ET: submissions due, and last day to claim credits.**
  That is **Nov 5, 7:30 AM IST** (the event page shows this time; an
  Internshala listing said 6:30 AM, which ignores the clock change). Late submissions are not considered.
- Nov 5 to 8: judging.
- Nov 9, 12:00 PM ET: closing ceremony. Top 10 teams (5 per track) announced,
  live final judging, winners revealed, community vote opens.
- Nov 16: community vote winner announced on Discord.

## What we must build

The project must build toward one of two problem statements, and must use
Meta's models.

1. Build for Your World: bring Meta's models into a domain you know
   firsthand. Solve a problem you know, free up time and mental space, make
   something possible that was not before.
2. Push the Frontier: use Meta's models on challenges in software, robotics,
   manufacturing, energy, materials and beyond. Give a machine a new
   capability, speed up a science experiment, or better understand and
   control a physical system.

Meta models allowed:
- Through Meta Model API: Muse Spark series (chat, reasoning, multimodal),
  Muse Wonder, Muse Image, Muse Voice Transcribe, SAM 3.1.
- Open weights: Muse Glimmer and Muse Spark Open (run on own hardware or
  through partners Baseten, Modal, Fireworks).
- Muse Code: Meta's coding agent, to write code faster.

## Tracks and prizes (total pool $1,000,000)

We enter the **Indie developer track** (individuals and students).

Indie track ($400K): 1st $150K, 2nd $100K, 3rd $75K, 4th $50K, 5th $25K.
Startup track ($550K): 1st $250K, 2nd $150K, 3rd $75K, 4th $50K, 5th $25K.

Bonus prizes from Meta ($50K). The guide does not say whether a project can
win a track prize and a bonus prize together:

| Bonus | Prize | How it is decided |
|---|---|---|
| Most Viral Project | $20,000 | Most likes, reposts and comments on the X post of the demo, counted until Nov 8 end of day. Submit the post link on the form. |
| Best Build on Meta Open Weight Models | $10,000 | Built with Muse Glimmer or Muse Spark Open, on own hardware or partner inference. Flagged in the first judging round and checked by the infrastructure partner. |
| Community Vote | $10,000 | Most votes in the public gallery, one vote per verified account. Announced Nov 16. |
| Best Agentic Use-Case | $5,000 | Strongest use of AI agents: autonomy, effectiveness, practical use. |
| Best Creative Build | $5,000 | Most original project using Muse Image or Muse Wonder. Flagged in the first round. |

## Judging

- Stage 1 (pass or fail): the project reasonably fits a theme and reasonably
  uses Meta Model API and/or Meta open-weight models, built during the event.
- Stage 2 (each scored 0 to 10):
  - Impact, 30%: real-world potential, who benefits, could people use it,
    fits a problem statement.
  - Use of Meta AI tooling, 25%: how creatively, beyond a basic
    integration, capabilities that surprise the judges.
  - Demo, 25%: working, impressive, holds up live, video is cool to watch.
  - Technical depth and execution, 20%: sound, thought-through engineering.
- Stage 3: top 5 per track are judged live on their demo videos and ranked
  with the same rubric.

## Rules

- New work only. What is presented must be built during the event. The demo
  must show only features and code built during the hackathon, and judges must
  be able to tell what was new. Failure means disqualification.
- Repository must be public.
- Team size up to 4. Solo is allowed (we are solo).
- Banned: projects that break legal, ethical or platform rules, or use code,
  data or assets we have no rights to.
- Generic or banned examples to avoid: AI medical advice, mental health
  advisors, skin detectors, basic RAG apps, simple image analyzers, simple
  "AI for education" chatbots, AI job screeners, AI nutrition coaches,
  personality analyzers, sports analyzers or coaches, anything political or
  about war.
- Official rules were to be published at kickoff and accepted by selected
  participants. Not seen by us yet, so check Discord or the event page.

## Submission form fields

- Team name, team members (listed: anishisbusy / Anish Kumar).
- Track, and which problem statement we built toward.
- X post link (only for Most Viral).
- Project description.
- Public GitHub repository link.
- 3-minute demo video link (YouTube). This is a main artifact for judges.
- How we used Meta products to build it.
- Why Meta's models are important to the solution.
- Feedback on Meta products.
- Feedback on partner technologies (Fireworks, Modal, Baseten).

There is no field for a live URL. Judging text still mentions a "live
product", so a live link is a small plus but not required. If we host one,
cap usage so visitors do not burn the API credits.

## Resources and credits

- Meta Model API credits: $150 for each accepted participant. Claim form
  submitted by Anish on 29 Oct. Credits come in batches; check the Billing
  page at https://dev.meta.ai. **A card must be on file to use credits.**
  Adding a card causes a temporary pre-authorization charge that is released
  automatically in a few business days. Set a spend limit alert at $150.
- Claim deadline: Nov 4, 9:00 PM ET.
- Platform: https://dev.meta.ai (Chat, Image, Audio, Segment, API keys, Usage,
  Models, Billing, Documentation). Anish is logged in. The platform works from
  India. The consumer Muse app (muse.ai) and Muse Code CLI are NOT available
  in India (waitlist screen), so do not plan around Muse Code.
- Baseten: $100 credits and 2M TPM rate limit, up to 2,000 people, reviewed by
  use case, email to selected. In the hackathon, use the model name
  `meta-models/muse-spark-open-1026` (the docs say `muse-spark-open`).
- Modal: $100 credits, first 1,000 participants, for open-weight models
  through Endpoints.
- Fireworks: $100 credits for shortlisted teams (emailed).
- Docs: Meta Model API Overview, Quickstart, Model list, API cookbook, API
  fundamentals, Muse code recipes, OSS model cookbook (links on the event
  page).
- Discord (instructions on the event page): #intros, #team-search,
  #questions, #office-hours (Meta team), #announcements, partner channels.

## Status as of 29 Oct 2026

- Accepted into the hackathon (Submit Project button and credits are shown).
- Credits claim form: submitted.
- Meta Model API account exists. No payment method yet, so no API key.
- Open question: whether Muse models, SAM 3.1 and Muse Image work from India
  through the API. Test on day 1 (see ideas.md and PLAN notes in AGENTS.md).
