"""
Copyright (c) 2020 Hecong Wang

This software is released under the MIT License.
https://opensource.org/licenses/MIT
"""
from __future__ import annotations

import json
import os.path
import re
from typing import Iterable, NamedTuple, Tuple
from uuid import UUID

SAMPLE = re.compile(r"^Instance (.{36})\D+(\d+)\D+(\d+).+$")
INSTANCE = re.compile(r"^Summary\D+(\d+)\D+(\d+).+$")
EXPERIMENT = re.compile(r"^(?:Commencing|Concluding).+\((.+), (\d), (.+)\)$")


class Path(NamedTuple):
    weight: float
    content: str


class Sample(NamedTuple):
    error: float
    target: Tuple[int, ...]
    result: Tuple[float, ...]
    human_paths: Tuple[Path, ...]
    machine_paths: Tuple[Path, ...]

    @staticmethod
    def parse(content: str, outputs: str) -> Sample:
        if not (match := re.match(SAMPLE, content)):
            raise RuntimeError("content cannot be parsed as Sample")

        uuid, human_size, machine_size = match.groups()
        human_size, machine_size = int(human_size), int(machine_size)

        with open(os.path.join(outputs, f"{uuid}.json"), "r") as file:
            output = json.load(file)
            output["reasons"] = [Path._make(i) for i in output["reasons"]]

        if len(output["reasons"]) != human_size + machine_size:
            raise RuntimeError("inconsistent size description for reasons")

        return Sample(
            error=output["entropy"],
            target=tuple(int(i) for i in output["target"][1:-1].split(',')),
            result=tuple(output["result"]),
            human_paths=tuple(output["reasons"][:human_size]),
            machine_paths=tuple(output["reasons"][human_size:])
        )


class Instance(NamedTuple):
    human_size: int
    machine_size: int
    samples: Tuple[Sample, ...]

    @staticmethod
    def parse(content: Iterable[str, ...], outputs: str) -> Instance:
        *samples, instance = content

        if not (match := re.match(INSTANCE, instance)):
            raise RuntimeError("content cannot be parsed as Instance")

        human_size, machine_size = match.groups()
        human_size, machine_size = int(human_size), int(machine_size)

        return Instance(
            human_size=human_size,
            machine_size=machine_size,
            samples=tuple(Sample.parse(i, outputs) for i in samples)
        )


class Experiment(NamedTuple):
    story: UUID
    sentence: int
    character: str
    instances: Tuple[Instance, ...]

    @staticmethod
    def parse(content: Iterable[str, ...], outputs: str) -> Experiment:
        commence, *instances, conclude = content

        if not (commence_match := re.match(EXPERIMENT, commence)):
            raise RuntimeError("content cannot be parsed as Experiment")

        if not (conclude_match := re.match(EXPERIMENT, conclude)):
            raise RuntimeError("content cannot be parsed as Experiment")

        if commence_match.groups() != conclude_match.groups():
            raise RuntimeError("inconsistent commencing and concluding line")

        story, sentence, character = commence_match.groups()
        sentence = int(sentence)

        chunks, buffer = [], []

        for line in instances:
            buffer.append(line)

            if line.startswith("Summary"):
                chunks.append(buffer)
                buffer = []

        return Experiment(
            story=UUID(story),
            sentence=sentence,
            character=character,
            instances=tuple(Instance.parse(i, outputs) for i in chunks)
        )


def load_experiments(filename: str, directory: str) -> Tuple[Experiment, ...]:
    with open(filename, "r") as file:
        content = [i[37:].strip() for i in file]

    chunks, buffer = [], []

    for line in content:
        if line.startswith("Commencing"):
            buffer = []
            buffer.append(line)
        elif line.startswith("Instance") or line.startswith("Summary"):
            buffer.append(line)
        elif line.startswith("Concluding"):
            buffer.append(line)
            chunks.append(buffer)
            buffer = []

    return tuple(Experiment.parse(i, directory) for i in chunks)
