"""Lightweight semantic version helpers (major.minor.patch)."""

from __future__ import annotations


def parse_version(label: str) -> tuple[int, int, int]:
    parts = (label or "0.0.0").strip().lstrip("v").split(".")
    nums = [int(p) if p.isdigit() else 0 for p in parts[:3]]
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


def bump_version(label: str, part: str = "patch") -> str:
    major, minor, patch = parse_version(label)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"
