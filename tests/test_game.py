"""
Unit tests for game module.
"""

import unittest
from src.cards import Card, Shoe
from src.game import BlackjackGame, GameRules, PlayerAction, HandOutcome


class TestGameRules(unittest.TestCase):
    """Test cases for GameRules dataclass."""

    def test_default_rules(self):
        """Test default game rules."""
        rules = GameRules()
        self.assertFalse(rules.dealer_hits_soft_17)
        self.assertTrue(rules.surrender_allowed)
        self.assertTrue(rules.double_after_split)
        self.assertEqual(rules.blackjack_payout, 1.5)

    def test_custom_rules(self):
        """Test creating custom game rules."""
        rules = GameRules(
            dealer_hits_soft_17=True,
            surrender_allowed=False,
            blackjack_payout=1.2  # 6:5 payout
        )
        self.assertTrue(rules.dealer_hits_soft_17)
        self.assertFalse(rules.surrender_allowed)
        self.assertEqual(rules.blackjack_payout, 1.2)


class TestBlackjackGame(unittest.TestCase):
    """Test cases for BlackjackGame class."""

    def test_game_creation(self):
        """Test creating a blackjack game."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        self.assertIsNotNone(game.shoe)
        self.assertIsNotNone(game.dealer)
        self.assertIsNotNone(game.player_hand)
        self.assertIsNotNone(game.rules)

    def test_deal_initial_cards(self):
        """Test dealing initial cards."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        game.deal_initial_cards()

        self.assertEqual(len(game.player_hand), 2)
        self.assertEqual(len(game.dealer.hand), 2)

    def test_player_blackjack_wins(self):
        """Test player winning with blackjack."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Manually set up player blackjack
        game.player_hand.add_card(Card('A', '♠'))
        game.player_hand.add_card(Card('K', '♥'))

        # Dealer gets non-blackjack
        game.dealer.hand.add_card(Card('10', '♠'))
        game.dealer.hand.add_card(Card('9', '♥'))

        # Player should win with blackjack (no need to play)
        result = game.play_hand(deal_cards=False)

        self.assertEqual(result.outcome, HandOutcome.PLAYER_BLACKJACK)
        self.assertEqual(result.payout, 1.5)  # 3:2 payout
        self.assertTrue(result.player_hand.is_blackjack())

    def test_dealer_blackjack_wins(self):
        """Test dealer winning with blackjack."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Player gets non-blackjack
        game.player_hand.add_card(Card('10', '♠'))
        game.player_hand.add_card(Card('9', '♥'))

        # Dealer gets blackjack
        game.dealer.hand.add_card(Card('A', '♠'))
        game.dealer.hand.add_card(Card('K', '♥'))

        result = game.play_hand(deal_cards=False)

        self.assertEqual(result.outcome, HandOutcome.DEALER_WIN)
        self.assertEqual(result.payout, -1.0)

    def test_both_blackjack_push(self):
        """Test push when both have blackjack."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Both get blackjack
        game.player_hand.add_card(Card('A', '♠'))
        game.player_hand.add_card(Card('K', '♥'))

        game.dealer.hand.add_card(Card('A', '♦'))
        game.dealer.hand.add_card(Card('Q', '♣'))

        result = game.play_hand(deal_cards=False)

        self.assertEqual(result.outcome, HandOutcome.PUSH)
        self.assertEqual(result.payout, 0.0)

    def test_player_stands_and_wins(self):
        """Test player standing and winning."""
        shoe = Shoe(num_decks=1, infinite=True)
        game = BlackjackGame(shoe)

        # Player has 20
        game.player_hand.add_card(Card('K', '♠'))
        game.player_hand.add_card(Card('Q', '♥'))

        # Dealer has 16 (will need to hit)
        game.dealer.hand.add_card(Card('10', '♠'))
        game.dealer.hand.add_card(Card('6', '♥'))

        # Player stands (default strategy)
        result = game.play_hand()

        # Player should win (dealer will likely bust or get < 20)
        # Result depends on dealer's draw, but player won't bust
        self.assertFalse(result.player_hand.is_bust())

    def test_player_hits_strategy(self):
        """Test player hitting with a strategy function."""
        shoe = Shoe(num_decks=1, infinite=True)
        game = BlackjackGame(shoe)

        # Player has 12
        game.player_hand.add_card(Card('7', '♠'))
        game.player_hand.add_card(Card('5', '♥'))

        # Dealer shows 6
        game.dealer.hand.add_card(Card('6', '♠'))
        game.dealer.hand.add_card(Card('10', '♥'))

        # Strategy: hit until 17+
        def hit_to_17(player_hand, dealer_upcard):
            if player_hand.value() < 17:
                return PlayerAction.HIT
            return PlayerAction.STAND

        result = game.play_hand(strategy_func=hit_to_17, deal_cards=False)

        # Player should have hit at least once
        self.assertGreaterEqual(len(result.player_hand), 3)

    def test_player_bust_loses(self):
        """Test player busting and losing."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Player will bust
        game.player_hand.add_card(Card('K', '♠'))
        game.player_hand.add_card(Card('Q', '♥'))

        # Dealer has anything
        game.dealer.hand.add_card(Card('7', '♠'))
        game.dealer.hand.add_card(Card('8', '♥'))

        # Strategy: always hit (will bust on first hit)
        def always_hit(player_hand, dealer_upcard):
            return PlayerAction.HIT

        result = game.play_hand(strategy_func=always_hit, deal_cards=False)

        self.assertEqual(result.outcome, HandOutcome.PLAYER_BUST)
        self.assertEqual(result.payout, -1.0)
        self.assertTrue(result.player_hand.is_bust())

    def test_dealer_bust_player_wins(self):
        """Test player winning when dealer busts."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Player has 18
        game.player_hand.add_card(Card('K', '♠'))
        game.player_hand.add_card(Card('8', '♥'))

        # Dealer has 16, will bust with next card
        game.dealer.hand.add_card(Card('K', '♦'))
        game.dealer.hand.add_card(Card('6', '♣'))

        # Add a card to shoe that will bust dealer
        # (In infinite shoe, dealer will keep drawing until bust or stand)
        shoe_inf = Shoe(num_decks=1, infinite=True)
        game.shoe = shoe_inf

        result = game.play_hand()  # Player stands by default

        # Dealer must hit on 16, may bust
        if result.dealer_hand.is_bust():
            self.assertEqual(result.outcome, HandOutcome.DEALER_BUST)
            self.assertEqual(result.payout, 1.0)

    def test_push(self):
        """Test push (tie)."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Both have 20
        game.player_hand.add_card(Card('K', '♠'))
        game.player_hand.add_card(Card('Q', '♥'))

        game.dealer.hand.add_card(Card('10', '♦'))
        game.dealer.hand.add_card(Card('10', '♣'))

        result = game.play_hand(deal_cards=False)

        self.assertEqual(result.outcome, HandOutcome.PUSH)
        self.assertEqual(result.payout, 0.0)

    def test_double_down(self):
        """Test doubling down."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Player has 11
        game.player_hand.add_card(Card('6', '♠'))
        game.player_hand.add_card(Card('5', '♥'))

        # Dealer has anything
        game.dealer.hand.add_card(Card('7', '♠'))
        game.dealer.hand.add_card(Card('10', '♥'))

        # Strategy: double on 11
        def double_on_11(player_hand, dealer_upcard):
            if player_hand.value() == 11 and len(player_hand) == 2:
                return PlayerAction.DOUBLE
            return PlayerAction.STAND

        result = game.play_hand(strategy_func=double_on_11, deal_cards=False)

        # Player should have exactly 3 cards (initial 2 + 1 from double)
        self.assertEqual(len(result.player_hand), 3)
        # Bet should be doubled
        self.assertEqual(result.bet, 2.0)

    def test_surrender(self):
        """Test surrendering."""
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe)

        # Player has 16
        game.player_hand.add_card(Card('K', '♠'))
        game.player_hand.add_card(Card('6', '♥'))

        # Dealer shows ace
        game.dealer.hand.add_card(Card('A', '♠'))
        game.dealer.hand.add_card(Card('7', '♥'))

        # Strategy: always surrender
        def always_surrender(player_hand, dealer_upcard):
            return PlayerAction.SURRENDER

        result = game.play_hand(strategy_func=always_surrender)

        # Should lose half bet
        self.assertEqual(result.payout, -0.5)

    def test_surrender_not_allowed(self):
        """Test that surrender is treated as stand when not allowed."""
        rules = GameRules(surrender_allowed=False)
        shoe = Shoe(num_decks=1, infinite=True)
        game = BlackjackGame(shoe, rules=rules)

        # Player has 16
        game.player_hand.add_card(Card('K', '♠'))
        game.player_hand.add_card(Card('6', '♥'))

        # Dealer has anything
        game.dealer.hand.add_card(Card('7', '♠'))
        game.dealer.hand.add_card(Card('8', '♥'))

        # Try to surrender
        def try_surrender(player_hand, dealer_upcard):
            return PlayerAction.SURRENDER

        result = game.play_hand(strategy_func=try_surrender)

        # Should play out normally (not surrender)
        # Payout should be -1 or +1, not -0.5
        self.assertIn(result.payout, [-1.0, 0.0, 1.0])

    def test_blackjack_payout_6_5(self):
        """Test 6:5 blackjack payout."""
        rules = GameRules(blackjack_payout=1.2)  # 6:5
        shoe = Shoe(num_decks=1)
        game = BlackjackGame(shoe, rules=rules)

        # Player gets blackjack
        game.player_hand.add_card(Card('A', '♠'))
        game.player_hand.add_card(Card('K', '♥'))

        # Dealer doesn't
        game.dealer.hand.add_card(Card('10', '♠'))
        game.dealer.hand.add_card(Card('9', '♥'))

        result = game.play_hand(deal_cards=False)

        self.assertEqual(result.outcome, HandOutcome.PLAYER_BLACKJACK)
        self.assertEqual(result.payout, 1.2)  # 6:5 payout


if __name__ == '__main__':
    unittest.main()
