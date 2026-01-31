"""
Unit tests for hand module.
"""

import unittest
from src.cards import Card
from src.hand import Hand


class TestHand(unittest.TestCase):
    """Test cases for Hand class."""

    def test_empty_hand(self):
        """Test creating an empty hand."""
        hand = Hand()
        self.assertEqual(len(hand), 0)
        self.assertEqual(hand.value(), 0)
        self.assertFalse(hand.is_soft())
        self.assertFalse(hand.is_bust())
        self.assertFalse(hand.is_blackjack())
        self.assertFalse(hand.is_pair())

    def test_add_card(self):
        """Test adding cards to a hand."""
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        self.assertEqual(len(hand), 1)
        hand.add_card(Card('K', '♥'))
        self.assertEqual(len(hand), 2)

    def test_simple_values(self):
        """Test hand value calculation for simple hands."""
        hand = Hand()
        hand.add_card(Card('5', '♠'))
        hand.add_card(Card('7', '♥'))
        self.assertEqual(hand.value(), 12)

    def test_face_card_values(self):
        """Test that face cards are worth 10."""
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('Q', '♥'))
        self.assertEqual(hand.value(), 20)

        hand2 = Hand()
        hand2.add_card(Card('J', '♠'))
        hand2.add_card(Card('10', '♥'))
        self.assertEqual(hand2.value(), 20)

    def test_ace_as_eleven(self):
        """Test ace counted as 11 when it doesn't bust."""
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('7', '♥'))
        self.assertEqual(hand.value(), 18)  # A=11 + 7 = 18
        self.assertTrue(hand.is_soft())

    def test_ace_as_one(self):
        """Test ace counted as 1 when 11 would bust."""
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('K', '♥'))
        hand.add_card(Card('9', '♦'))
        self.assertEqual(hand.value(), 20)  # A=1 + K=10 + 9 = 20
        self.assertFalse(hand.is_soft())

    def test_multiple_aces(self):
        """Test handling multiple aces in a hand."""
        # Two aces: one as 11, one as 1
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('A', '♥'))
        self.assertEqual(hand.value(), 12)  # 11 + 1 = 12
        self.assertTrue(hand.is_soft())

        # Three aces: one as 11, two as 1
        hand2 = Hand()
        hand2.add_card(Card('A', '♠'))
        hand2.add_card(Card('A', '♥'))
        hand2.add_card(Card('A', '♦'))
        self.assertEqual(hand2.value(), 13)  # 11 + 1 + 1 = 13
        self.assertTrue(hand2.is_soft())

        # Four aces: one as 11, three as 1
        hand3 = Hand()
        hand3.add_card(Card('A', '♠'))
        hand3.add_card(Card('A', '♥'))
        hand3.add_card(Card('A', '♦'))
        hand3.add_card(Card('A', '♣'))
        self.assertEqual(hand3.value(), 14)  # 11 + 1 + 1 + 1 = 14
        self.assertTrue(hand3.is_soft())

    def test_soft_hand_transitions(self):
        """Test soft hand becoming hard when adding cards."""
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('5', '♥'))
        self.assertEqual(hand.value(), 16)  # A=11 + 5 = 16
        self.assertTrue(hand.is_soft())

        # Add another card that forces ace to be 1
        hand.add_card(Card('8', '♦'))
        self.assertEqual(hand.value(), 14)  # A=1 + 5 + 8 = 14
        self.assertFalse(hand.is_soft())

    def test_blackjack(self):
        """Test blackjack detection (21 in 2 cards)."""
        # Ace + 10-value card = blackjack
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('K', '♥'))
        self.assertTrue(hand.is_blackjack())
        self.assertEqual(hand.value(), 21)

        # Ace + 10 = blackjack
        hand2 = Hand()
        hand2.add_card(Card('A', '♠'))
        hand2.add_card(Card('10', '♥'))
        self.assertTrue(hand2.is_blackjack())

        # 21 in 3 cards is NOT blackjack
        hand3 = Hand()
        hand3.add_card(Card('7', '♠'))
        hand3.add_card(Card('7', '♥'))
        hand3.add_card(Card('7', '♦'))
        self.assertFalse(hand3.is_blackjack())
        self.assertEqual(hand3.value(), 21)

    def test_bust(self):
        """Test bust detection (value > 21)."""
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('Q', '♥'))
        hand.add_card(Card('5', '♦'))
        self.assertTrue(hand.is_bust())
        self.assertEqual(hand.value(), 25)

    def test_not_bust_with_ace(self):
        """Test that ace adjustment prevents bust when possible."""
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('K', '♥'))
        hand.add_card(Card('5', '♦'))
        self.assertFalse(hand.is_bust())
        self.assertEqual(hand.value(), 16)  # A=1 + K=10 + 5 = 16

    def test_pair_detection(self):
        """Test pair detection for splitting."""
        # Same rank = pair
        hand = Hand()
        hand.add_card(Card('8', '♠'))
        hand.add_card(Card('8', '♥'))
        self.assertTrue(hand.is_pair())
        self.assertTrue(hand.can_split())

        # Different ranks = not pair
        hand2 = Hand()
        hand2.add_card(Card('8', '♠'))
        hand2.add_card(Card('9', '♥'))
        self.assertFalse(hand2.is_pair())

        # Face cards of different types but same value = pair
        hand3 = Hand()
        hand3.add_card(Card('K', '♠'))
        hand3.add_card(Card('Q', '♥'))
        self.assertFalse(hand3.is_pair())  # Different ranks (K vs Q)

        # Same face card = pair
        hand4 = Hand()
        hand4.add_card(Card('K', '♠'))
        hand4.add_card(Card('K', '♥'))
        self.assertTrue(hand4.is_pair())

    def test_pair_with_aces(self):
        """Test pair detection with aces."""
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('A', '♥'))
        self.assertTrue(hand.is_pair())
        self.assertTrue(hand.can_split())

    def test_clear_hand(self):
        """Test clearing a hand."""
        hand = Hand()
        hand.add_card(Card('K', '♠'))
        hand.add_card(Card('Q', '♥'))
        self.assertEqual(len(hand), 2)

        hand.clear()
        self.assertEqual(len(hand), 0)
        self.assertEqual(hand.value(), 0)

    def test_hand_repr(self):
        """Test hand string representation."""
        hand = Hand()
        self.assertEqual(repr(hand), "Hand(empty)")

        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('8', '♥'))
        repr_str = repr(hand)
        self.assertIn("A♠", repr_str)
        self.assertIn("8♥", repr_str)
        self.assertIn("19", repr_str)
        self.assertIn("soft", repr_str)

    def test_soft_17(self):
        """Test the classic soft 17 (A-6)."""
        hand = Hand()
        hand.add_card(Card('A', '♠'))
        hand.add_card(Card('6', '♥'))
        self.assertEqual(hand.value(), 17)
        self.assertTrue(hand.is_soft())

    def test_hard_17(self):
        """Test hard 17."""
        hand = Hand()
        hand.add_card(Card('10', '♠'))
        hand.add_card(Card('7', '♥'))
        self.assertEqual(hand.value(), 17)
        self.assertFalse(hand.is_soft())

    def test_edge_case_all_aces_as_ones(self):
        """Test hand where all aces must be counted as 1."""
        hand = Hand()
        # Five aces: 1+1+1+1+11 = 15 (soft), but with more cards...
        for _ in range(10):
            hand.add_card(Card('A', '♠'))
        # 10 aces: best is one as 11, nine as 1 = 11+9 = 20
        self.assertEqual(hand.value(), 20)

    def test_21_exactly(self):
        """Test various ways to get 21."""
        # Blackjack
        hand1 = Hand()
        hand1.add_card(Card('A', '♠'))
        hand1.add_card(Card('K', '♥'))
        self.assertEqual(hand1.value(), 21)
        self.assertTrue(hand1.is_blackjack())

        # Three sevens
        hand2 = Hand()
        hand2.add_card(Card('7', '♠'))
        hand2.add_card(Card('7', '♥'))
        hand2.add_card(Card('7', '♦'))
        self.assertEqual(hand2.value(), 21)
        self.assertFalse(hand2.is_blackjack())

        # Soft 21
        hand3 = Hand()
        hand3.add_card(Card('A', '♠'))
        hand3.add_card(Card('5', '♥'))
        hand3.add_card(Card('5', '♦'))
        self.assertEqual(hand3.value(), 21)
        self.assertFalse(hand3.is_blackjack())


if __name__ == '__main__':
    unittest.main()
