from dataclasses import dataclass, field
import argparse


@dataclass
class Config:
    sim_time: float = 0.05
    graphics: bool = True
    infinite: bool = False
    perf_check: bool = True
    heartbeat_time: int = 1000

    default_ct: float =  10/3 
    default_rp: float = 300

    slow_ct: float = 4
    slow_rp: float = 0.1

    blocked_ids: list[int] = field(default_factory=list)

    log: bool = False
    debugging: bool = False
    firing_node: int = 5
    length: int = 12
    max_log_lines: int = 25

    @staticmethod
    def _parse_bool(val, name):
        v = str(val).strip().lower()
        if v in ("1", "true", "t", "yes", "y", "on"):
            return True
        if v in ("0", "false", "f", "no", "n", "off"):
            return False
        raise ValueError(f"Invalid arg for {name}: '{val}'. Use true/false or 1/0")

    @classmethod
    def from_args(cls, argv=None):
        """Parse command line arguments and return a Config instance."""
        cfg = cls()

        parser = argparse.ArgumentParser(description="Run microreentry simulation")
        parser.add_argument("--graphics", type=str, default=str(cfg.graphics), help="true/false")
        parser.add_argument("--infinite", type=str, default=str(cfg.infinite), help="true/false")
        parser.add_argument("--sim_time", type=float, default=cfg.sim_time, help="time step sleep value")
        parser.add_argument("--perf_check", type=str, default=str(cfg.perf_check), help="true/false")
        parser.add_argument("--heartbeat_time", type=int, default=cfg.heartbeat_time, help="heartbeat interval")
        parser.add_argument("--length", type=int, default=cfg.length, help="sheet size")
        parser.add_argument("--firing_node", type=int, default=cfg.firing_node, help="starter node")
        parser.add_argument("--max_log_lines", type=int, default=cfg.max_log_lines)
        parser.add_argument("--log", type=str, default=str(cfg.log), help="true/false")
        parser.add_argument("--debugging", type=str, default=str(cfg.debugging), help="true/false")

        args = parser.parse_args(argv)

        cfg.graphics = cls._parse_bool(args.graphics, "graphics")
        cfg.infinite = cls._parse_bool(args.infinite, "infinite")
        cfg.sim_time = args.sim_time
        cfg.perf_check = cls._parse_bool(args.perf_check, "perf_check")
        cfg.heartbeat_time = args.heartbeat_time
        cfg.length = args.length
        cfg.firing_node = args.firing_node
        cfg.max_log_lines = args.max_log_lines
        cfg.log = cls._parse_bool(args.log, "log")
        cfg.debugging = cls._parse_bool(args.debugging, "debugging")

        return cfg

    @classmethod
    def from_monte_carlo_args(cls, argv=None):
        """Parse only the CLI args relevant to Monte Carlo runs."""
        cfg = cls()
        cfg.graphics = False
        cfg.infinite = False
        cfg.sim_time = 0
        cfg.log = False
        cfg.debugging = False

        parser = argparse.ArgumentParser(description="Run microreentry Monte Carlo simulation")
        parser.add_argument("--length", type=int, default=cfg.length, help="sheet size")
        parser.add_argument("--heartbeat_time", type=int, default=cfg.heartbeat_time, help="heartbeat interval")
        parser.add_argument("--firing_node", type=int, default=cfg.firing_node, help="starter node")
        parser.add_argument("--perf_check", type=str, default=str(cfg.perf_check), help="true/false")

        args = parser.parse_args(argv)

        cfg.length = args.length
        cfg.heartbeat_time = args.heartbeat_time
        cfg.firing_node = args.firing_node
        cfg.perf_check = cls._parse_bool(args.perf_check, "perf_check")

        return cfg
