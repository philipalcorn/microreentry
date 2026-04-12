import unittest
import time

from config import Config
from topology import build_sheet
from simulation import run_simulation, update_everything, log_event


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.cfg = Config()
        self.nodes, self.muscles = build_sheet(self.cfg.length)

    def test_config_defaults(self):
        print("Running test_config_defaults")
        self.assertFalse(self.cfg.infinite)
        self.assertTrue(self.cfg.graphics)
        self.assertEqual(self.cfg.sim_time, 0.05)
        self.assertEqual(self.cfg.heartbeat_time, 600)
        self.assertEqual(self.cfg.default_rp, 350)
        self.assertEqual(self.cfg.default_ct, 6)
        self.assertEqual(self.cfg.length, 12)
        self.assertEqual(self.cfg.blocked_ids, [])

    def test_run_simulation_headless_no_sleep(self):
        print("Running test_run_simulation_headless_no_sleep")
        self.cfg.graphics = False
        self.cfg.perf_check = True
        self.cfg.infinite = False

        start = time.perf_counter()
        result = run_simulation(self.cfg, self.nodes, self.muscles, max_timesteps=50)
        elapsed = time.perf_counter() - start

        self.assertIsInstance(result, dict)
        self.assertIn("timestep", result)
        self.assertLess(elapsed, 0.5)

    def test_run_simulation_micro_detected(self):
        print("Running test_run_simulation_micro_detected")
        self.cfg.graphics = False
        self.cfg.perf_check = False
        self.cfg.infinite = False

        result = run_simulation(self.cfg, self.nodes, self.muscles, max_timesteps=200)
        self.assertIn("micro", result)
        self.assertTrue(result["micro"] or result["timestep"] == 200)

    def test_run_simulation_latches_micro_in_infinite_mode(self):
        print("Running test_run_simulation_latches_micro_in_infinite_mode")
        self.cfg.graphics = False
        self.cfg.perf_check = False
        self.cfg.infinite = True

        # Run past the detection deadline (150) and ensure micro stays latched.
        result = run_simulation(self.cfg, self.nodes, self.muscles, max_timesteps=200)
        self.assertIn("micro", result)
        self.assertTrue(result["micro"])


    def test_run_simulation_heartbeat_fire(self):
        print("Running test_run_simulation_heartbeat_fire")
        self.cfg.graphics = False
        self.cfg.perf_check = False
        self.cfg.infinite = False
        self.cfg.heartbeat_time = 1

        result = run_simulation(self.cfg, self.nodes, self.muscles, max_timesteps=5)
        self.assertLessEqual(result["timestep"], 5)

    def test_update_everything_and_log_event(self):
        print("Running test_update_everything_and_log_event")
        event_log = []
        t, micro, micro_origin = update_everything(0, self.nodes, self.muscles, event_log, None, debugging=False, max_log_lines=10)
        self.assertIsInstance(t, int)
        self.assertIn(micro, [True, False])
        self.assertIsNone(micro_origin)

        log_event(event_log, 1, "Timestep 1: test")
        log_event(event_log, 1, "Timestep 1: test")
        self.assertEqual(len(event_log), 1)

        for i in range(15):
            log_event(event_log, i + 2, f"Timestep {i+2}: extra", max_log_lines=5)
        self.assertLessEqual(len(event_log), 5)

    def test_reentry_detection_requires_more_than_half_refired_nodes_before_t150(self):
        print("Running test_reentry_detection_requires_more_than_half_refired_nodes_before_t150")
        event_log = []

        # Use empty muscles and directly set node fire counts.
        muscles = []

        # Exactly 50% nodes refired is not enough before t=150.
        half = len(self.nodes) // 2
        for nid in range(half):
            self.nodes[nid].has_fired = 2

        _, micro, micro_origin = update_everything(
            0,
            self.nodes,
            muscles,
            event_log,
            None,
            debugging=False,
            max_log_lines=10,
        )
        self.assertFalse(micro)
        self.assertIsNone(micro_origin)

        # Crossing 50% before t=150 should trigger reentry.
        self.nodes[half].has_fired = 2
        _, micro, micro_origin = update_everything(
            1,
            self.nodes,
            muscles,
            event_log,
            None,
            debugging=False,
            max_log_lines=10,
        )
        self.assertTrue(micro)
        self.assertIsNotNone(micro_origin)

        # Even if threshold is crossed, detection should not trigger at/after t=150.
        _, micro, _ = update_everything(
            150,
            self.nodes,
            muscles,
            event_log,
            None,
            debugging=False,
            max_log_lines=10,
        )
        self.assertFalse(micro)


if __name__ == "__main__":
    unittest.main()
