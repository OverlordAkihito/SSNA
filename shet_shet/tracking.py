"""Small, dependency-free multi-face association and landmark smoothing."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from typing import Iterable

Point = tuple[float, float]
Shape = tuple[Point, ...]


@dataclass(frozen=True)
class FaceShape:
    points: Shape
    _center: Point = field(init=False, repr=False, compare=False)
    _bounds: tuple[float, float, float, float] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.points:
            object.__setattr__(self, "_center", (0.0, 0.0))
            object.__setattr__(self, "_bounds", (0.0, 0.0, 0.0, 0.0))
            return
        xs = [point[0] for point in self.points]
        ys = [point[1] for point in self.points]
        object.__setattr__(self, "_center", (sum(xs) / len(xs), sum(ys) / len(ys)))
        object.__setattr__(self, "_bounds", (min(xs), min(ys), max(xs), max(ys)))

    @property
    def center(self) -> Point:
        return self._center

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return self._bounds


@dataclass
class FaceTrack:
    track_id: int
    shape: FaceShape
    misses: int = 0


def _distance(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def _intersection_over_union(a: FaceShape, b: FaceShape) -> float:
    ax1, ay1, ax2, ay2 = a.bounds
    bx1, by1, bx2, by2 = b.bounds
    width = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    height = max(0.0, min(ay2, by2) - max(ay1, by1))
    intersection = width * height
    area_a = max(1e-6, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1e-6, (bx2 - bx1) * (by2 - by1))
    return intersection / (area_a + area_b - intersection)


def _blend(old: FaceShape, new: FaceShape, alpha: float) -> FaceShape:
    if len(old.points) != len(new.points):
        return new
    return FaceShape(tuple(
        (x0 + (x1 - x0) * alpha, y0 + (y1 - y0) * alpha)
        for (x0, y0), (x1, y1) in zip(old.points, new.points)
    ))


class FaceTracker:
    """Greedy nearest-face association with EMA smoothing and short holdover."""

    def __init__(self, max_missed_frames: int = 3, match_distance: float = 0.24):
        self.max_missed_frames = max_missed_frames
        self.match_distance = match_distance
        self._tracks: list[FaceTrack] = []
        self._next_id = 1

    @property
    def tracks(self) -> tuple[FaceTrack, ...]:
        return tuple(self._tracks)

    def update(self, detections: Iterable[FaceShape], smoothing: float = 0.35) -> tuple[FaceTrack, ...]:
        shapes = [shape for shape in detections if len(shape.points) >= 3]
        alpha = min(1.0, max(0.05, smoothing))
        candidates: list[tuple[float, int, int]] = []
        for new_index, shape in enumerate(shapes):
            for track_index, track in enumerate(self._tracks):
                distance = _distance(shape.center, track.shape.center)
                overlap = _intersection_over_union(shape, track.shape)
                if distance <= self.match_distance or overlap >= 0.05:
                    # Favor spatially close matches, while allowing scale changes.
                    candidates.append((distance - overlap * 0.08, new_index, track_index))

        assigned_new: set[int] = set()
        assigned_tracks: set[int] = set()
        for _, new_index, track_index in sorted(candidates):
            if new_index in assigned_new or track_index in assigned_tracks:
                continue
            track = self._tracks[track_index]
            track.shape = _blend(track.shape, shapes[new_index], alpha)
            track.misses = 0
            assigned_new.add(new_index)
            assigned_tracks.add(track_index)

        for track_index, track in enumerate(self._tracks):
            if track_index not in assigned_tracks:
                track.misses += 1

        self._tracks = [t for t in self._tracks if t.misses <= self.max_missed_frames]
        for index, shape in enumerate(shapes):
            if index not in assigned_new:
                self._tracks.append(FaceTrack(self._next_id, shape))
                self._next_id += 1
        return self.tracks
