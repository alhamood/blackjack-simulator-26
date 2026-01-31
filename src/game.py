"""
Single hand blackjack game logic.

Classes:
    GameRules: Configuration for game rules
    GameResult: Result of a single hand
    BlackjackGame: Manages a single hand of blackjack
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from src.cards import Shoe
from src.hand import Hand
from src.dealer import Dealer


class PlayerAction(Enum):
    """Possible player actions."""
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"


class HandOutcome(Enum):
    """Possible outcomes for a hand."""
    PLAYER_WIN = "player_win"
    DEALER_WIN = "dealer_win"
    PUSH = "push"
    PLAYER_BLACKJACK = "player_blackjack"
    PLAYER_BUST = "player_bust"
    DEALER_BUST = "dealer_bust"


@dataclass
class GameRules:
    """
    Configuration for blackjack game rules.

    Attributes:
        dealer_hits_soft_17: If True, dealer hits on soft 17
        surrender_allowed: If True, player can surrender
        double_after_split: If True, player can double after splitting
        blackjack_payout: Payout multiplier for blackjack (1.5 for 3:2, 1.2 for 6:5)
    """
    dealer_hits_soft_17: bool = False
    surrender_allowed: bool = True
    double_after_split: bool = True
    blackjack_payout: float = 1.5  # 3:2 payout


@dataclass
class GameResult:
    """
    Result of a single blackjack hand.

    Attributes:
        outcome: The outcome of the hand
        player_hand: Final player hand
        dealer_hand: Final dealer hand
        payout: Net payout (positive = player wins, negative = player loses)
        bet: Original bet amount
    """
    outcome: HandOutcome
    player_hand: Hand
    dealer_hand: Hand
    payout: float
    bet: float = 1.0


class BlackjackGame:
    """
    Manages a single hand of blackjack.

    Simplified for simulation - no splitting support yet.
    """

    def __init__(self, shoe: Shoe, rules: Optional[GameRules] = None):
        """
        Initialize a blackjack game.

        Args:
            shoe: The shoe to deal cards from
            rules: Game rules configuration (uses defaults if None)
        """
        self.shoe = shoe
        self.rules = rules or GameRules()
        self.dealer = Dealer(hits_soft_17=self.rules.dealer_hits_soft_17)
        self.player_hand = Hand()
        self.bet = 1.0  # Default bet

    def deal_initial_cards(self):
        """Deal initial two cards to player and dealer."""
        self.player_hand.clear()
        self.dealer.clear_hand()

        # Deal alternating (player, dealer, player, dealer)
        self.player_hand.add_card(self.shoe.deal_card())
        self.dealer.hand.add_card(self.shoe.deal_card())
        self.player_hand.add_card(self.shoe.deal_card())
        self.dealer.hand.add_card(self.shoe.deal_card())

    def play_hand(self, strategy_func=None, deal_cards=True) -> GameResult:
        """
        Play a complete hand of blackjack.

        Args:
            strategy_func: Optional function that takes (player_hand, dealer_upcard)
                         and returns a PlayerAction. If None, player stands.
            deal_cards: If True, deal initial cards. Set False if cards already dealt.

        Returns:
            GameResult with outcome and payout
        """
        if deal_cards:
            self.deal_initial_cards()

        # Check for dealer blackjack
        if self.dealer.has_blackjack():
            if self.player_hand.is_blackjack():
                # Push - both have blackjack
                return GameResult(
                    outcome=HandOutcome.PUSH,
                    player_hand=self.player_hand,
                    dealer_hand=self.dealer.hand,
                    payout=0.0,
                    bet=self.bet
                )
            else:
                # Dealer wins with blackjack
                return GameResult(
                    outcome=HandOutcome.DEALER_WIN,
                    player_hand=self.player_hand,
                    dealer_hand=self.dealer.hand,
                    payout=-self.bet,
                    bet=self.bet
                )

        # Check for player blackjack (dealer doesn't have blackjack)
        if self.player_hand.is_blackjack():
            return GameResult(
                outcome=HandOutcome.PLAYER_BLACKJACK,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=self.bet * self.rules.blackjack_payout,
                bet=self.bet
            )

        # Player's turn
        while True:
            if self.player_hand.is_bust():
                break

            # Get action from strategy (or default to stand)
            if strategy_func:
                action = strategy_func(self.player_hand, self.dealer.upcard())
            else:
                action = PlayerAction.STAND

            if action == PlayerAction.HIT:
                self.player_hand.add_card(self.shoe.deal_card())
            elif action == PlayerAction.STAND:
                break
            elif action == PlayerAction.DOUBLE:
                # Double down: double bet, take one card, end turn
                self.bet *= 2
                self.player_hand.add_card(self.shoe.deal_card())
                break
            elif action == PlayerAction.SURRENDER:
                if self.rules.surrender_allowed:
                    # Surrender: lose half bet
                    return GameResult(
                        outcome=HandOutcome.DEALER_WIN,
                        player_hand=self.player_hand,
                        dealer_hand=self.dealer.hand,
                        payout=-self.bet * 0.5,
                        bet=self.bet
                    )
                else:
                    # If surrender not allowed, treat as stand
                    break
            else:
                # Unknown action, treat as stand
                break

        # Check if player busted
        if self.player_hand.is_bust():
            return GameResult(
                outcome=HandOutcome.PLAYER_BUST,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=-self.bet,
                bet=self.bet
            )

        # Dealer's turn (player didn't bust)
        self.dealer.play_hand(self.shoe)

        # Determine winner
        return self._determine_winner()

    def _determine_winner(self) -> GameResult:
        """
        Determine the winner after both player and dealer have played.

        Returns:
            GameResult with outcome and payout
        """
        player_value = self.player_hand.value()
        dealer_value = self.dealer.value()

        # Dealer bust
        if self.dealer.is_bust():
            return GameResult(
                outcome=HandOutcome.DEALER_BUST,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=self.bet,
                bet=self.bet
            )

        # Compare values
        if player_value > dealer_value:
            return GameResult(
                outcome=HandOutcome.PLAYER_WIN,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=self.bet,
                bet=self.bet
            )
        elif player_value < dealer_value:
            return GameResult(
                outcome=HandOutcome.DEALER_WIN,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=-self.bet,
                bet=self.bet
            )
        else:
            # Push
            return GameResult(
                outcome=HandOutcome.PUSH,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=0.0,
                bet=self.bet
            )
