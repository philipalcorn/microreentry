from dataclasses import dataclass, field
@dataclass
class Config:
    sim_time: float = 0.05
    graphics: bool = True
    infinite: bool = False
    perf_check: bool = True
    heartbeat_time: int = 600

    default_ct: int = 6
    default_rp: int = 350

    slow_ct: float = 4
    slow_rp: float = 0.1

    blocked_ids: list[int] = field(default_factory=lambda: [51, 63, 64, 199, 211, 212])

    log: bool = False
    debugging: bool = False
    firing_node: int = 5
    l: int = 12
    max_log_lines: int = 25
