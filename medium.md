# What Is NVIDIA SpatialClaw?

## A simple explainer of NVIDIA Research’s training-free spatial reasoning agent

*[Upload header.jpg as the story / featured image]*

---

## In Short

**SpatialClaw** is a training-free AI agent from NVIDIA Research that helps vision-language models answer hard questions about space — where things are, how they relate, and how they move in 3D and video.

It does not fine-tune a new model.

Instead, it gives the model a **persistent Python workspace**.

The model writes small pieces of code, runs them, looks at the results, and tries again until it can answer.

On 20 spatial benchmarks it reaches **59.9%** average accuracy — about **+11 points** over a strong prior spatial agent — using the same setup across six different model backbones.

**Project:** [spatialclaw.github.io](https://spatialclaw.github.io/)

**Paper:** [arXiv:2606.13673](https://arxiv.org/abs/2606.13673)

**Code:** [github.com/NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw)

**This post + demo:** [github.com/cobusgreyling/spatialclaw-code-as-action](https://github.com/cobusgreyling/spatialclaw-code-as-action)

---

## The problem it targets

Vision-language models are good at describing images.

They are weaker at precise spatial questions, for example:

- Which object is closer to the camera?
- Is the door left or right of the sink if the wall faces east?
- How far is the sofa from the toilet in meters?
- Did the person turn left or right?

Those questions need geometry: depth, masks, camera pose, distances, angles — often across multiple views or video frames.

A common fix is to give the model **tools**: a segmenter, a depth estimator, and so on.

That helps.

But *how* the model is allowed to use those tools matters a lot.

---

## Three ways agents use tools

SpatialClaw compares three styles.

### 1. Single-pass code

The model writes one full Python program and runs it once.

Flexible, but it must commit to a full plan before it sees any intermediate result.

A bad assumption early on is hard to fix.

### 2. Structured tool calls

The model picks named tools with typed inputs and outputs (think JSON tool calling).

Clean and controlled, but awkward when the task needs a custom combination the API did not anticipate — for example “segment these objects, project them into 3D, then run a nearest-neighbor search with my own filter.”

### 3. SpatialClaw: code as the action interface

The model writes **one Python cell at a time** inside a **persistent kernel**.

Outputs from previous steps stay as normal Python variables.

The model can print values, plot images, inspect masks, and revise the next step.

That is the core idea:

> Same tools. Different interface. Code that can compose, inspect, and revise.

---

## How SpatialClaw works (simple loop)

For each question:

1. **Start a Python kernel** pre-loaded with the input images/frames and helpful libraries (NumPy, SciPy, Matplotlib).
2. **Optional plan** — outline the analysis in text.
3. **Write a code cell** — call perception tools, do math, plot something.
4. **Run it** (with basic safety checks).
5. **Feed results back** — printed numbers, variable summaries, images shown via `show()`.
6. **Repeat** until the model submits an answer with `ReturnAnswer()`, or hits a step limit.

### What is already in the toolbox?

Typical building blocks include:

- **Images / video frames** and basic metadata
- **Segmentation** (for example SAM 3)
- **3D reconstruction / depth** (for example Depth Anything 3)
- **Math and plotting** libraries
- Helpers to **show** intermediate images and optionally ask a side VLM for grounding or extra questions

Important nuance: SpatialClaw does **not** invent brand-new specialist tools on the fly (it does not train a new depth network mid-task).

It **writes code** that uses and combines the tools and libraries it already has — including custom geometry that no fixed tool API listed in advance.

---

## Why that matters

The paper’s claim is blunt:

> Agent capability is limited less by *which* tools you ship, and more by *how* the agent can compose them.

Supporting evidence:

- **Action-interface ablation** (same tools and prompt; only the interface changes): code-as-action beats single-pass code and structured tool calls.
- **Remove utility helper functions** and keep only core perception + NumPy/SciPy: performance barely drops. The flexible code interface carries a lot of the gain.
- **Biggest wins** show up on multi-view and 4D/video-style tasks — places that need chained geometric steps across frames and viewpoints.
- Gains hold across **six backbones** without retuning the prompt per model or per benchmark.

When SpatialClaw beats structured tool calling, most of the wins are attributed to **composition** and **control flow** in code — things a fixed tool menu struggles to express.

---

## What SpatialClaw is not

- Not a general chatbot product
- Not a claim that code replaces good perception (bad depth or masks still break the pipeline)
- Not free at runtime (multi-step model calls plus perception tools cost compute)
- Not unrestricted code execution in production without a sandbox

It is a research framework that shows a better *interface* for spatial agents.

---

## Bottom line

**SpatialClaw** = a vision-language model + a persistent Python notebook-like kernel + perception tools, looping until it can answer a spatial question.

Write code → run → look → revise → answer.

No task-specific training.

Strong results across many spatial benchmarks.

The lesson is simple: for open-ended spatial reasoning, **code is a better action interface than a fixed list of tool calls**.

---

## References

- SpatialClaw project: [https://spatialclaw.github.io/](https://spatialclaw.github.io/)
- Cho et al., *SpatialClaw: Rethinking Action Interface for Agentic Spatial Reasoning*, arXiv:2606.13673, 2026
- Official code: [https://github.com/NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw)
- This post + conceptual demo: [https://github.com/cobusgreyling/spatialclaw-code-as-action](https://github.com/cobusgreyling/spatialclaw-code-as-action)

---

*[Chief Evangelist](https://www.linkedin.com/in/cobusgreyling/) @ Kore.ai | Exploring the intersection of AI and language — language models, agents, frameworks, and data-driven tools.*

---

**Suggested Medium tags**

`AI Agents` · `Artificial Intelligence` · `Machine Learning` · `NVIDIA` · `Spatial AI` · `Computer Vision` · `Large Language Models`

**Publish checklist**

1. New story → paste from this file
2. Title + subtitle from the first two headings
3. Upload `header.jpg` as featured image
4. Add tags above
5. Optional: link the GitHub demo repo
