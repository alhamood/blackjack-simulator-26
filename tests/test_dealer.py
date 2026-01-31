"""
Unit tests for dealer module.
"""

import unittest
from src.cards import Card, Shoe
from src.dealer import Dealer


class TestDealer(unittest.TestCase):
    """Test cases for Dealer class."""

    def test_dealer_creation(self):
        """Test creating a dealer."""
        dealer = Dealer()
        self.assertFalse(dealer.hits_soft_17)
        self.assertEqual(len(dealer.hand), 0)

        dealer_h17 = Dealer(hits_soft_17=True)
        self.assertTrue(dealer_h17.hits_soft_17)

    def test_deal_initial_cards(self):
        """Test dealing initial cards to dealer."""
        dealer = Dealer()
        shoe = Shoe(num_decks=1)

        dealer.deal_initial_cards(shoe)
        self.assertEqual(len(dealer.hand), 2)

    def test_upcard_and_holecard(self):
        """Test accessing dealer's upcard and hole card."""
        dealer = Dealer()
        shoe = Shoe(num_decks=1)
        dealer.deal_initial_cards(shoe)

        upcard = dealer.upcard()
        holecard = dealer.holecard()

        self.assertIsInstance(upcard, Card)
        self.assertIsInstance(holecard, Card)
        self.assertEqual(upcard, dealer.hand.cards[0])
        self.assertEqual(holecard, dealer.hand.cards[1])

    def test_upcard_no_cards_error(self):
        """Test that accessing upcard with no cards raises error."""
        dealer = Dealer()
        with self.assertRaises(ValueError):
            dealer.upcard()

    def test_holecard_insufficient_cards_error(self):
        """Test that accessing hole card with <2 cards raises error."""
        dealer = Dealer()
        dealer.hand.add_card(Card('K', '♠'))
        with self.assertRaises(ValueError):
            dealer.holecard()

    def test_should_hit_on_16(self):
        """Test dealer hits on 16."""
        dealer = Dealer()
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('6', '♥'))
        self.assertEqual(dealer.hand.value(), 16)
        self.assertTrue(dealer.should_hit())

    def test_should_stand_on_hard_17(self):
        """Test dealer stands on hard 17."""
        dealer = Dealer()
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('7', '♥'))
        self.assertEqual(dealer.hand.value(), 17)
        self.assertFalse(dealer.hand.is_soft())
        self.assertFalse(dealer.should_hit())

    def test_should_stand_on_soft_17_default(self):
        """Test dealer stands on soft 17 by default."""
        dealer = Dealer(hits_soft_17=False)
        dealer.hand.add_card(Card('A', '♠'))
        dealer.hand.add_card(Card('6', '♥'))
        self.assertEqual(dealer.hand.value(), 17)
        self.assertTrue(dealer.hand.is_soft())
        self.assertFalse(dealer.should_hit())

    def test_should_hit_soft_17_when_enabled(self):
        """Test dealer hits soft 17 when rule is enabled."""
        dealer = Dealer(hits_soft_17=True)
        dealer.hand.add_card(Card('A', '♠'))
        dealer.hand.add_card(Card('6', '♥'))
        self.assertEqual(dealer.hand.value(), 17)
        self.assertTrue(dealer.hand.is_soft())
        self.assertTrue(dealer.should_hit())

    def test_should_stand_on_18(self):
        """Test dealer stands on 18."""
        dealer = Dealer()
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('8', '♥'))
        self.assertEqual(dealer.hand.value(), 18)
        self.assertFalse(dealer.should_hit())

    def test_should_stand_on_soft_18(self):
        """Test dealer stands on soft 18 (even with H17 rule)."""
        dealer = Dealer(hits_soft_17=True)
        dealer.hand.add_card(Card('A', '♠'))
        dealer.hand.add_card(Card('7', '♥'))
        self.assertEqual(dealer.hand.value(), 18)
        self.assertTrue(dealer.hand.is_soft())
        self.assertFalse(dealer.should_hit())

    def test_play_hand_simple(self):
        """Test dealer playing out a simple hand."""
        dealer = Dealer()
        shoe = Shoe(num_decks=1, infinite=True)

        # Give dealer 16 (should hit)
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('6', '♥'))

        final_hand = dealer.play_hand(shoe)

        # Dealer should have hit at least once
        self.assertGreater(len(final_hand), 2)
        # Final value should be 17+ or bust
        self.assertTrue(final_hand.value() >= 17 or final_hand.is_bust())

    def test_play_hand_stands_on_17(self):
        """Test dealer stands on 17."""
        dealer = Dealer()
        shoe = Shoe(num_decks=1)

        # Give dealer hard 17
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('7', '♥'))

        final_hand = dealer.play_hand(shoe)

        # Dealer should not have hit (still 2 cards)
        self.assertEqual(len(final_hand), 2)
        self.assertEqual(final_hand.value(), 17)

    def test_play_hand_soft_17_stand(self):
        """Test dealer stands on soft 17 (default rule)."""
        dealer = Dealer(hits_soft_17=False)
        shoe = Shoe(num_decks=1)

        # Give dealer soft 17
        dealer.hand.add_card(Card('A', '♠'))
        dealer.hand.add_card(Card('6', '♥'))

        final_hand = dealer.play_hand(shoe)

        # Dealer should not have hit
        self.assertEqual(len(final_hand), 2)
        self.assertEqual(final_hand.value(), 17)
        self.assertTrue(final_hand.is_soft())

    def test_play_hand_soft_17_hit(self):
        """Test dealer hits soft 17 when rule enabled."""
        dealer = Dealer(hits_soft_17=True)
        shoe = Shoe(num_decks=1, infinite=True)

        # Give dealer soft 17
        dealer.hand.add_card(Card('A', '♠'))
        dealer.hand.add_card(Card('6', '♥'))

        final_hand = dealer.play_hand(shoe)

        # Dealer should have hit at least once
        self.assertGreater(len(final_hand), 2)

    def test_blackjack_detection(self):
        """Test dealer blackjack detection."""
        dealer = Dealer()
        dealer.hand.add_card(Card('A', '♠'))
        dealer.hand.add_card(Card('K', '♥'))

        self.assertTrue(dealer.has_blackjack())
        self.assertEqual(dealer.value(), 21)

    def test_bust_detection(self):
        """Test dealer bust detection."""
        dealer = Dealer()
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('Q', '♥'))
        dealer.hand.add_card(Card('5', '♦'))

        self.assertTrue(dealer.is_bust())
        self.assertEqual(dealer.value(), 25)

    def test_clear_hand(self):
        """Test clearing dealer's hand."""
        dealer = Dealer()
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('Q', '♥'))
        self.assertEqual(len(dealer.hand), 2)

        dealer.clear_hand()
        self.assertEqual(len(dealer.hand), 0)

    def test_dealer_repr(self):
        """Test dealer string representation."""
        dealer = Dealer()
        self.assertIn("no cards", repr(dealer))

        dealer.hand.add_card(Card('K', '♠'))
        repr_str = repr(dealer)
        self.assertIn("upcard", repr_str)
        self.assertIn("K♠", repr_str)

        dealer.hand.add_card(Card('7', '♥'))
        repr_str = repr(dealer)
        self.assertIn("hand", repr_str)

    def test_play_hand_stops_on_bust(self):
        """Test that dealer stops playing after busting."""
        dealer = Dealer()
        shoe = Shoe(num_decks=1)

        # Manually bust the dealer
        dealer.hand.add_card(Card('K', '♠'))
        dealer.hand.add_card(Card('K', '♥'))
        dealer.hand.add_card(Card('5', '♦'))
        self.assertTrue(dealer.is_bust())

        initial_count = len(dealer.hand)
        dealer.play_hand(shoe)

        # Should not have drawn more cards after bust
        self.assertEqual(len(dealer.hand), initial_count)


if __name__ == '__main__':
    unittest.main()
