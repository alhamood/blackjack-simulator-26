"""
Unit tests for betting strategy module.
"""

import os
import json
import unittest
import tempfile

from src.betting import (
    BettingStrategy, FlatBetting, MartingaleBetting,
    ReverseMartingaleBetting, Sequence1326Betting,
    ParoliBetting, DAlembertBetting, FibonacciBetting,
    STRATEGY_REGISTRY,
)


class TestFlatBetting(unittest.TestCase):
    """Test flat betting strategy."""

    def test_always_returns_base_unit(self):
        s = FlatBetting(base_unit=5.0)
        for _ in range(10):
            self.assertEqual(s.get_bet(), 5.0)
            s.update('loss', -5.0, 5.0)
        for _ in range(10):
            self.assertEqual(s.get_bet(), 5.0)
            s.update('win', 5.0, 5.0)


class TestMartingaleBetting(unittest.TestCase):
    """Test Martingale betting strategy."""

    def test_double_on_loss(self):
        s = MartingaleBetting(base_unit=1.0, max_bet=1000.0)
        self.assertEqual(s.get_bet(), 1.0)
        s.update('loss', -1.0, 1.0)
        self.assertEqual(s.get_bet(), 2.0)
        s.update('loss', -2.0, 2.0)
        self.assertEqual(s.get_bet(), 4.0)

    def test_reset_on_win(self):
        s = MartingaleBetting(base_unit=1.0, max_bet=1000.0)
        s.update('loss', -1.0, 1.0)
        s.update('loss', -2.0, 2.0)
        self.assertEqual(s.get_bet(), 4.0)
        s.update('win', 4.0, 4.0)
        self.assertEqual(s.get_bet(), 1.0)

    def test_max_bet_cap(self):
        s = MartingaleBetting(base_unit=1.0, max_bet=8.0)
        for _ in range(10):
            s.update('loss', -s.get_bet(), s.get_bet())
        self.assertEqual(s.get_bet(), 8.0)

    def test_reset(self):
        s = MartingaleBetting(base_unit=1.0, max_bet=1000.0)
        s.update('loss', -1.0, 1.0)
        s.update('loss', -2.0, 2.0)
        s.reset()
        self.assertEqual(s.get_bet(), 1.0)


class TestReverseMartingaleBetting(unittest.TestCase):
    """Test Reverse Martingale betting strategy."""

    def test_double_on_win(self):
        s = ReverseMartingaleBetting(base_unit=1.0, max_bet=1000.0)
        self.assertEqual(s.get_bet(), 1.0)
        s.update('win', 1.0, 1.0)
        self.assertEqual(s.get_bet(), 2.0)
        s.update('win', 2.0, 2.0)
        self.assertEqual(s.get_bet(), 4.0)

    def test_reset_on_loss(self):
        s = ReverseMartingaleBetting(base_unit=1.0, max_bet=1000.0)
        s.update('win', 1.0, 1.0)
        s.update('win', 2.0, 2.0)
        s.update('loss', -4.0, 4.0)
        self.assertEqual(s.get_bet(), 1.0)


class TestSequence1326Betting(unittest.TestCase):
    """Test 1-3-2-6 betting strategy."""

    def test_sequence_on_wins(self):
        s = Sequence1326Betting(base_unit=5.0, max_bet=1000.0)
        self.assertEqual(s.get_bet(), 5.0)   # 1 * 5
        s.update('win', 5.0, 5.0)
        self.assertEqual(s.get_bet(), 15.0)  # 3 * 5
        s.update('win', 15.0, 15.0)
        self.assertEqual(s.get_bet(), 10.0)  # 2 * 5
        s.update('win', 10.0, 10.0)
        self.assertEqual(s.get_bet(), 30.0)  # 6 * 5

    def test_stays_at_end_of_sequence(self):
        s = Sequence1326Betting(base_unit=1.0, max_bet=1000.0)
        # Win 4 times to get to end
        for _ in range(4):
            s.update('win', s.get_bet(), s.get_bet())
        # Should stay at position 3 (bet=6)
        self.assertEqual(s.get_bet(), 6.0)

    def test_reset_on_loss(self):
        s = Sequence1326Betting(base_unit=1.0, max_bet=1000.0)
        s.update('win', 1.0, 1.0)
        s.update('win', 3.0, 3.0)
        self.assertEqual(s.get_bet(), 2.0)
        s.update('loss', -2.0, 2.0)
        self.assertEqual(s.get_bet(), 1.0)


class TestParoliBetting(unittest.TestCase):
    """Test Paroli betting strategy."""

    def test_double_on_win(self):
        s = ParoliBetting(base_unit=1.0, max_bet=1000.0)
        self.assertEqual(s.get_bet(), 1.0)
        s.update('win', 1.0, 1.0)
        self.assertEqual(s.get_bet(), 2.0)
        s.update('win', 2.0, 2.0)
        self.assertEqual(s.get_bet(), 4.0)

    def test_reset_after_three_wins(self):
        s = ParoliBetting(base_unit=1.0, max_bet=1000.0)
        s.update('win', 1.0, 1.0)
        s.update('win', 2.0, 2.0)
        s.update('win', 4.0, 4.0)  # 3rd win - reset
        self.assertEqual(s.get_bet(), 1.0)

    def test_reset_on_loss(self):
        s = ParoliBetting(base_unit=1.0, max_bet=1000.0)
        s.update('win', 1.0, 1.0)
        self.assertEqual(s.get_bet(), 2.0)
        s.update('loss', -2.0, 2.0)
        self.assertEqual(s.get_bet(), 1.0)


class TestDAlembertBetting(unittest.TestCase):
    """Test D'Alembert betting strategy."""

    def test_increase_on_loss(self):
        s = DAlembertBetting(base_unit=1.0, max_bet=1000.0)
        self.assertEqual(s.get_bet(), 1.0)
        s.update('loss', -1.0, 1.0)
        self.assertEqual(s.get_bet(), 2.0)
        s.update('loss', -2.0, 2.0)
        self.assertEqual(s.get_bet(), 3.0)

    def test_decrease_on_win(self):
        s = DAlembertBetting(base_unit=1.0, max_bet=1000.0)
        s.update('loss', -1.0, 1.0)
        s.update('loss', -2.0, 2.0)
        self.assertEqual(s.get_bet(), 3.0)
        s.update('win', 3.0, 3.0)
        self.assertEqual(s.get_bet(), 2.0)

    def test_floor_at_one_unit(self):
        s = DAlembertBetting(base_unit=1.0, max_bet=1000.0)
        self.assertEqual(s.get_bet(), 1.0)
        s.update('win', 1.0, 1.0)
        # Should not go below 1 unit
        self.assertEqual(s.get_bet(), 1.0)

    def test_push_no_change(self):
        s = DAlembertBetting(base_unit=1.0, max_bet=1000.0)
        s.update('loss', -1.0, 1.0)
        self.assertEqual(s.get_bet(), 2.0)
        s.update('push', 0.0, 2.0)
        self.assertEqual(s.get_bet(), 2.0)


class TestFibonacciBetting(unittest.TestCase):
    """Test Fibonacci betting strategy."""

    def test_fibonacci_on_losses(self):
        s = FibonacciBetting(base_unit=1.0, max_bet=1000.0)
        expected = [1, 1, 2, 3, 5, 8, 13]
        for exp in expected:
            self.assertEqual(s.get_bet(), float(exp))
            s.update('loss', -s.get_bet(), s.get_bet())

    def test_step_back_two_on_win(self):
        s = FibonacciBetting(base_unit=1.0, max_bet=1000.0)
        # Lose 4 times: positions 0,1,2,3 → bets 1,1,2,3 → now at position 4 (bet=5)
        for _ in range(4):
            s.update('loss', -s.get_bet(), s.get_bet())
        self.assertEqual(s.get_bet(), 5.0)  # position 4
        s.update('win', 5.0, 5.0)
        self.assertEqual(s.get_bet(), 2.0)  # position 2

    def test_win_at_start_stays_at_start(self):
        s = FibonacciBetting(base_unit=1.0, max_bet=1000.0)
        self.assertEqual(s.get_bet(), 1.0)
        s.update('win', 1.0, 1.0)
        self.assertEqual(s.get_bet(), 1.0)  # Can't go below 0


class TestFromJson(unittest.TestCase):
    """Test loading strategies from JSON config files."""

    def test_load_martingale(self):
        config = {
            "name": "Martingale",
            "type": "martingale",
            "params": {"base_unit": 5.0, "max_bet": 500.0}
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()
            s = BettingStrategy.from_json(f.name)
        os.unlink(f.name)
        self.assertIsInstance(s, MartingaleBetting)
        self.assertEqual(s.base_unit, 5.0)
        self.assertEqual(s.max_bet, 500.0)

    def test_load_unknown_type_defaults_to_flat(self):
        config = {"type": "nonexistent", "params": {}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()
            s = BettingStrategy.from_json(f.name)
        os.unlink(f.name)
        self.assertIsInstance(s, FlatBetting)


class TestStrategyRegistry(unittest.TestCase):
    """Test strategy registry completeness."""

    def test_all_types_registered(self):
        expected = ['flat', 'martingale', 'reverse_martingale', '1-3-2-6',
                     'paroli', 'dalembert', 'fibonacci']
        for key in expected:
            self.assertIn(key, STRATEGY_REGISTRY)

    def test_config_files_loadable(self):
        """All JSON config files in config/betting_strategies/ should load."""
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config', 'betting_strategies')
        if not os.path.isdir(config_dir):
            self.skipTest('Config directory not found')
        for fname in os.listdir(config_dir):
            if fname.endswith('.json'):
                path = os.path.join(config_dir, fname)
                s = BettingStrategy.from_json(path)
                self.assertIsInstance(s, BettingStrategy)
                self.assertGreater(s.get_bet(), 0)


if __name__ == '__main__':
    unittest.main()
