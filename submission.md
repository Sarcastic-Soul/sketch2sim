# Sketch2Sim submission draft

## Project description

Sketch2Sim lets a student, teacher, or maker photograph a hand-drawn mechanism and test the idea before building it. Meta models read the sketch into a structured scene. A deterministic Pymunk simulation checks whether the machine reaches its goal. When it fails, a bounded agent edits only safe scene fields and tries again. The demo shows the failed run, the verifier's measurements, the repair attempts, and the verified machine.

## How we used Meta products

- SAM 3.1 identifies the geometry of drawn parts.
- Muse Spark reads part labels, handwritten notes, and the goal from the image.
- Muse Spark Open proposes structured repairs from the physics log through Baseten or Modal.
- Muse Voice Transcribe turns a spoken goal into the simulation goal.
- Muse Image renders the successful machine as a clean illustration.

Every model response is cached locally. The physics verifier remains deterministic and does not accept free-form model output as executable code.

## Why Meta models matter

The input is both visual and informal: a photograph of a drawing, handwritten annotations, and optionally a spoken instruction. A text-only interface would force the user to rebuild the idea as a data structure. Meta's multimodal, segmentation, voice, and image capabilities let the user stay in the medium where the idea started while the verifier works with precise geometry.

## Feedback on Meta products

To complete after the India API gate: record model IDs, latency, failure modes, image quality, and whether the API documentation made multimodal and segmentation requests easy to debug.

## Feedback on partner technologies

To complete after testing Baseten or Modal: record time to first response, structured JSON reliability, setup friction, and whether the open-weight repair loop was practical for a live demo.

## Links

- Repository: https://github.com/Sarcastic-Soul/sketch2sim
- Demo video: TBD
- X post: TBD
