"""
Copyright (c) 2020 Hecong Wang

This software is released under the MIT License.
https://opensource.org/licenses/MIT
"""
from __future__ import annotations

from typing import NamedTuple, Tuple
from uuid import UUID


class Path(NamedTuple):
    weight: float
    content: str


class Sample(NamedTuple):
    error: float
    target: Tuple[int, ...]
    result: Tuple[float, ...]
    human_paths: Tuple[Path, ...]
    machine_paths: Tuple[Path, ...]


class Instance(NamedTuple):
    human_size: int
    machine_size: int
    samples: Tuple[Sample, ...]


class Experiment(NamedTuple):
    story: UUID
    sentence: int
    character: str
    instances: Tuple[Instance, ...]
