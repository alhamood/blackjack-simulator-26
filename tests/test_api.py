"""
Unit tests for web API endpoints.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from fastapi.testclient import TestClient
    from web.api import app
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipIf(not FASTAPI_AVAILABLE, "FastAPI not installed")
class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""

    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_get_defaults(self):
        """Test GET /api/defaults endpoint."""
        response = self.client.get("/api/defaults")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('game_rules', data)
        self.assertIn('shoe', data)
        self.assertIn('simulation', data)
        self.assertIn('available_strategies', data)

        # Check defaults
        self.assertEqual(data['game_rules']['dealer_hits_soft_17'], True)
        self.assertEqual(data['game_rules']['surrender_allowed'], True)
        self.assertEqual(data['game_rules']['blackjack_payout'], 1.5)
        self.assertEqual(data['shoe']['num_decks'], 6)
        self.assertEqual(data['shoe']['penetration'], 0.75)

    def test_list_strategies(self):
        """Test GET /api/strategies endpoint."""
        response = self.client.get("/api/strategies")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('strategies', data)
        self.assertIsInstance(data['strategies'], list)
        self.assertGreater(len(data['strategies']), 0)

        # Check strategy structure
        strategy = data['strategies'][0]
        self.assertIn('id', strategy)
        self.assertIn('name', strategy)
        self.assertIn('description', strategy)

    def test_get_strategy_basic(self):
        """Test GET /api/strategies/{id} for basic strategy."""
        response = self.client.get("/api/strategies/basic_strategy_h17")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('name', data)
        self.assertIn('strategy', data)

        strategy = data['strategy']
        self.assertIn('hard_totals', strategy)
        self.assertIn('soft_totals', strategy)
        self.assertIn('pairs', strategy)

    def test_get_strategy_not_found(self):
        """Test GET /api/strategies/{id} with non-existent strategy."""
        response = self.client.get("/api/strategies/nonexistent")
        self.assertEqual(response.status_code, 404)

    def test_simulate_basic(self):
        """Test POST /api/simulate with basic parameters."""
        payload = {
            "game_rules": {
                "dealer_hits_soft_17": False,
                "surrender_allowed": True,
                "double_after_split": True,
                "blackjack_payout": 1.5
            },
            "shoe": {
                "num_decks": 6,
                "penetration": 0.75,
                "infinite_shoe": False
            },
            "simulation": {
                "total_hands": 100,  # Small number for fast test
                "num_sessions": 1,
                "strategy": "basic_strategy_h17",
                "track_hands": False
            }
        }

        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('summary', data)
        self.assertIn('sessions', data)

        # Check summary structure
        summary = data['summary']
        self.assertEqual(summary['total_hands'], 100)
        self.assertIn('ev_per_hand', summary)
        self.assertIn('win_rate', summary)
        self.assertIn('win_count', summary)
        self.assertIn('loss_count', summary)
        self.assertIn('push_count', summary)

    def test_simulate_infinite_shoe(self):
        """Test POST /api/simulate with infinite shoe."""
        payload = {
            "simulation": {
                "total_hands": 100,
                "num_sessions": 1,
                "strategy": "basic_strategy_h17"
            },
            "shoe": {
                "infinite_shoe": True
            }
        }

        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('summary', data)

    def test_simulate_multi_session(self):
        """Test POST /api/simulate with multiple sessions."""
        payload = {
            "simulation": {
                "total_hands": 200,
                "num_sessions": 2,
                "strategy": "basic_strategy_h17"
            }
        }

        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('sessions', data)
        self.assertEqual(len(data['sessions']), 2)

        # Should have variance statistics
        self.assertIn('variance', data)
        self.assertIn('session_ev_mean', data['variance'])
        self.assertIn('session_ev_stdev', data['variance'])

    def test_simulate_custom_strategy(self):
        """Test POST /api/simulate with custom strategy."""
        # Create a simple custom strategy (always stand)
        custom_strategy = {
            "name": "Test Strategy",
            "strategy": {
                "hard_totals": {str(i): {dealer: "stand" for dealer in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']} for i in range(5, 22)},
                "soft_totals": {str(i): {dealer: "stand" for dealer in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']} for i in range(13, 22)},
                "pairs": {rank: {dealer: "stand" for dealer in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']} for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']}
            }
        }

        payload = {
            "simulation": {
                "total_hands": 100,
                "num_sessions": 1,
                "strategy": "custom",
                "custom_strategy": custom_strategy
            }
        }

        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn('summary', data)

    def test_simulate_invalid_strategy(self):
        """Test POST /api/simulate with invalid strategy ID."""
        payload = {
            "simulation": {
                "total_hands": 100,
                "num_sessions": 1,
                "strategy": "nonexistent_strategy"
            }
        }

        response = self.client.post("/api/simulate", json=payload)
        # Invalid strategy returns 500 (internal error when loading fails)
        self.assertIn(response.status_code, [400, 500])

    def test_simulate_validation_min_hands(self):
        """Test validation for minimum hands."""
        payload = {
            "simulation": {
                "total_hands": 50,  # Below minimum of 100
                "num_sessions": 1,
                "strategy": "basic_strategy_h17"
            }
        }

        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_simulate_validation_max_hands(self):
        """Test validation for maximum hands (limit is 100M)."""
        payload = {
            "simulation": {
                "total_hands": 200_000_000,  # Above maximum of 100M
                "num_sessions": 1,
                "strategy": "basic_strategy_h17"
            }
        }

        response = self.client.post("/api/simulate", json=payload)
        self.assertEqual(response.status_code, 422)  # Validation error


if __name__ == '__main__':
    unittest.main()
