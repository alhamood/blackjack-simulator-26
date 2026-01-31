"""
Player strategy system for blackjack decisions.

Classes:
    Strategy: Loads and executes JSON-based blackjack strategies
"""

import json
from pathlib import Path
from typing import Optional
from src.game import PlayerAction
from src.hand import Hand
from src.cards import Card


class Strategy:
    """
    Blackjack strategy that loads from JSON and provides action lookups.

    The strategy JSON format includes:
    - hard_totals: {player_total: {dealer_upcard: action}}
    - soft_totals: {player_total: {dealer_upcard: action}}
    - pairs: {pair_rank: {dealer_upcard: action}}

    Actions can include fallbacks like:
    - "double_else_hit": double if allowed, otherwise hit
    - "double_else_stand": double if allowed, otherwise stand
    - "surrender_else_hit": surrender if allowed, otherwise hit
    - "surrender_else_split": surrender if allowed, otherwise split
    """

    def __init__(self, strategy_path: str):
        """
        Load a strategy from a JSON file.

        Args:
            strategy_path: Path to the strategy JSON file
        """
        with open(strategy_path, 'r') as f:
            data = json.load(f)

        self.name = data.get('name', 'Unknown Strategy')
        self.description = data.get('description', '')
        self.rules = data.get('rules', {})

        # Load strategy tables
        strategy_data = data.get('strategy', {})
        self.hard_totals = strategy_data.get('hard_totals', {})
        self.soft_totals = strategy_data.get('soft_totals', {})
        self.pairs = strategy_data.get('pairs', {})
        self.action_codes = data.get('action_codes', {})

    def get_action(
        self,
        player_hand: Hand,
        dealer_upcard: Card,
        can_double: bool = True,
        can_surrender: bool = True,
        can_split: bool = False
    ) -> PlayerAction:
        """
        Get the recommended action for a given situation.

        Args:
            player_hand: The player's current hand
            dealer_upcard: The dealer's face-up card
            can_double: Whether doubling is allowed (usually only on first 2 cards)
            can_surrender: Whether surrender is allowed
            can_split: Whether splitting is allowed (pair on first 2 cards)

        Returns:
            PlayerAction to take
        """
        # Normalize dealer upcard (A, 2-10)
        dealer_key = self._normalize_dealer_upcard(dealer_upcard)

        # Check for pairs first (if can split and hand is a pair)
        if can_split and player_hand.is_pair() and len(player_hand) == 2:
            pair_rank = self._normalize_pair_rank(player_hand.cards[0])
            if pair_rank in self.pairs:
                action_str = self.pairs[pair_rank].get(dealer_key, 'stand')
                return self._resolve_action(
                    action_str,
                    can_double=can_double,
                    can_surrender=can_surrender,
                    can_split=can_split
                )

        # Check soft vs hard totals
        hand_value = player_hand.value()

        if player_hand.is_soft():
            # Soft hand (has an ace counted as 11)
            hand_key = str(hand_value)
            if hand_key in self.soft_totals:
                action_str = self.soft_totals[hand_key].get(dealer_key, 'stand')
                return self._resolve_action(
                    action_str,
                    can_double=can_double,
                    can_surrender=can_surrender,
                    can_split=False  # Already checked pairs
                )

        # Hard hand (no soft ace)
        hand_key = str(hand_value)
        if hand_key in self.hard_totals:
            action_str = self.hard_totals[hand_key].get(dealer_key, 'stand')
            return self._resolve_action(
                action_str,
                can_double=can_double,
                can_surrender=can_surrender,
                can_split=False  # Already checked pairs
            )

        # Default: stand if >= 17, otherwise hit
        if hand_value >= 17:
            return PlayerAction.STAND
        return PlayerAction.HIT

    def _normalize_dealer_upcard(self, card: Card) -> str:
        """
        Normalize dealer upcard to strategy table key (2-10, A).

        Args:
            card: The dealer's upcard

        Returns:
            String key for strategy lookup
        """
        if card.rank == 'A':
            return 'A'
        elif card.rank in ['J', 'Q', 'K']:
            return '10'
        else:
            return card.rank

    def _normalize_pair_rank(self, card: Card) -> str:
        """
        Normalize card rank for pair lookup (2-10, A).

        Args:
            card: One card from the pair

        Returns:
            String key for pair lookup
        """
        if card.rank == 'A':
            return 'A'
        elif card.rank in ['J', 'Q', 'K']:
            return '10'
        else:
            return card.rank

    def _resolve_action(
        self,
        action_str: str,
        can_double: bool,
        can_surrender: bool,
        can_split: bool
    ) -> PlayerAction:
        """
        Resolve action string to PlayerAction, handling fallbacks.

        Args:
            action_str: Action string from strategy table
            can_double: Whether doubling is allowed
            can_surrender: Whether surrender is allowed
            can_split: Whether splitting is allowed

        Returns:
            Resolved PlayerAction
        """
        # Handle simple actions
        if action_str == 'hit':
            return PlayerAction.HIT
        elif action_str == 'stand':
            return PlayerAction.STAND
        elif action_str == 'double':
            return PlayerAction.DOUBLE if can_double else PlayerAction.HIT
        elif action_str == 'split':
            return PlayerAction.SPLIT if can_split else PlayerAction.HIT
        elif action_str == 'surrender':
            return PlayerAction.SURRENDER if can_surrender else PlayerAction.HIT

        # Handle fallback actions
        elif action_str == 'double_else_hit':
            return PlayerAction.DOUBLE if can_double else PlayerAction.HIT
        elif action_str == 'double_else_stand':
            return PlayerAction.DOUBLE if can_double else PlayerAction.STAND
        elif action_str == 'surrender_else_hit':
            return PlayerAction.SURRENDER if can_surrender else PlayerAction.HIT
        elif action_str == 'surrender_else_stand':
            return PlayerAction.SURRENDER if can_surrender else PlayerAction.STAND
        elif action_str == 'surrender_else_split':
            if can_surrender:
                return PlayerAction.SURRENDER
            elif can_split:
                return PlayerAction.SPLIT
            else:
                return PlayerAction.HIT

        # Unknown action - default to stand
        return PlayerAction.STAND

    def __str__(self) -> str:
        """Return strategy name."""
        return self.name

    def __repr__(self) -> str:
        """Return detailed strategy representation."""
        return f"Strategy('{self.name}')"
