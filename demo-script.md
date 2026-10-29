# Three-minute demo script

**0:00–0:20 — Problem.** Hold up a sketch and say: “A maker should be able to test a mechanism idea before building it. Sketch2Sim turns this drawing into a machine the computer can verify.”

**0:20–0:45 — Perception.** Upload the sketch. Show the part masks and the scene JSON. Call out that SAM supplies geometry while Muse Spark reads the part types and the goal.

**0:45–1:25 — First simulation.** Start the run. Show the ball moving and stopping short of the bell. Point to the measured distance in the attempt log. Explain that the physics simulation is the verifier, not the language model.

**1:25–2:10 — Repair loop.** Let the repair attempts stream. Read the short reasoning line for each attempt. Show the structured edit, the rerun, and the bell being reached. Mention that Muse Spark Open can propose edits, but the schema validator rejects unsafe or unknown operations.

**2:10–2:35 — Voice and render.** Speak “make it ring the bell faster” and show the transcribed goal. Show the clean Muse Image illustration after the verifier succeeds.

**2:35–3:00 — Why Meta.** Close with: “This only works as a natural sketch workflow because the system combines segmentation, multimodal reading, voice, open-weight reasoning, and image generation. The closed loop is grounded by a deterministic physical verifier.”

Record a backup run using a cached response before recording the final video.
