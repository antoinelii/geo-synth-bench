# 🛰️ GeoSynthBench

Synthetic Geospatial Dataset for Structured Reasoning Evaluation

<p align="left"> <img src="https://img.shields.io/badge/python-3.12-blue.svg" /> <img src="https://img.shields.io/badge/uv-managed-blueviolet.svg" /> <img src="https://img.shields.io/badge/lint-ruff-informational.svg" /> <img src="https://img.shields.io/badge/tests-pytest-lightgrey.svg" /> <img src="https://img.shields.io/badge/license-MIT-black.svg" /> </p>

## Overview

GeoSynthBench is a controllable synthetic data generator for evaluating structured geospatial reasoning in multimodal models.
Rather than testing only perception, it probes:

- Spatial & topological reasoning
- Temporal change understanding
- Policy & rule-based inference
- Counterfactual reasoning
- Uncertainty handling

Each example includes rendered world state (t₀, optional t₁), a reasoning question, and deterministic ground-truth answers.

## Task Ladder

- Tasks scale in reasoning dep
- Perception — object detection & counting
- Topology — connectivity, intersections
- Temporal — change & disruption analysis
- Policy — zoning or rule violations
- Counterfactual / Uncertainty — hypothetical reasoning

The world state is generated symbolically first, then rendered — ensuring traceable reasoning and perfect labels.

## Dataset Format

Each example is stored in .jsonl:

<pre>
{
  "id": "example_000123",
  "prompt": "Is Building A reachable after the flood?",
  "answer": "no",
  "image_path_t0": "assets/example_000123_t0.png",
  "image_path_t1": "assets/example_000123_t1.png",
  "metadata": {
    "task_type": "temporal_connectivity",
    "difficulty": 3
  }
}
</pre>

A small sample dataset (hundreds of examples) is included.

## Installation

<pre>
uv sync
</pre>

## Generate Data

## Why Synthetic?

Synthetic generation enables:

Controlled reasoning difficulty

Explicit ground truth

Deterministic reproducibility

Adversarial edge-case construction

GeoSynthBench is designed to evaluate reasoning depth, not just perception.
