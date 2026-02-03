"""
Unit tests for cards module.
"""

import unittest
from src.cards import Card, Deck, Shoe


class TestCard(unittest.TestCase):
    """Test cases for Card class."""

    def test_card_creation(self):
        """Test creating a valid card."""
        card = Card('A', '♠')
        self.assertEqual(card.rank, 'A')
        self.assertEqual(card.suit, '♠')

    def test_invalid_rank(self):
        """Test that invalid rank raises ValueError."""
        with self.assertRaises(ValueError):
            Card('X', '♠')

    def test_invalid_suit(self):
        """Test that invalid suit raises ValueError."""
        with self.assertRaises(ValueError):
            Card('A', 'X')

    def test_card_values(self):
        """Test card value calculations."""
        self.assertEqual(Card('2', '♠').value(), 2)
        self.assertEqual(Card('10', '♠').value(), 10)
        self.assertEqual(Card('J', '♠').value(), 10)
        self.assertEqual(Card('Q', '♠').value(), 10)
        self.assertEqual(Card('K', '♠').value(), 10)
        self.assertEqual(Card('A', '♠').value(), 11)

    def test_card_equality(self):
        """Test card equality comparison."""
        card1 = Card('A', '♠')
        card2 = Card('A', '♠')
        card3 = Card('A', '♥')
        self.assertEqual(card1, card2)
        self.assertNotEqual(card1, card3)

    def test_card_repr(self):
        """Test card string representation."""
        card = Card('A', '♠')
        self.assertEqual(repr(card), 'A♠')

    def test_hi_lo_values(self):
        """Test Hi-Lo count values for all ranks."""
        # Low cards (2-6): +1
        for rank in ['2', '3', '4', '5', '6']:
            self.assertEqual(Card(rank, '♠').hi_lo_value(), 1)
        # Neutral cards (7-9): 0
        for rank in ['7', '8', '9']:
            self.assertEqual(Card(rank, '♠').hi_lo_value(), 0)
        # High cards (10-A): -1
        for rank in ['10', 'J', 'Q', 'K', 'A']:
            self.assertEqual(Card(rank, '♠').hi_lo_value(), -1)


class TestDeck(unittest.TestCase):
    """Test cases for Deck class."""

    def test_deck_creation(self):
        """Test creating a standard deck."""
        deck = Deck()
        self.assertEqual(len(deck), 52)

    def test_deck_has_all_cards(self):
        """Test that deck contains all 52 unique cards."""
        deck = Deck()
        ranks = [card.rank for card in deck.cards]
        suits = [card.suit for card in deck.cards]

        # Each rank should appear 4 times (one per suit)
        for rank in Card.RANKS:
            self.assertEqual(ranks.count(rank), 4)

        # Each suit should appear 13 times (one per rank)
        for suit in Card.SUITS:
            self.assertEqual(suits.count(suit), 13)

    def test_deck_shuffle(self):
        """Test that shuffling changes card order."""
        deck = Deck()
        original_order = [repr(card) for card in deck.cards]
        deck.shuffle()
        shuffled_order = [repr(card) for card in deck.cards]

        # After shuffling, order should be different (statistically almost certain)
        # and length should be the same
        self.assertEqual(len(deck), 52)
        self.assertNotEqual(original_order, shuffled_order)


class TestShoe(unittest.TestCase):
    """Test cases for Shoe class."""

    def test_shoe_creation(self):
        """Test creating a shoe with multiple decks."""
        shoe = Shoe(num_decks=6)
        self.assertEqual(shoe.total_cards, 52 * 6)
        self.assertEqual(len(shoe.cards), 52 * 6)

    def test_single_deck_shoe(self):
        """Test creating a single-deck shoe."""
        shoe = Shoe(num_decks=1)
        self.assertEqual(shoe.total_cards, 52)

    def test_invalid_num_decks(self):
        """Test that invalid num_decks raises ValueError."""
        with self.assertRaises(ValueError):
            Shoe(num_decks=0)

    def test_invalid_penetration(self):
        """Test that invalid penetration raises ValueError."""
        with self.assertRaises(ValueError):
            Shoe(penetration=1.5)
        with self.assertRaises(ValueError):
            Shoe(penetration=-0.1)

    def test_deal_card(self):
        """Test dealing cards from shoe."""
        shoe = Shoe(num_decks=1, penetration=1.0)
        initial_count = len(shoe.cards)

        card = shoe.deal_card()
        self.assertIsInstance(card, Card)
        self.assertEqual(len(shoe.cards), initial_count - 1)
        self.assertEqual(shoe.cards_dealt, 1)

    def test_penetration_reshuffle(self):
        """Test that shoe reshuffles at penetration threshold."""
        shoe = Shoe(num_decks=1, penetration=0.5)

        # Deal cards up to penetration point
        cards_to_deal = int(52 * 0.5) + 1
        for _ in range(cards_to_deal):
            shoe.deal_card()

        # After dealing past penetration, shoe should have reshuffled
        # We've dealt 27 cards: 26 before reshuffle, then 1 after
        self.assertEqual(len(shoe.cards), 51)  # One card dealt from fresh shoe
        self.assertEqual(shoe.cards_dealt, 1)  # One card dealt since reshuffle

    def test_infinite_shoe(self):
        """Test infinite deck mode."""
        shoe = Shoe(num_decks=6, infinite=True)

        # Deal many cards (more than would be in the shoe)
        for _ in range(1000):
            card = shoe.deal_card()
            self.assertIsInstance(card, Card)

        # Infinite shoe never runs out
        self.assertEqual(shoe.cards_remaining(), float('inf'))
        self.assertFalse(shoe.needs_shuffle())

    def test_infinite_shoe_sampling(self):
        """Test that infinite shoe samples reasonably from all ranks."""
        shoe = Shoe(num_decks=6, infinite=True)

        # Deal 520 cards (10 full decks worth)
        dealt_ranks = [shoe.deal_card().rank for _ in range(520)]

        # Each rank should appear roughly 40 times (520 / 13)
        # We use a loose bound to avoid test flakiness
        for rank in Card.RANKS:
            count = dealt_ranks.count(rank)
            # Should be roughly 40, give or take (allow 15-65 for randomness)
            self.assertGreater(count, 15)
            self.assertLess(count, 65)

    def test_cards_remaining(self):
        """Test tracking cards remaining in shoe."""
        shoe = Shoe(num_decks=1, penetration=1.0)
        self.assertEqual(shoe.cards_remaining(), 52)

        shoe.deal_card()
        self.assertEqual(shoe.cards_remaining(), 51)

    def test_shoe_repr(self):
        """Test shoe string representation."""
        shoe = Shoe(num_decks=6)
        self.assertIn("Shoe", repr(shoe))

        infinite_shoe = Shoe(num_decks=6, infinite=True)
        self.assertIn("infinite", repr(infinite_shoe))

    def test_running_count_initialization(self):
        """Test that running count starts at zero."""
        shoe = Shoe(num_decks=6)
        self.assertEqual(shoe.running_count, 0)

    def test_running_count_updated_on_deal(self):
        """Test that running count is updated when cards are dealt."""
        shoe = Shoe(num_decks=1, penetration=1.0)
        initial_count = shoe.running_count

        # Deal cards and verify count changes
        card = shoe.deal_card()
        expected_count = initial_count + card.hi_lo_value()
        self.assertEqual(shoe.running_count, expected_count)

    def test_running_count_resets_on_shuffle(self):
        """Test that running count resets to zero on shuffle."""
        shoe = Shoe(num_decks=1, penetration=1.0)

        # Deal some cards to build up count
        for _ in range(10):
            shoe.deal_card()

        # Shuffle and check count is reset
        shoe.shuffle()
        self.assertEqual(shoe.running_count, 0)

    def test_running_count_resets_on_rebuild(self):
        """Test that running count resets when shoe rebuilds at penetration."""
        shoe = Shoe(num_decks=1, penetration=0.5)

        # Deal past penetration to trigger rebuild
        cards_to_deal = int(52 * 0.5) + 1
        for _ in range(cards_to_deal):
            shoe.deal_card()

        # After rebuild, only one card dealt so count should reflect just that card
        # (cards_dealt should be 1, count should be hi_lo_value of that one card)
        self.assertEqual(shoe.cards_dealt, 1)
        # Count should be small (just one card's value)
        self.assertIn(shoe.running_count, [-1, 0, 1])

    def test_true_count_calculation(self):
        """Test true count is running count divided by decks remaining."""
        shoe = Shoe(num_decks=2, penetration=1.0)

        # Manually set running count for testing
        shoe.running_count = 8

        # With 104 cards (2 decks), true count should be 8 / 2 = 4
        self.assertAlmostEqual(shoe.true_count, 4.0, places=1)

        # Deal half the shoe (52 cards)
        for _ in range(52):
            shoe.deal_card()

        # Now ~1 deck remaining, recalculate
        decks_remaining = shoe.decks_remaining()
        expected_tc = shoe.running_count / decks_remaining
        self.assertAlmostEqual(shoe.true_count, expected_tc, places=1)

    def test_decks_remaining(self):
        """Test decks_remaining calculation."""
        shoe = Shoe(num_decks=2, penetration=1.0)
        self.assertAlmostEqual(shoe.decks_remaining(), 2.0, places=1)

        # Deal 52 cards (1 deck)
        for _ in range(52):
            shoe.deal_card()

        self.assertAlmostEqual(shoe.decks_remaining(), 1.0, places=1)

    def test_infinite_shoe_no_count_tracking(self):
        """Test that infinite shoe returns 0 for true count."""
        shoe = Shoe(num_decks=6, infinite=True)

        # Deal many cards
        for _ in range(100):
            shoe.deal_card()

        # True count should always be 0 for infinite shoe
        self.assertEqual(shoe.true_count, 0.0)
        self.assertEqual(shoe.decks_remaining(), float('inf'))


if __name__ == '__main__':
    unittest.main()
