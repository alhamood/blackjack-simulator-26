"""
Betting strategy system for blackjack bet sizing.

Provides a base class and concrete implementations for various betting
strategies. Each strategy determines bet size before each hand based on
game state (previous outcomes, count, etc.).
"""

import json
from pathlib import Path
from typing import Optional


class BettingStrategy:
    """Base class for all betting strategies."""

    def __init__(self, base_unit: float = 1.0, max_bet: float = 1000.0):
        self.base_unit = base_unit
        self.max_bet = max_bet

    def get_bet(self) -> float:
        """Return the bet for the next hand."""
        return self.base_unit

    def update(self, outcome: str, payout: float, bet: float):
        """Called after each hand. outcome is 'win', 'loss', or 'push'."""
        pass

    def reset(self):
        """Reset state (e.g., at start of new session)."""
        pass

    @staticmethod
    def from_json(path: str) -> 'BettingStrategy':
        """Load a betting strategy from a JSON config file."""
        with open(path, 'r') as f:
            data = json.load(f)
        strategy_type = data.get('type', 'flat')
        params = data.get('params', {})
        cls = STRATEGY_REGISTRY.get(strategy_type, FlatBetting)
        return cls(**params)


class FlatBetting(BettingStrategy):
    """Always bet the same amount."""

    def get_bet(self) -> float:
        return self.base_unit


class MartingaleBetting(BettingStrategy):
    """Double bet after each loss, reset to base after win."""

    def __init__(self, base_unit: float = 1.0, max_bet: float = 1000.0):
        super().__init__(base_unit, max_bet)
        self._current_bet = base_unit

    def get_bet(self) -> float:
        return min(self._current_bet, self.max_bet)

    def update(self, outcome: str, payout: float, bet: float):
        if outcome == 'loss':
            self._current_bet = min(self._current_bet * 2, self.max_bet)
        else:
            self._current_bet = self.base_unit

    def reset(self):
        self._current_bet = self.base_unit


class ReverseMartingaleBetting(BettingStrategy):
    """Double bet after each win, reset to base after loss."""

    def __init__(self, base_unit: float = 1.0, max_bet: float = 1000.0):
        super().__init__(base_unit, max_bet)
        self._current_bet = base_unit

    def get_bet(self) -> float:
        return min(self._current_bet, self.max_bet)

    def update(self, outcome: str, payout: float, bet: float):
        if outcome == 'win':
            self._current_bet = min(self._current_bet * 2, self.max_bet)
        else:
            self._current_bet = self.base_unit

    def reset(self):
        self._current_bet = self.base_unit


class Sequence1326Betting(BettingStrategy):
    """Cycle through 1-3-2-6 unit sequence on consecutive wins."""

    SEQUENCE = [1, 3, 2, 6]

    def __init__(self, base_unit: float = 1.0, max_bet: float = 1000.0):
        super().__init__(base_unit, max_bet)
        self._position = 0

    def get_bet(self) -> float:
        units = self.SEQUENCE[self._position]
        return min(self.base_unit * units, self.max_bet)

    def update(self, outcome: str, payout: float, bet: float):
        if outcome == 'win':
            self._position = min(self._position + 1, len(self.SEQUENCE) - 1)
        else:
            self._position = 0

    def reset(self):
        self._position = 0


class ParoliBetting(BettingStrategy):
    """Double bet after win, reset after 3 consecutive wins or any loss."""

    def __init__(self, base_unit: float = 1.0, max_bet: float = 1000.0):
        super().__init__(base_unit, max_bet)
        self._current_bet = base_unit
        self._consecutive_wins = 0

    def get_bet(self) -> float:
        return min(self._current_bet, self.max_bet)

    def update(self, outcome: str, payout: float, bet: float):
        if outcome == 'win':
            self._consecutive_wins += 1
            if self._consecutive_wins >= 3:
                self._current_bet = self.base_unit
                self._consecutive_wins = 0
            else:
                self._current_bet = min(self._current_bet * 2, self.max_bet)
        else:
            self._current_bet = self.base_unit
            self._consecutive_wins = 0

    def reset(self):
        self._current_bet = self.base_unit
        self._consecutive_wins = 0


class DAlembertBetting(BettingStrategy):
    """Increase bet by 1 unit after loss, decrease by 1 unit after win."""

    def __init__(self, base_unit: float = 1.0, max_bet: float = 1000.0):
        super().__init__(base_unit, max_bet)
        self._current_units = 1

    def get_bet(self) -> float:
        return min(self.base_unit * self._current_units, self.max_bet)

    def update(self, outcome: str, payout: float, bet: float):
        if outcome == 'loss':
            self._current_units += 1
        elif outcome == 'win' and self._current_units > 1:
            self._current_units -= 1

    def reset(self):
        self._current_units = 1


class FibonacciBetting(BettingStrategy):
    """Follow Fibonacci sequence on losses, step back 2 on win."""

    def __init__(self, base_unit: float = 1.0, max_bet: float = 1000.0):
        super().__init__(base_unit, max_bet)
        self._sequence = [1, 1]
        self._position = 0

    def _ensure_sequence(self, pos: int):
        """Extend the Fibonacci sequence if needed."""
        while len(self._sequence) <= pos:
            self._sequence.append(
                self._sequence[-1] + self._sequence[-2]
            )

    def get_bet(self) -> float:
        self._ensure_sequence(self._position)
        units = self._sequence[self._position]
        return min(self.base_unit * units, self.max_bet)

    def update(self, outcome: str, payout: float, bet: float):
        if outcome == 'loss':
            self._position += 1
        elif outcome == 'win':
            self._position = max(0, self._position - 2)

    def reset(self):
        self._position = 0


class HiLoCountingBetting(BettingStrategy):
    """
    Hi-Lo card counting bet spread strategy.

    Adjusts bet size based on the true count. Higher true counts indicate
    a player advantage, warranting larger bets.
    """

    # Default spread: TC -> units multiplier
    DEFAULT_SPREAD = {
        1: 1,   # TC <= 1: 1 unit
        2: 2,   # TC = 2: 2 units
        3: 4,   # TC = 3: 4 units
        4: 8,   # TC >= 4: 8 units
    }

    def __init__(
        self,
        base_unit: float = 1.0,
        max_bet: float = 1000.0,
        spread: Optional[dict] = None,
    ):
        """
        Initialize Hi-Lo counting strategy.

        Args:
            base_unit: Base betting unit
            max_bet: Maximum allowed bet
            spread: Dict mapping true count thresholds to unit multipliers.
                    Keys should be integers; bet is determined by the highest
                    key <= true_count. Default: {1: 1, 2: 2, 3: 4, 4: 8}
        """
        super().__init__(base_unit, max_bet)
        # Convert string keys to int (JSON loads keys as strings)
        if spread is not None:
            self._spread = {int(k): v for k, v in spread.items()}
        else:
            self._spread = self.DEFAULT_SPREAD.copy()
        self._spread_thresholds = sorted(self._spread.keys())
        self._shoe = None

    def set_shoe(self, shoe):
        """Set the shoe reference for count access."""
        self._shoe = shoe

    def get_bet(self) -> float:
        if self._shoe is None or self._shoe.infinite:
            # No shoe or infinite deck: flat bet
            return self.base_unit

        tc = self._shoe.true_count
        # Find the highest threshold <= true count
        units = 1
        for threshold in self._spread_thresholds:
            if tc >= threshold:
                units = self._spread[threshold]
            else:
                break

        return min(self.base_unit * units, self.max_bet)

    def reset(self):
        pass  # No state to reset (count is in the shoe)


# Registry mapping type strings to classes
STRATEGY_REGISTRY = {
    'flat': FlatBetting,
    'martingale': MartingaleBetting,
    'reverse_martingale': ReverseMartingaleBetting,
    '1-3-2-6': Sequence1326Betting,
    'paroli': ParoliBetting,
    'dalembert': DAlembertBetting,
    'fibonacci': FibonacciBetting,
    'hi_lo': HiLoCountingBetting,
}
