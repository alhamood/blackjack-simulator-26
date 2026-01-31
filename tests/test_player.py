"""
Unit tests for player strategy module.
"""

import unittest
from src.player import Strategy
from src.hand import Hand
from src.cards import Card
from src.game import PlayerAction


class TestStrategy(unittest.TestCase):
    """Test cases for Strategy class."""

    def setUp(self):
        """Set up test fixtures."""
        # Load basic strategy
        self.basic_strategy = Strategy('config/strategies/basic_strategy_h17.json')
        # Load never bust strategy
        self.never_bust = Strategy('config/strategies/never_bust.json')

    def test_load_basic_strategy(self):
        """Test loading basic strategy from JSON."""
        self.assertEqual(self.basic_strategy.name, "Basic Strategy (H17, Surrender)")
        self.assertIn('hard_totals', self.basic_strategy.__dict__)
        self.assertIn('soft_totals', self.basic_strategy.__dict__)
        self.assertIn('pairs', self.basic_strategy.__dict__)

    def test_load_never_bust_strategy(self):
        """Test loading never bust strategy."""
        self.assertEqual(self.never_bust.name, "Never Bust (Toy Strategy)")

    def test_hard_total_hit(self):
        """Test hitting on hard totals."""
        # Hard 8 vs dealer 5 should double (or hit if can't double)
        hand = Hand()
        hand.add_card(Card('5', '♠'))
        hand.add_card(Card('3', '♥'))
        dealer_upcard = Card('5', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_double=False)
        self.assertEqual(action, PlayerAction.HIT)

    def test_hard_total_stand(self):
        """Test standing on hard totals."""
        # Hard 17 vs dealer 10 should stand
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('7', '♥'))
        dealer_upcard = Card('10', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard)
        self.assertEqual(action, PlayerAction.STAND)

    def test_hard_total_double(self):
        """Test doubling on hard totals."""
        # Hard 11 vs dealer 6 should double
        hand = Hand()
        hand.add_card(Card('6', '♠'))
        hand.add_card(Card('5', '♥'))
        dealer_upcard = Card('6', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_double=True)
        self.assertEqual(action, PlayerAction.DOUBLE)

    def test_double_else_hit(self):
        """Test double_else_hit fallback."""
        # Hard 10 vs dealer 5 should double, or hit if can't
        hand = Hand()
        hand.add_card(Card('7', '♠'))
        hand.add_card(Card('3', '♥'))
        dealer_upcard = Card('5', '♦')

        # Can double
        action = self.basic_strategy.get_action(hand, dealer_upcard, can_double=True)
        self.assertEqual(action, PlayerAction.DOUBLE)

        # Can't double (simulating a 2-card hand where doubling is not allowed)
        action = self.basic_strategy.get_action(hand, dealer_upcard, can_double=False)
        self.assertEqual(action, PlayerAction.HIT)

    def test_soft_total_hit(self):
        """Test hitting on soft totals."""
        # Soft 13 (A,2) vs dealer 2 should hit
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('2', '♥'))
        dealer_upcard = Card('2', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard)
        self.assertEqual(action, PlayerAction.HIT)

    def test_soft_total_stand(self):
        """Test standing on soft totals."""
        # Soft 19 (A,8) vs dealer 6 should stand
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('8', '♥'))
        dealer_upcard = Card('6', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard)
        self.assertEqual(action, PlayerAction.STAND)

    def test_soft_total_double(self):
        """Test doubling on soft totals."""
        # Soft 17 (A,6) vs dealer 6 should double
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('6', '♥'))
        dealer_upcard = Card('6', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_double=True)
        self.assertEqual(action, PlayerAction.DOUBLE)

    def test_soft_18_hit_vs_9(self):
        """Test soft 18 hits against dealer 9."""
        # Soft 18 (A,7) vs dealer 9 should hit
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('7', '♥'))
        dealer_upcard = Card('9', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard)
        self.assertEqual(action, PlayerAction.HIT)

    def test_surrender(self):
        """Test surrendering."""
        # Hard 16 vs dealer 10 should surrender
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('6', '♥'))
        dealer_upcard = Card('10', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_surrender=True)
        self.assertEqual(action, PlayerAction.SURRENDER)

    def test_surrender_not_allowed(self):
        """Test surrender fallback when not allowed."""
        # Hard 16 vs dealer 10 should surrender, or hit if can't
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('6', '♥'))
        dealer_upcard = Card('10', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_surrender=False)
        self.assertEqual(action, PlayerAction.HIT)

    def test_pair_split(self):
        """Test splitting pairs."""
        # Pair of 8s vs dealer 5 should split
        hand = Hand()
        hand.add_card(Card('8', '♠'))
        hand.add_card(Card('8', '♥'))
        dealer_upcard = Card('5', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_split=True)
        self.assertEqual(action, PlayerAction.SPLIT)

    def test_pair_aces_split(self):
        """Test splitting aces."""
        # Pair of aces should always split
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('A', '♥'))
        dealer_upcard = Card('10', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_split=True)
        self.assertEqual(action, PlayerAction.SPLIT)

    def test_pair_tens_stand(self):
        """Test not splitting 10s."""
        # Pair of 10s should stand (not split)
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('Q', '♥'))
        dealer_upcard = Card('5', '♦')

        action = self.basic_strategy.get_action(hand, dealer_upcard, can_split=True)
        self.assertEqual(action, PlayerAction.STAND)

    def test_pair_8s_surrender_vs_ace(self):
        """Test pair of 8s surrendering vs ace."""
        # Pair of 8s vs dealer ace: surrender if allowed, else split
        hand = Hand()
        hand.add_card(Card('8', '♠'))
        hand.add_card(Card('8', '♥'))
        dealer_upcard = Card('A', '♦')

        # Can surrender
        action = self.basic_strategy.get_action(
            hand, dealer_upcard, can_split=True, can_surrender=True
        )
        self.assertEqual(action, PlayerAction.SURRENDER)

        # Can't surrender, should split
        action = self.basic_strategy.get_action(
            hand, dealer_upcard, can_split=True, can_surrender=False
        )
        self.assertEqual(action, PlayerAction.SPLIT)

    def test_dealer_upcard_normalization(self):
        """Test that face cards are treated as 10."""
        # Hard 16 vs dealer K should surrender (same as vs 10)
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('6', '♥'))

        dealer_10 = Card('10', '♦')
        dealer_j = Card('J', '♦')
        dealer_q = Card('Q', '♦')
        dealer_k = Card('K', '♦')

        action_10 = self.basic_strategy.get_action(hand, dealer_10, can_surrender=True)
        action_j = self.basic_strategy.get_action(hand, dealer_j, can_surrender=True)
        action_q = self.basic_strategy.get_action(hand, dealer_q, can_surrender=True)
        action_k = self.basic_strategy.get_action(hand, dealer_k, can_surrender=True)

        # All should surrender
        self.assertEqual(action_10, PlayerAction.SURRENDER)
        self.assertEqual(action_j, PlayerAction.SURRENDER)
        self.assertEqual(action_q, PlayerAction.SURRENDER)
        self.assertEqual(action_k, PlayerAction.SURRENDER)

    def test_never_bust_strategy(self):
        """Test never bust strategy behavior."""
        # Hard 12 should stand (never bust strategy)
        hand = Hand()
        hand.add_card(Card('7', '♠'))
        hand.add_card(Card('5', '♥'))
        dealer_upcard = Card('10', '♦')

        action = self.never_bust.get_action(hand, dealer_upcard)
        self.assertEqual(action, PlayerAction.STAND)

        # Hard 11 should hit (won't bust)
        hand2 = Hand()
        hand2.add_card(Card('6', '♠'))
        hand2.add_card(Card('5', '♥'))

        action2 = self.never_bust.get_action(hand2, dealer_upcard)
        self.assertEqual(action2, PlayerAction.HIT)

    def test_strategy_string_representation(self):
        """Test strategy string representations."""
        self.assertEqual(str(self.basic_strategy), "Basic Strategy (H17, Surrender)")
        self.assertIn("Basic Strategy", repr(self.basic_strategy))


if __name__ == '__main__':
    unittest.main()
