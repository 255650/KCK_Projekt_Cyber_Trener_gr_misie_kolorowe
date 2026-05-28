from typing import Optional

class SessionAnalyzer:
    def __init__(self, side_weight: float = 0.75, min_tech_to_count: int = 60,
                 min_down_frames: int = 4, min_up_frames: int = 2):
        self.side_weight = side_weight
        self.min_tech_to_count = min_tech_to_count
        self.min_down_frames = min_down_frames
        self.min_up_frames = min_up_frames
        self.reset_session()

    def reset_session(self):
        self.rep_count = 0
        self.rep_active = False
        self.good_frames = 0
        self.total_frames = 0
        self.down_frames = 0
        self.up_frames = 0
        # snapshoty ostatniej klatki (używane do wyświetlania techniki)
        self.last_side_snapshot = (0, 1)
        self.last_front_snapshot = (0, 1)

    def update_side(self, score: int, max_score: int, extra: dict):
        """
        score/max_score to ocena z ostatniej klatki (0..max_score).
        extra może zawierać: 'phase' (UP/DOWN), 'start_rep' (bool)
        """
        # zapisz snapshot ostatniej klatki (używany do combined tech)
        self.last_side_snapshot = (score, max_score)

        phase = extra.get("phase") if extra else None

        if phase == "DOWN":
            self.down_frames += 1
            self.up_frames = 0
        elif phase == "UP":
            self.up_frames += 1
            self.down_frames = 0
        else:
            self.down_frames = 0
            self.up_frames = 0

        if self.down_frames >= self.min_down_frames:
            self.rep_active = True

        if self.rep_active:
            # akumulacja oparta na score/max_score (tak jak wcześniej)
            self.good_frames += score
            self.total_frames += max_score

        if self.rep_active and self.up_frames >= self.min_up_frames:
            technique_percent = int((self.good_frames / self.total_frames) * 100) if self.total_frames > 0 else 0
            if technique_percent >= self.min_tech_to_count:
                self.rep_count += 1
            # reset akumulacji
            self.good_frames = 0
            self.total_frames = 0
            self.rep_active = False
            self.down_frames = 0
            self.up_frames = 0

    def update_front(self, score: int, max_score: int):
        # snapshot ostatniej klatki frontowej
        self.last_front_snapshot = (score, max_score)

    def get_combined_tech(self, side_weight: Optional[float] = None) -> int:
        if side_weight is None:
            side_weight = self.side_weight
        side_score, side_max = self.last_side_snapshot
        front_score, front_max = self.last_front_snapshot
        side_tech = int((side_score / side_max) * 100) if side_max > 0 else 0
        front_tech = int((front_score / front_max) * 100) if front_max > 0 else 0
        combined = int(side_weight * side_tech + (1 - side_weight) * front_tech)
        return combined

    def get_rep_count(self) -> int:
        return self.rep_count

# Singleton
_SESSION = SessionAnalyzer()

def reset_session():
    _SESSION.reset_session()

def update_side(score: int, max_score: int, extra: dict):
    _SESSION.update_side(score, max_score, extra)

def update_front(score: int, max_score: int):
    _SESSION.update_front(score, max_score)

def get_combined_tech() -> int:
    return _SESSION.get_combined_tech()

def get_rep_count() -> int:
    return _SESSION.get_rep_count()
