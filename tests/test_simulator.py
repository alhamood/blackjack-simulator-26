"""
Unit tests for simulator module.
"""

import unittest
from src.simulator import Simulator, SessionResult, SimulationResult
from src.game import GameRules, PlayerAction
from src.hand import Hand
from src.cards import Card


class TestSessionResult(unittest.TestCase):
    """Test cases for SessionResult class."""

    def test_session_result_creation(self):
        """Test creating a session result."""
        session = SessionResult()
        self.assertEqual(session.hands_played, 0)
        self.assertEqual(session.total_payout, 0.0)
        self.assertEqual(session.win_count, 0)

    def test_ev_per_hand(self):
        """Test EV calculation."""
        session = SessionResult(hands_played=100, total_payout=-5.0)
        self.assertEqual(session.ev_per_hand, -0.05)

    def test_ev_per_hand_zero_hands(self):
        """Test EV with zero hands."""
        session = SessionResult()
        self.assertEqual(session.ev_per_hand, 0.0)

    def test_win_rate(self):
        """Test win rate calculation."""
        session = SessionResult(win_count=45, loss_count=55, push_count=10)
        self.assertEqual(session.win_rate, 0.45)

    def test_win_rate_no_decided_hands(self):
        """Test win rate with only pushes."""
        session = SessionResult(push_count=100)
        self.assertEqual(session.win_rate, 0.0)


class TestSimulationResult(unittest.TestCase):
    """Test cases for SimulationResult class."""

    def test_simulation_result_creation(self):
        """Test creating a simulation result."""
        result = SimulationResult()
        self.assertEqual(result.total_hands, 0)
        self.assertEqual(result.total_payout, 0.0)
        self.assertEqual(len(result.sessions), 0)

    def test_ev_per_hand(self):
        """Test overall EV calculation."""
        result = SimulationResult(total_hands=1000, total_payout=-50.0)
        self.assertEqual(result.ev_per_hand, -0.05)

    def test_win_rate(self):
        """Test overall win rate."""
        result = SimulationResult(win_count=450, loss_count=550, push_count=100)
        self.assertEqual(result.win_rate, 0.45)

    def test_session_statistics(self):
        """Test session statistics calculation."""
        # Create sessions with different EVs
        session1 = SessionResult(hands_played=100, total_payout=-5.0)  # EV = -0.05
        session2 = SessionResult(hands_played=100, total_payout=-3.0)  # EV = -0.03
        session3 = SessionResult(hands_played=100, total_payout=-7.0)  # EV = -0.07

        result = SimulationResult(sessions=[session1, session2, session3])

        # Mean should be -0.05
        self.assertAlmostEqual(result.session_ev_mean, -0.05)

        # Stdev should be positive
        self.assertGreater(result.session_ev_stdev, 0.0)

    def test_session_statistics_single_session(self):
        """Test session statistics with single session."""
        session = SessionResult(hands_played=100, total_payout=-5.0)
        result = SimulationResult(sessions=[session])

        # Mean should equal session EV
        self.assertEqual(result.session_ev_mean, -0.05)

        # Stdev should be 0 (only 1 session)
        self.assertEqual(result.session_ev_stdev, 0.0)

    def test_summary_string(self):
        """Test summary generation."""
        result = SimulationResult(
            total_hands=1000,
            total_payout=-50.0,
            win_count=400,
            loss_count=500,
            push_count=100,
            blackjack_count=50,
            bust_count=150
        )

        summary = result.summary()
        self.assertIn("1,000", summary)  # Total hands formatted
        self.assertIn("-50.00", summary)  # Total payout
        self.assertIn("Wins:", summary)
        self.assertIn("Losses:", summary)


class TestSimulator(unittest.TestCase):
    """Test cases for Simulator class."""

    def test_simulator_creation(self):
        """Test creating a simulator."""
        sim = Simulator()
        self.assertIsNotNone(sim.rules)
        self.assertEqual(sim.num_decks, 6)
        self.assertEqual(sim.penetration, 0.75)
        self.assertFalse(sim.infinite_shoe)

    def test_simulator_custom_rules(self):
        """Test simulator with custom rules."""
        rules = GameRules(dealer_hits_soft_17=True, blackjack_payout=1.2)
        sim = Simulator(rules=rules, num_decks=8, infinite_shoe=True)

        self.assertTrue(sim.rules.dealer_hits_soft_17)
        self.assertEqual(sim.rules.blackjack_payout, 1.2)
        self.assertEqual(sim.num_decks, 8)
        self.assertTrue(sim.infinite_shoe)

    def test_run_session_basic(self):
        """Test running a basic session."""
        sim = Simulator(infinite_shoe=True)

        # Simple strategy: stand on everything
        def always_stand(player_hand, dealer_upcard):
            return PlayerAction.STAND

        session = sim.run_session(100, always_stand)

        self.assertEqual(session.hands_played, 100)
        # Should have some wins, losses, and pushes
        total_outcomes = session.win_count + session.loss_count + session.push_count
        self.assertEqual(total_outcomes, 100)

    def test_run_session_hit_strategy(self):
        """Test session with a hit-until-17 strategy."""
        sim = Simulator(infinite_shoe=True)

        def hit_to_17(player_hand, dealer_upcard):
            if player_hand.value() < 17:
                return PlayerAction.HIT
            return PlayerAction.STAND

        session = sim.run_session(100, hit_to_17)

        self.assertEqual(session.hands_played, 100)
        # This strategy should produce some busts
        self.assertGreater(session.bust_count, 0)

    def test_run_session_tracks_blackjacks(self):
        """Test that sessions track blackjacks."""
        sim = Simulator(infinite_shoe=True)

        def always_stand(player_hand, dealer_upcard):
            return PlayerAction.STAND

        # Run enough hands to likely get a blackjack
        session = sim.run_session(1000, always_stand)

        # Should get some blackjacks over 1000 hands
        self.assertGreater(session.blackjack_count, 0)

    def test_run_session_tracks_doubles(self):
        """Test that sessions track doubles."""
        sim = Simulator(infinite_shoe=True)

        def always_double(player_hand, dealer_upcard):
            if len(player_hand) == 2:
                return PlayerAction.DOUBLE
            return PlayerAction.STAND

        session = sim.run_session(100, always_double)

        # Most hands should be doubled (some will be blackjacks)
        self.assertGreater(session.double_count, 50)

    def test_run_session_tracks_surrenders(self):
        """Test that sessions track surrenders."""
        rules = GameRules(surrender_allowed=True)
        sim = Simulator(rules=rules, infinite_shoe=True)

        def always_surrender(player_hand, dealer_upcard):
            if len(player_hand) == 2:
                return PlayerAction.SURRENDER
            return PlayerAction.STAND

        session = sim.run_session(100, always_surrender)

        # Most hands should be surrendered (some will be blackjacks)
        self.assertGreater(session.surrender_count, 50)

    def test_run_simulation_single_session(self):
        """Test single-session simulation."""
        sim = Simulator(infinite_shoe=True)

        def always_stand(player_hand, dealer_upcard):
            return PlayerAction.STAND

        result = sim.run_simulation(1000, always_stand, num_sessions=1)

        self.assertEqual(result.total_hands, 1000)
        self.assertEqual(len(result.sessions), 1)
        # EV should be negative (house edge)
        self.assertLess(result.ev_per_hand, 0.0)

    def test_run_simulation_multiple_sessions(self):
        """Test multi-session simulation."""
        sim = Simulator(infinite_shoe=True)

        def always_stand(player_hand, dealer_upcard):
            return PlayerAction.STAND

        result = sim.run_simulation(1000, always_stand, num_sessions=10)

        self.assertEqual(result.total_hands, 1000)
        self.assertEqual(len(result.sessions), 10)

        # Each session should have ~100 hands
        for session in result.sessions:
            self.assertEqual(session.hands_played, 100)

    def test_run_simulation_variance(self):
        """Test that multi-session captures variance."""
        sim = Simulator(infinite_shoe=True)

        def always_stand(player_hand, dealer_upcard):
            return PlayerAction.STAND

        # Run 100 sessions of 100 hands each
        result = sim.run_simulation(10000, always_stand, num_sessions=100)

        # Should have variance across sessions
        self.assertGreater(result.session_ev_stdev, 0.0)

        # Mean should be close to overall EV
        self.assertAlmostEqual(
            result.session_ev_mean,
            result.ev_per_hand,
            places=4
        )

    def test_compare_strategies(self):
        """Test strategy comparison."""
        sim = Simulator(infinite_shoe=True)

        def always_stand(player_hand, dealer_upcard):
            return PlayerAction.STAND

        def hit_to_17(player_hand, dealer_upcard):
            if player_hand.value() < 17:
                return PlayerAction.HIT
            return PlayerAction.STAND

        results = sim.compare_strategies(
            strategy_funcs=[always_stand, hit_to_17],
            strategy_names=['Always Stand', 'Hit to 17'],
            hands_per_strategy=1000
        )

        self.assertEqual(len(results), 2)
        self.assertIn('Always Stand', results)
        self.assertIn('Hit to 17', results)

        # Both should have played 1000 hands
        self.assertEqual(results['Always Stand'].total_hands, 1000)
        self.assertEqual(results['Hit to 17'].total_hands, 1000)

        # Hit to 17 should perform better than always stand
        # (though with only 1000 hands, this might not always be true due to variance)
        # So we'll just check they have different EVs
        self.assertNotEqual(
            results['Always Stand'].ev_per_hand,
            results['Hit to 17'].ev_per_hand
        )


if __name__ == '__main__':
    unittest.main()
