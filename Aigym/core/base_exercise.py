import math 
import time
from abc import ABC, abstractmethod


class BaseExercise(ABC):
    # A real rep can never physically complete faster than this. A single
    # noisy/occluded MediaPipe frame right at a threshold boundary can
    # otherwise register a spurious extra state-flip and double-count one
    # physical rep, which silently pushes `reps` past `reps_per_set * target_sets`
    # and ends the workout early. This gate filters that out.
    MIN_REP_INTERVAL_SEC = 0.4

    def __init__(self):
        self.reps = 0
        self.stage = None
        self._last_rep_time = 0.0

    def _count_rep(self):
        now = time.time()

        if now - self._last_rep_time >= self.MIN_REP_INTERVAL_SEC:
            self.reps += 1
            self._last_rep_time = now

    def calculate_angle(self, a, b, c):
        ax, ay = a[0] - b[0], a[1] - b[1]
        cx, cy = c[0] - b[0], c[1] - b[1]

        dot = ax * cx + ay * cy

        mag_a = math.sqrt(ax ** 2 + ay ** 2)
        mag_c = math.sqrt(cx ** 2 + cy ** 2)

        if mag_a * mag_c == 0:
            return 0.0

        cos_angle = max(-1.0, min(1.0, dot / (mag_a * mag_c)))

        return math.degrees(math.acos(cos_angle))

    def get_point(self, landmarks, idx):
        p = landmarks[idx]

        return (p.x, p.y)

    @abstractmethod
    def process(self, landmarks):
        pass

    @abstractmethod
    def reset(self):
        pass