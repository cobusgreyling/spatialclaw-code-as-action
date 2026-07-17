# SpatialClaw: Code as the Action Interface

![SpatialClaw — code as the action interface](header.jpg)

Blog post and conceptual demo on **NVIDIA SpatialClaw** — a training-free spatial reasoning agent that uses **code as the action interface**, not a fixed tool menu.

**Thesis link:** truly effective agents must not be hemmed in by static tools; they must compose and develop tools on the fly. SpatialClaw is strong empirical evidence for that claim on hard 3D/4D spatial tasks.

## Blog

[blog.md](blog.md) — Why the *action interface* (not the tool list) is the real bottleneck; how SpatialClaw's persistent Python kernel works; the 59.9% / +11.2 pp results; and how this maps to the [Universal Agent Thesis](https://cobusgreyling.medium.com/universal-agent-thesis-db16bd7dc650).

### Primary sources

| Resource | Link |
| --- | --- |
| Project page | [spatialclaw.github.io](https://spatialclaw.github.io/) |
| Paper | [arXiv:2606.13673](https://arxiv.org/abs/2606.13673) |
| Official code | [github.com/NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw) |
| Universal Agents (Medium) | [Universal Agents](https://cobusgreyling.medium.com/universal-agents-3b9f566868ba) |
| Universal Agent Thesis | [Thesis](https://cobusgreyling.medium.com/universal-agent-thesis-db16bd7dc650) · [repo](https://github.com/cobusgreyling/universal-agent-thesis) |

## Conceptual demo

This repo does **not** re-implement SpatialClaw (use the official NVlabs code for that). It ships a small, dependency-light demo that makes the **three action interfaces** concrete on a toy geometry task:

1. **Single-pass code** — commit to a full strategy before seeing intermediates  
2. **Structured tool-call** — fixed JSON-style tools only  
3. **Code-as-action (SpatialClaw-style)** — multi-step cells in a persistent namespace, with inspect & revise  

### Run

```bash
python3 demo_action_interfaces.py
```

No API key, GPU, or NVIDIA NIM required.

Optional Gradio UI:

```bash
pip install -r requirements.txt
python3 demo_gradio.py
```

### What the demo shows

- Same scene (synthetic 3D points + object labels)
- Same question: *which object is closest to the camera along the viewing ray, after filtering noise?*
- How single-pass can hard-code a wrong assumption
- How structured tools fail when the needed composition is not in the API
- How a persistent code kernel composes filter → project → nearest-neighbor and revises after inspection

## Security note

Do not put NVIDIA NIM / API keys in this repository. If you experiment with NIM-hosted VLMs against the official SpatialClaw stack, use environment variables only (`export NGC_API_KEY=...`) and rotate any key that has been shared in chat or committed by mistake.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0) — see [LICENSE](LICENSE).

SpatialClaw itself is NVIDIA Research work; this repository is independent commentary and educational code.
