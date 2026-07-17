# What Is NVIDIA SpatialClaw?

![SpatialClaw](header.jpg)

Simple explainer blog and a small conceptual demo of **NVIDIA SpatialClaw** — a training-free spatial reasoning agent that uses **code as the action interface**.

## Blog

- [blog.md](blog.md) — GitHub version
- [medium.md](medium.md) — Medium paste-ready version

### Primary sources

| Resource | Link |
| --- | --- |
| Project page | [spatialclaw.github.io](https://spatialclaw.github.io/) |
| Paper | [arXiv:2606.13673](https://arxiv.org/abs/2606.13673) |
| Official code | [github.com/NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw) |

## Conceptual demo

Not the official SpatialClaw stack. A tiny stdlib demo of three action interfaces on a toy geometry task:

1. Single-pass code  
2. Structured tool-call  
3. Code-as-action (inspect & revise in a persistent namespace)

```bash
python3 demo_action_interfaces.py
```

Optional Gradio UI:

```bash
pip install -r requirements.txt
python3 demo_gradio.py
```

## License

Creative Commons Attribution 4.0 International (CC BY 4.0) — see [LICENSE](LICENSE).

SpatialClaw is NVIDIA Research work; this repository is independent commentary and educational code.
