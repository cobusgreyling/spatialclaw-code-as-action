#!/usr/bin/env python3
"""Optional Gradio UI for the three-interface conceptual demo."""

from __future__ import annotations

import json

import gradio as gr

from demo_action_interfaces import (
    GROUND_TRUTH,
    QUESTION,
    SCENE,
    code_as_action,
    single_pass_code,
    structured_tool_call,
)


def run_all() -> tuple[str, str, str, str]:
    scene_txt = "\n".join(
        f"- {p.name}: (x={p.x}, y={p.y}, z={p.z})"
        + ("  [noise]" if p.is_noise else "")
        for p in SCENE
    )
    a = single_pass_code()
    b = structured_tool_call()
    c = code_as_action()

    def fmt(r: dict) -> str:
        body = {
            "interface": r["interface"],
            "answer": r["answer"],
            "correct": r["correct"],
            "note": r["note"],
        }
        if "trajectory" in r:
            body["trajectory"] = r["trajectory"]
        if "steps" in r:
            body["steps"] = [
                {
                    "purpose": s["purpose"],
                    "shown": s["shown"],
                    "stdout": s["stdout"],
                }
                for s in r["steps"]
            ]
        return json.dumps(body, indent=2)

    header = (
        f"**Question:** {QUESTION}\n\n"
        f"**Ground truth:** `{GROUND_TRUTH}`\n\n"
        f"**Scene**\n{scene_txt}"
    )
    return header, fmt(a), fmt(b), fmt(c)


def build() -> gr.Blocks:
    with gr.Blocks(title="SpatialClaw — Action Interfaces") as demo:
        gr.Markdown(
            """
# SpatialClaw conceptual demo: three action interfaces

Educational only — not the official SpatialClaw stack.

Thesis: effective agents should not be hemmed in by static tools;
they should compose tools in code as the task requires.

Project: [spatialclaw.github.io](https://spatialclaw.github.io/)
            """.strip()
        )
        btn = gr.Button("Run comparison", variant="primary")
        overview = gr.Markdown()
        with gr.Row():
            out_a = gr.Code(label="(a) Single-pass code", language="json")
            out_b = gr.Code(label="(b) Structured tool-call", language="json")
            out_c = gr.Code(label="(c) Code-as-action", language="json")
        btn.click(fn=run_all, outputs=[overview, out_a, out_b, out_c])
        demo.load(fn=run_all, outputs=[overview, out_a, out_b, out_c])
    return demo


if __name__ == "__main__":
    build().launch()
