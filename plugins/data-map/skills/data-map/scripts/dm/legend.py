"""legend.json: the single record of every layer's encoding, its answers, and the decisions behind it."""

from __future__ import annotations

import json
from pathlib import Path

EXPR = {
    "classes": {
        "maplibre": {"fill-color": ["get", "dm_fill"]},
        "deck": {"getFillColor": "properties.dm_fill"},
    },
    "sizes": {
        "maplibre": {"circle-radius": ["get", "dm_r"], "circle-sort-key": ["get", "dm_order"], "circle-color": ["get", "dm_fill"]},
        "deck": {"getRadius": "properties.dm_r", "radiusUnits": "pixels", "getFillColor": "properties.dm_fill"},
    },
    "flows": {
        "maplibre": {"line-width": ["get", "dm_width"], "line-sort-key": ["get", "dm_order"], "line-color": ["get", "dm_fill"]},
        "maplibre_arrows": {"icon-rotate": ["get", "dm_bearing"], "icon-rotation-alignment": "map", "symbol-sort-key": ["get", "dm_order"]},
        "maplibre_nodes": {"circle-radius": ["get", "dm_r"], "circle-sort-key": ["get", "dm_order"], "circle-color": ["get", "dm_fill"]},
        "deck": {"getWidth": "width", "widthUnits": "pixels", "getSourcePosition": "source", "getTargetPosition": "target"},
    },
}


def empty() -> dict:
    return {"version": 1, "layers": {}, "answers": {}, "decisions": []}


def load(path: Path) -> dict:
    if path.exists():
        doc = json.loads(path.read_text())
        base = empty()
        base.update(doc)
        return base
    return empty()


def merge(doc: dict, name: str, layer: dict, answers: dict | None, decisions: list) -> dict:
    """Replaces this layer's entry, answers, and decisions, and keeps every other layer's."""
    layer = dict(layer, expr=EXPR[layer["kind"]])
    doc["layers"][name] = layer
    if answers is not None:
        doc["answers"][name] = answers
    kept = [d for d in doc["decisions"] if d.get("layer") != name] + [dict(d, layer=name) for d in decisions]
    rank = {layer_name: i for i, layer_name in enumerate(doc["layers"])}
    doc["decisions"] = sorted(kept, key=lambda d: rank.get(d.get("layer"), len(rank)))
    return doc


def update(path: Path, name: str, layer: dict, answers: dict | None, decisions: list) -> dict:
    doc = merge(load(path), name, layer, answers, decisions)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    return doc


def decision(rule: str, choice: str, why: str, *sources: str) -> dict:
    return {"rule": rule, "choice": choice, "why": why, "sources": list(sources)}
