#!/usr/bin/env python3
"""
Conceptual demo: three action interfaces for a toy spatial task.

This is NOT SpatialClaw. It illustrates why "code as action" (persistent
multi-step composition) beats single-pass code and fixed tool-call menus
when the right intermediate filter only becomes obvious after inspection.

Run:
    python3 demo_action_interfaces.py
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Synthetic scene (camera at origin looking +Z)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Point:
    name: str
    x: float
    y: float
    z: float  # depth along camera axis
    is_noise: bool = False


SCENE = [
    Point("sofa", -0.4, 0.1, 3.2),
    Point("table", 0.2, -0.1, 2.1),
    Point("lamp", 0.8, 0.3, 4.0),
    Point("sensor_glitch", 0.01, 0.0, 0.4, is_noise=True),  # near-camera artifact
    Point("plant", -0.9, 0.2, 2.8),
]

QUESTION = (
    "Which real object is closest to the camera along the viewing axis "
    "(ignore near-field sensor noise with depth < 0.5 m)?"
)

GROUND_TRUTH = "table"  # depth 2.1 after noise filter


# ---------------------------------------------------------------------------
# (a) Single-pass code — commits before observing intermediates
# ---------------------------------------------------------------------------

def single_pass_code() -> dict[str, Any]:
    """
    Writes one complete program. A common failure mode: forgetting noise
    filtering because it was not anticipated before execution.
    """
    code = """
# committed strategy: nearest by raw z (no intermediate inspection)
nearest = min(SCENE, key=lambda p: p.z)
answer = nearest.name
"""
    ns: dict[str, Any] = {"SCENE": SCENE}
    exec(code, ns, ns)
    return {
        "interface": "single-pass code",
        "answer": ns["answer"],
        "correct": ns["answer"] == GROUND_TRUTH,
        "note": "Committed to min(z) before seeing the near-field glitch.",
        "code": code.strip(),
    }


# ---------------------------------------------------------------------------
# (b) Structured tool-call — fixed API only
# ---------------------------------------------------------------------------

TOOL_SPECS = {
    "list_objects": "Return object names in the scene.",
    "get_depth": "Return depth z for a named object.",
    "nearest_by_depth": "Return name of object with minimum raw depth (no filters).",
}


def tool_list_objects() -> list[str]:
    return [p.name for p in SCENE]


def tool_get_depth(name: str) -> float:
    for p in SCENE:
        if p.name == name:
            return p.z
    raise KeyError(name)


def tool_nearest_by_depth() -> str:
    return min(SCENE, key=lambda p: p.z).name


def structured_tool_call() -> dict[str, Any]:
    """
    Agent may only call pre-registered tools. There is no
    filter_depth_range or compose_with_predicate tool — so the agent
    cannot express "ignore depth < 0.5" without a new API entry.
    """
    trajectory = []
    names = tool_list_objects()
    trajectory.append({"tool": "list_objects", "result": names})

    depths = {n: tool_get_depth(n) for n in names}
    trajectory.append({"tool": "get_depth*", "result": depths})

    answer = tool_nearest_by_depth()
    trajectory.append({"tool": "nearest_by_depth", "result": answer})

    return {
        "interface": "structured tool-call",
        "answer": answer,
        "correct": answer == GROUND_TRUTH,
        "note": (
            "API has no depth-filter or custom predicate. "
            "Agent is stuck with nearest_by_depth → picks sensor_glitch."
        ),
        "available_tools": TOOL_SPECS,
        "trajectory": trajectory,
    }


# ---------------------------------------------------------------------------
# (c) Code-as-action — persistent kernel, compose / inspect / revise
# ---------------------------------------------------------------------------

class PersistentKernel:
    """Tiny stand-in for SpatialClaw's persistent Python workspace."""

    def __init__(self) -> None:
        self.ns: dict[str, Any] = {
            "SCENE": SCENE,
            "math": math,
            "json": json,
        }
        self.history: list[dict[str, Any]] = []
        self._shown: list[str] = []

    def show(self, label: str, value: Any) -> None:
        self._shown.append(f"{label}: {value!r}")

    def run_cell(self, purpose: str, code: str) -> dict[str, Any]:
        self.ns["show"] = self.show
        local_shown_before = len(self._shown)
        stdout: list[str] = []

        def _print(*args: Any, **kwargs: Any) -> None:
            stdout.append(" ".join(str(a) for a in args))

        self.ns["print"] = _print
        error = None
        try:
            exec(code, self.ns, self.ns)
        except Exception as e:  # educational demo only
            error = f"{type(e).__name__}: {e}"

        step = {
            "purpose": purpose,
            "code": code.strip(),
            "stdout": stdout,
            "shown": self._shown[local_shown_before:],
            "error": error,
            "vars": {
                k: repr(v)[:80]
                for k, v in self.ns.items()
                if k not in {"SCENE", "math", "json", "show", "print"}
                and not k.startswith("_")
                and not callable(v)
            },
        }
        self.history.append(step)
        return step


def code_as_action() -> dict[str, Any]:
    """
    Multi-step SpatialClaw-style loop: write cell → inspect → revise.
    """
    k = PersistentKernel()

    # Step 1: survey depths
    k.run_cell(
        "Survey depths",
        """
depths = {p.name: p.z for p in SCENE}
show("depths", depths)
print("min raw", min(depths, key=depths.get))
""",
    )

    # Step 2: notice near-field glitch and filter
    k.run_cell(
        "Filter noise after inspection",
        """
raw_nearest = min(SCENE, key=lambda p: p.z).name
show("raw_nearest", raw_nearest)
filtered = [p for p in SCENE if p.z >= 0.5 and not p.is_noise]
show("filtered_names", [p.name for p in filtered])
""",
    )

    # Step 3: recompute nearest on filtered set; optional metric compose
    k.run_cell(
        "Compose nearest on filtered points",
        """
import math as _m
def cam_distance(p):
    return _m.sqrt(p.x*p.x + p.y*p.y + p.z*p.z)

ranked = sorted(filtered, key=lambda p: p.z)
answer = ranked[0].name
show("ranked_by_z", [(p.name, p.z) for p in ranked])
show("answer", answer)
print(answer)
""",
    )

    answer = k.ns.get("answer")
    return {
        "interface": "code-as-action (SpatialClaw-style)",
        "answer": answer,
        "correct": answer == GROUND_TRUTH,
        "note": (
            "Inspected intermediates, filtered noise, recomposed nearest. "
            "No new tool was registered — composition happened in code."
        ),
        "steps": k.history,
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 72)
    print("THREE ACTION INTERFACES — toy spatial task")
    print("=" * 72)
    print(f"\nQuestion: {QUESTION}")
    print(f"Ground truth: {GROUND_TRUTH}\n")

    results = [
        single_pass_code(),
        structured_tool_call(),
        code_as_action(),
    ]

    for r in results:
        mark = "OK" if r["correct"] else "FAIL"
        print("-" * 72)
        print(f"[{mark}] {r['interface']}")
        print(f"  answer : {r['answer']}")
        print(f"  note   : {r['note']}")
        if r["interface"].startswith("code-as-action"):
            print(f"  steps  : {len(r['steps'])} cells in persistent kernel")
            for i, step in enumerate(r["steps"], 1):
                print(f"    cell {i}: {step['purpose']}")
                if step["shown"]:
                    for s in step["shown"]:
                        print(f"      show → {s}")

    print("-" * 72)
    print("\nTakeaway:")
    print("  Same scene. Same question. Only the action interface changes.")
    print("  Static tools and single-pass commits hem the agent in.")
    print("  Persistent code lets the agent develop the filter it needs on the fly.")
    print()
    print("See blog.md and https://spatialclaw.github.io/")


if __name__ == "__main__":
    main()
