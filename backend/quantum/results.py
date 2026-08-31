from dataclasses import dataclass

@dataclass
class SimulationResult:
    algorithm: str
    target_state: str
    shots: int
    counts: dict[str, int]

    def __post_init__(self):
        if self.shots <= 0:
            raise ValueError("shots must be greater than zero")

        if any(count < 0 for count in self.counts.values()):
            raise ValueError("measurement counts cannot be negative")

        if sum(self.counts.values()) != self.shots:
            raise ValueError("measurement counts must sum to shots")

    @property
    def probabilities(self) -> dict[str, float]:
        return {
            state: count/self.shots
            for state, count in self.counts.items()
        }

    @property
    def target_probability(self)->float:
        return self.counts.get(self.target_state, 0)/ self.shots

    @property
    def most_likely_state(self)->str:
        return max(self.counts, key=self.counts.get)