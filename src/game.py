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
        bet: Original bet amount (total across all split hands)
        initial_player_hand: Initial 2-card hand (for strategy verification)
        initial_dealer_upcard: Dealer's upcard (for strategy verification)
        actions: List of actions taken during the hand (for debugging)
        split_hands_count: Number of hands created (1 if no split, 2+ if split)
        split_bets: List of individual hand bets (for debugging splits)
        split_payouts: List of individual hand payouts (for debugging splits)
    """
    outcome: HandOutcome
    player_hand: Hand
    dealer_hand: Hand
    payout: float
    bet: float = 1.0
    initial_player_hand: Optional[Hand] = None
    initial_dealer_upcard: Optional[int] = None
    actions: list = None
    split_hands_count: int = 1
    split_bets: list = None
    split_payouts: list = None
    split_hands_final: list = None  # List of (cards, value, soft) tuples for each split hand

    def __post_init__(self):
        """Initialize lists if not provided."""
        if self.actions is None:
            self.actions = []
        if self.split_bets is None:
            self.split_bets = []
        if self.split_payouts is None:
            self.split_payouts = []
        if self.split_hands_final is None:
            self.split_hands_final = []


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

        # Capture initial hand state (for strategy verification)
        initial_hand = Hand()
        for card in self.player_hand.cards[:2]:  # Copy first 2 cards
            initial_hand.add_card(card)
        initial_dealer_upcard = self.dealer.upcard().rank  # Store just the rank, not the whole card
        actions = []

        # Check for dealer blackjack
        if self.dealer.has_blackjack():
            if self.player_hand.is_blackjack():
                # Push - both have blackjack
                return GameResult(
                    outcome=HandOutcome.PUSH,
                    player_hand=self.player_hand,
                    dealer_hand=self.dealer.hand,
                    payout=0.0,
                    bet=self.bet,
                    initial_player_hand=initial_hand,
                    initial_dealer_upcard=initial_dealer_upcard,
                    actions=actions
                )
            else:
                # Dealer wins with blackjack
                return GameResult(
                    outcome=HandOutcome.DEALER_WIN,
                    player_hand=self.player_hand,
                    dealer_hand=self.dealer.hand,
                    payout=-self.bet,
                    bet=self.bet,
                    initial_player_hand=initial_hand,
                    initial_dealer_upcard=initial_dealer_upcard,
                    actions=actions
                )

        # Check for player blackjack (dealer doesn't have blackjack)
        if self.player_hand.is_blackjack():
            return GameResult(
                outcome=HandOutcome.PLAYER_BLACKJACK,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=self.bet * self.rules.blackjack_payout,
                bet=self.bet,
                initial_player_hand=initial_hand,
                initial_dealer_upcard=initial_dealer_upcard,
                actions=actions
            )

        # Initialize split hands structure
        # Each entry tracks: hand, bet, whether it's complete, if it's split aces, and actions for this hand
        split_hands = [{
            'hand': self.player_hand,
            'bet': 1.0,
            'is_complete': False,
            'is_aces': False,
            'actions': []
        }]

        # Player's turn - process each hand (including splits)
        hand_idx = 0
        while hand_idx < len(split_hands):
            hand_dict = split_hands[hand_idx]
            current_hand = hand_dict['hand']

            # Skip if hand is already complete
            if hand_dict['is_complete']:
                hand_idx += 1
                continue

            # Special handling for split hands that haven't received their second card yet
            # Check explicitly for False (not just falsy) to avoid affecting the original hand
            if hand_dict.get('received_card') == False:
                # Deal one card to complete the initial 2-card hand
                current_hand.add_card(self.shoe.deal_card())
                hand_dict['received_card'] = True

                # For split aces, mark complete (no further actions allowed)
                if hand_dict['is_aces']:
                    hand_dict['is_complete'] = True
                    hand_idx += 1
                    continue
                # For non-aces, fall through to normal action loop

            # Normal action loop for this hand
            while True:
                if current_hand.is_bust():
                    hand_dict['is_complete'] = True
                    break

                # Get action from strategy (or default to stand)
                if strategy_func:
                    action = strategy_func(current_hand, self.dealer.upcard())
                else:
                    action = PlayerAction.STAND

                # Handle SPLIT action
                if action == PlayerAction.SPLIT:
                    # Verify split is allowed (is pair, has 2 cards, not exceeded max hands)
                    if current_hand.is_pair() and len(current_hand.cards) == 2 and len(split_hands) < 4:
                        # Get the two cards
                        card1 = current_hand.cards[0]
                        card2 = current_hand.cards[1]

                        # Check if splitting aces
                        is_aces = (card1.rank == 'A')

                        # Create two new hands
                        hand1 = Hand()
                        hand1.add_card(card1)
                        hand1.add_card(self.shoe.deal_card())

                        hand2 = Hand()
                        hand2.add_card(card2)
                        # Second hand will receive its card when we iterate to it

                        # Replace current hand with first split hand
                        split_hands[hand_idx] = {
                            'hand': hand1,
                            'bet': 1.0,
                            'is_complete': is_aces,  # Aces are complete after one card
                            'is_aces': is_aces,
                            'received_card': True,  # First hand already got its second card
                            'actions': ['split']  # Record that this hand came from a split
                        }

                        # Insert second split hand after current
                        split_hands.insert(hand_idx + 1, {
                            'hand': hand2,
                            'bet': 1.0,
                            'is_complete': False,
                            'is_aces': is_aces,
                            'received_card': False,  # Will get card when we iterate to it
                            'actions': ['split']  # Record that this hand came from a split
                        })

                        # For aces, break (both hands complete after one card)
                        # For other pairs, update current_hand and continue playing first split hand
                        if is_aces:
                            break
                        else:
                            # Update current_hand to the first split hand and continue action loop
                            current_hand = hand1
                            hand_dict = split_hands[hand_idx]  # Update dict reference to new split hand
                            continue  # Continue to next iteration of action loop
                    else:
                        # Split not allowed, treat as stand
                        hand_dict['actions'].append('stand')
                        hand_dict['is_complete'] = True
                        break

                # Handle actions and record what actually happened
                if action == PlayerAction.HIT:
                    hand_dict['actions'].append('hit')
                    current_hand.add_card(self.shoe.deal_card())
                elif action == PlayerAction.STAND:
                    hand_dict['actions'].append('stand')
                    hand_dict['is_complete'] = True
                    break
                elif action == PlayerAction.DOUBLE:
                    # Double down: double bet, take one card, end turn
                    if len(current_hand.cards) == 2 and (self.rules.double_after_split or hand_idx == 0):
                        hand_dict['actions'].append('double')
                        hand_dict['bet'] *= 2
                        current_hand.add_card(self.shoe.deal_card())
                        hand_dict['is_complete'] = True
                        break
                    else:
                        # Double not allowed, treat as hit
                        hand_dict['actions'].append('hit')
                        current_hand.add_card(self.shoe.deal_card())
                elif action == PlayerAction.SURRENDER:
                    # Surrender only allowed on first hand before split
                    if self.rules.surrender_allowed and hand_idx == 0 and len(split_hands) == 1:
                        # Surrender: lose half bet
                        return GameResult(
                            outcome=HandOutcome.DEALER_WIN,
                            player_hand=current_hand,
                            dealer_hand=self.dealer.hand,
                            payout=-hand_dict['bet'] * 0.5,
                            bet=hand_dict['bet'],
                            initial_player_hand=initial_hand,
                            initial_dealer_upcard=initial_dealer_upcard,
                            actions=['surrender']
                        )
                    else:
                        # Surrender not allowed, treat as stand
                        hand_dict['actions'].append('stand')
                        hand_dict['is_complete'] = True
                        break
                else:
                    # Unknown action, treat as stand
                    hand_dict['actions'].append('stand')
                    hand_dict['is_complete'] = True
                    break

            # Move to next hand
            hand_idx += 1

        # Dealer's turn (plays once for all hands)
        self.dealer.play_hand(self.shoe)

        # Aggregate results from all split hands
        total_bet = 0.0
        total_payout = 0.0
        split_bets = []
        split_payouts = []
        split_hands_final = []
        all_actions = []
        primary_outcome = None

        for idx, hand_dict in enumerate(split_hands):
            hand = hand_dict['hand']
            bet = hand_dict['bet']

            # Determine outcome for this hand
            is_split = (len(split_hands) > 1)  # Any split hand pays 1:1 for 21
            outcome, payout = self._evaluate_hand(hand, bet, is_split=is_split)

            # Track first hand's outcome as primary
            if idx == 0:
                primary_outcome = outcome

            total_bet += bet
            total_payout += payout
            split_bets.append(bet)
            split_payouts.append(payout)

            # Store final state of each hand
            split_hands_final.append({
                'cards': [f"{c.rank}{c.suit[0]}" for c in hand.cards],
                'value': hand.value(),
                'soft': hand.is_soft(),
                'bust': hand.is_bust(),
                'actions': hand_dict['actions']
            })

            # Collect actions with hand index (if multiple hands)
            if len(split_hands) > 1:
                for action in hand_dict['actions']:
                    all_actions.append(f"hand_{idx}:{action}")
            else:
                all_actions.extend(hand_dict['actions'])

        # Create single GameResult with aggregated data
        return GameResult(
            outcome=primary_outcome,
            player_hand=split_hands[0]['hand'],  # Primary hand for display
            dealer_hand=self.dealer.hand,
            payout=total_payout,
            bet=total_bet,
            initial_player_hand=initial_hand,
            initial_dealer_upcard=initial_dealer_upcard,
            actions=all_actions,
            split_hands_count=len(split_hands),
            split_bets=split_bets,
            split_payouts=split_payouts,
            split_hands_final=split_hands_final
        )

    def _determine_winner(self, initial_hand: Hand, initial_dealer_upcard: int, actions: list) -> GameResult:
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
                bet=self.bet,
                initial_player_hand=initial_hand,
                initial_dealer_upcard=initial_dealer_upcard,
                actions=actions
            )

        # Compare values
        if player_value > dealer_value:
            return GameResult(
                outcome=HandOutcome.PLAYER_WIN,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=self.bet,
                bet=self.bet,
                initial_player_hand=initial_hand,
                initial_dealer_upcard=initial_dealer_upcard,
                actions=actions
            )
        elif player_value < dealer_value:
            return GameResult(
                outcome=HandOutcome.DEALER_WIN,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=-self.bet,
                bet=self.bet,
                initial_player_hand=initial_hand,
                initial_dealer_upcard=initial_dealer_upcard,
                actions=actions
            )
        else:
            # Push
            return GameResult(
                outcome=HandOutcome.PUSH,
                player_hand=self.player_hand,
                dealer_hand=self.dealer.hand,
                payout=0.0,
                bet=self.bet,
                initial_player_hand=initial_hand,
                initial_dealer_upcard=initial_dealer_upcard,
                actions=actions
            )

    def _evaluate_hand(self, hand: Hand, bet: float, is_split: bool = False) -> tuple[HandOutcome, float]:
        """
        Evaluate a single hand against the dealer.

        Args:
            hand: The player's hand to evaluate
            bet: The bet amount for this hand
            is_split: True if this is a split hand (affects blackjack payout)

        Returns:
            Tuple of (outcome, payout)
        """
        # Player busted
        if hand.is_bust():
            return (HandOutcome.PLAYER_BUST, -bet)

        player_value = hand.value()
        dealer_value = self.dealer.value()

        # Dealer busted
        if self.dealer.is_bust():
            # Check for blackjack (but not if split - 21 after split pays 1:1)
            if hand.is_blackjack() and not is_split:
                return (HandOutcome.PLAYER_BLACKJACK, bet * self.rules.blackjack_payout)
            else:
                return (HandOutcome.DEALER_BUST, bet)

        # Compare values
        if player_value > dealer_value:
            # Check for blackjack (but not if split)
            if hand.is_blackjack() and not is_split:
                return (HandOutcome.PLAYER_BLACKJACK, bet * self.rules.blackjack_payout)
            else:
                return (HandOutcome.PLAYER_WIN, bet)
        elif player_value < dealer_value:
            return (HandOutcome.DEALER_WIN, -bet)
        else:
            # Push
            return (HandOutcome.PUSH, 0.0)
