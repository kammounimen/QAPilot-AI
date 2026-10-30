from typing import Literal

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    id: str
    text: str


class Step(BaseModel):
    action: str
    expected: str


class TestCase(BaseModel):
    __test__ = False  # évite la collecte par pytest

    id: str
    requirement_id: str
    title: str
    type: Literal["nominal", "negative"]
    layer: Literal["API", "UI"]
    priority: Literal["Haute", "Moyenne", "Basse"]
    preconditions: list[str] = []
    steps: list[Step] = Field(min_length=1)


class CaseList(BaseModel):
    cases: list[TestCase] = Field(min_length=2)
class GeneratedTest(BaseModel):
    code: str = Field(min_length=20)