# SpatialClaw: Code Is the Action Interface Universal Agents Were Waiting For

## NVIDIA’s training-free spatial agent does not win by adding more tools. It wins by letting the agent compose, inspect and revise tools through code — on the fly.

*[Upload header.jpg as the story image / first image]*

---

## In Short

The bottleneck in tool-augmented agents is not the tool menu.

It is the *action interface* — how tools are invoked, how their outputs are held, and whether the agent can revise after seeing intermediate evidence.

[SpatialClaw](https://spatialclaw.github.io/) (NVIDIA Research, 2026) is a training-free spatial reasoning agent that treats **code as the action interface**.

A VLM writes one Python cell per step inside a **persistent kernel**.

Perception outputs become ordinary variables.

NumPy, SciPy and Matplotlib are first-class.

The agent composes, inspects and revises.

Result: **59.9%** average accuracy across **20** spatial benchmarks — **+11.2 points** over the prior spatial agent (SpaceTools-Toolshed), with consistent gains across **six** VLM backbones and **no** benchmark- or model-specific adaptation.

This is not a robotics-only story.

It is empirical confirmation of a thesis I have been writing toward for months:

> Truly effective agents must not be hemmed in by static tools. They must develop and compose tools on the fly, as the task requires.

See:

- [Universal Agents](https://cobusgreyling.medium.com/universal-agents-3b9f566868ba)
- [Universal Agent Thesis](https://cobusgreyling.medium.com/universal-agent-thesis-db16bd7dc650)
- [Code-Writing Agents as Universal Adaptors](https://cobusgreyling.medium.com/the-new-paradigm-of-code-writing-ai-agents-as-universal-adaptors-51e64d3c4519)

**Project page:** [spatialclaw.github.io](https://spatialclaw.github.io/)

**Paper:** [arXiv:2606.13673](https://arxiv.org/abs/2606.13673)

**Code:** [github.com/NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw)

**Companion repo for this post:** [github.com/cobusgreyling/spatialclaw-code-as-action](https://github.com/cobusgreyling/spatialclaw-code-as-action)

---

## The problem is not “more tools”

Spatial reasoning — where things are, how they relate, how they move in 3D/4D — remains hard for vision-language models.

The obvious fix is tool augmentation: segmenters, depth estimators, pose modules.

That helps.

But only up to a point.

Prior spatial agents largely chose one of two interfaces.

**Single-pass code**

- What it does well: flexible programs; full NumPy / SciPy expressiveness
- Where it breaks: must commit to a complete strategy *before* seeing intermediate evidence

**Structured tool-call**

- What it does well: clean typed APIs; safe dispatch
- Where it breaks: poor at free composition; cannot invent test-time geometry on demand

**SpatialClaw (code as action)**

- What it does well: compose, inspect, revise in a persistent kernel
- Where it breaks: needs a disciplined prompt + sandbox; perception still bounds quality

The paper’s central claim is precise:

> The capability of a tool-augmented agent is bounded not by **which** tools are available, but by **how** they can be composed.

That sentence should be pinned above every agent framework design review.

---

## What SpatialClaw actually is

SpatialClaw is **training-free**.

No fine-tuning.

No reward model.

No benchmark-specific adapters.

For each question it:

1. Spins up a **persistent Python kernel** pre-loaded with input frames, perception primitives and scientific libraries
2. Optionally plans (text plan only — no code, no images in the planner for efficiency)
3. Has the VLM write **one executable cell per step**
4. Executes the cell under static safety checks
5. Feeds back stdout, variable summaries, errors and images registered via `show()`
6. Lets the agent revise until `ReturnAnswer()` or a step budget is hit

Public kernel entry points include:

- `InputImages` / `Metadata` — frames and temporal structure
- `tools` — perception (for example Depth Anything 3 reconstruction, SAM 3 masks) plus geometry helpers
- `show(...)` — visual inspection of intermediates
- `vlm` — targeted side queries / grounding
- `ReturnAnswer(...)` — commit

Perception outputs are not opaque tool payloads.

They are **variables**.

You can index them, combine them with SciPy KD-trees, run SVD on a plane, plot a cross-product, and re-use the result sixty steps later.

That is the difference between *calling tools* and *programming with evidence*.

---

## The numbers that matter

On Gemma 4-31B, across 20 benchmarks:

- **SpatialClaw:** 59.9% average
- **No-tool baseline:** 53.4%
- **SpaceTools-Toolshed:** 48.7% (−11.2 vs SpatialClaw)

Action-interface ablation — same toolset, same prompt, only the interface changes:

- **No-tool baseline** — 53.4%
- **Single-pass code** — 55.2% (+1.8)
- **Structured tool-call** — 56.7% (+3.3)
- **SpatialClaw (code as action)** — **59.9% (+6.5)**

Largest lifts land where chained geometric computation across frames and viewpoints is required — camera motion, multi-view reasoning, relative direction.

Categories that structured APIs struggle to pre-declare.

When SpatialClaw wins over structured tool-call, an LLM judge attributes:

- **52.2%** — code composition (chaining tools into one coherent program)
- **19.5%** — control flow (`if` / `for` over intermediate results)
- **28.3%** — interface-neutral

Over **70%** of those wins come from capabilities a fixed API does not easily provide.

And the killer ablation: **remove the utility wrappers**, keep only core perception + NumPy/SciPy, and performance barely moves.

The interface — not the hand-engineered helper library — is doing the work.

Remove perception tools entirely and the code interface still beats the no-tool baseline.

Code alone is not enough for hard 3D, but the *action interface contribution* is real and measurable.

---

## Why this is a universal-agent result

I defined a [universal agent](https://cobusgreyling.medium.com/universal-agents-3b9f566868ba) as a system that can:

1. **Perceive** its environment
2. **Reason** about tasks and decompose them
3. **Act** on the environment (write and execute code, use APIs)
4. **Learn** from feedback (see errors, iterate, improve)
5. **Operate** across extended horizons without being locked to a pre-declared tool surface

The core failure mode of today’s agents is tool hem:

> An AI Agent with 50 specialised tools might excel in narrow domains but falter on a simple requirement the menu never listed — for example, an arbitrary geometric composition that only becomes obvious mid-trajectory.

Static tools are hands with a fixed number of fingers.

Code is a workshop.

In the [Universal Agent Thesis](https://cobusgreyling.medium.com/universal-agent-thesis-db16bd7dc650) I argued:

- The integration layer is collapsing toward **terminal / code** as the universal adapter
- Agents must **explore and compose** rather than wait for curated schemas
- The endpoint is agents that **build tools**, not only call them
- Autonomy without **boundaries** (sandbox, policy, skill-edge awareness) is reckless — not universal

SpatialClaw sits exactly on that map:

**Do not hem the agent in static tools**
→ Code cells compose perception + math at test time

**Build / adapt tools as required**
→ New spatial analyses are new compositions, not new API entries

**Observe intermediate state**
→ Persistent kernel + `show()` + variable summaries

**Iterate on failure**
→ Static check failures and wrong evidence feed the next cell

**Transfer without reconfiguration**
→ Same prompt and tools across 6 backbones and 20 benchmarks

**Bound the blast radius**
→ AST safety checks, restricted builtins, disposable kernel per example

This is the same arc as Claude Code writing its own integration scripts, OpenAI freeform functions, terminal-native agents, and code-writing agents as [universal adaptors](https://cobusgreyling.medium.com/the-new-paradigm-of-code-writing-ai-agents-as-universal-adaptors-51e64d3c4519).

SpatialClaw simply makes the claim measurable on hard spatial tasks.

---

## Spontaneous tool composition is the signal

One of the paper’s most important qualitative findings: **without category-specific routing**, the agent spontaneously picks the right primitives from question semantics.

- Distance → KD-tree search and norms
- Direction → dot products and angular ops
- Camera motion → pose composition and transform chains

That is not “tool routing.”

That is **reasoning in the medium of code**.

Structured tool-call interfaces fight this behavior because every composition must be anticipated as an API surface.

Single-pass code can express it, but only if the agent guesses the full graph before seeing a single mask.

Code-as-action with persistence is the middle path that actually matches how humans do geometry: compute a little, look, correct, recompute.

---

## What this does *not* prove

Stay honest about scope.

- SpatialClaw does not invent better perception. When SAM or depth fails, the agent fails more slowly and more informatively — not magically.
- It is not a general enterprise agent runtime. It is a research framework for spatial reasoning.
- Training-free does not mean cost-free. Multi-step VLM + perception tool calls burn tokens and GPU time.
- A powerful interface without sandbox discipline is a security problem, not a product. Code-as-action requires the enforcement layer I covered in [OpenShell Secure Agents](https://github.com/cobusgreyling/openshell-secure-agents) — policy outside the agent’s control.
- Universal agency still needs **skill boundary awareness** ([Skill Boundary Problem](https://github.com/cobusgreyling/skill-boundary)): knowing when to stop, not only how to compose.

The paper itself is clear: the remaining bottleneck is perceptual quality of the backbone and of the tools it composes.

---

## The design lesson for builders

If you are building agents today, SpatialClaw suggests a stack order:

1. **Action interface first.** Prefer code (or terminal) over a frozen tool schema when the task space is open-ended.
2. **State that persists.** Intermediate evidence must be variables, not one-shot tool JSON that evaporates.
3. **Observe before commit.** `show()`, plots, summaries — make intermediate world state legible to the model.
4. **Discipline via prompt + harness, not via a bigger menu.** SpatialClaw uses one general spatial-reasoning system prompt across everything.
5. **Enforce safety below the model.** AST checks, sandboxes, network/fs policy — never “please don’t run `os.system`.”
6. **Measure interface ablations.** Same tools, different interface. If you only ship tool lists, you will never see the +3 to +6 pp hiding in composition.

Or, shorter:

> Stop adding tools. Start giving the agent a real computer and a disciplined loop.

---

## Closing

I have been arguing that universal agents are the future of AI agents — systems that land in an environment, explore what is there, build what is missing, and operate within discovered edges.

SpatialClaw is a clean, high-signal data point from NVIDIA Research that **the action interface is a first-class research surface**, not plumbing.

Code as action is not a coding-assistant gimmick.

It is how open-ended perception and reasoning scale when the next step cannot be named in advance.

Static tools hem agents in.

Code lets them grow hands when they need them.

That is the universal agent thesis — now measured at 59.9% across twenty spatial benchmarks.

---

## References

- SpatialClaw project: [https://spatialclaw.github.io/](https://spatialclaw.github.io/)
- Paper: Cho et al., *SpatialClaw: Rethinking Action Interface for Agentic Spatial Reasoning*, arXiv:2606.13673, 2026
- Official code: [https://github.com/NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw)
- This post + conceptual demo: [https://github.com/cobusgreyling/spatialclaw-code-as-action](https://github.com/cobusgreyling/spatialclaw-code-as-action)
- SpaceTools-Toolshed: [https://spacetools.github.io/](https://spacetools.github.io/)
- [Universal Agents](https://cobusgreyling.medium.com/universal-agents-3b9f566868ba)
- [Universal Agent Thesis](https://cobusgreyling.medium.com/universal-agent-thesis-db16bd7dc650)
- [The New Paradigm of Code-Writing AI Agents as Universal Adaptors](https://cobusgreyling.medium.com/the-new-paradigm-of-code-writing-ai-agents-as-universal-adaptors-51e64d3c4519)
- [AI Agents & The Skill Boundary Problem](https://github.com/cobusgreyling/skill-boundary)
- [OpenShell Secure Agents](https://github.com/cobusgreyling/openshell-secure-agents)

---

*[Chief Evangelist](https://www.linkedin.com/in/cobusgreyling/) @ [Kore.ai](https://blog.kore.ai/cobus-greyling/the-shifting-vocabulary-of-ai/) | I’m passionate about exploring the intersection of AI and language. Language Models, AI Agents, Agentic Apps, Dev Frameworks & Data-Driven Tools shaping tomorrow.*

---

**Suggested Medium tags**

`Universal Agents` · `AI Agents` · `Artificial Intelligence` · `Machine Learning` · `Large Language Models` · `NVIDIA` · `Spatial AI` · `Robotics`

**Publish checklist**

1. New story → paste from `medium.md` (or Import)
2. Set title + subtitle from the first two headings
3. Upload `header.jpg` as featured image
4. Add tags above
5. Link-check Medium internal links to your prior posts
6. Optional: embed or link the GitHub demo repo
