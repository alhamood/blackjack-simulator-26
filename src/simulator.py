"""
Blackjack simulation engine for testing strategies.

Classes:
    SimulationResult: Results from a simulation run
    SessionResult: Results from a single session
    Simulator: Runs blackjack simulations with configurable parameters
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Callable, List
import statistics
from src.cards import Shoe
from src.game import BlackjackGame, GameRules, GameResult, HandOutcome, PlayerAction
from src.hand import Hand
from src.cards import Card


@dataclass
class SessionResult:
    """
    Results from a single playing session.

    Attributes:
        hands_played: Number of hands played in this session
        total_payout: Net payout for the session
        win_count: Number of winning hands
        loss_count: Number of losing hands
        push_count: Number of pushes
        blackjack_count: Number of player blackjacks
        bust_count: Number of player busts
        surrender_count: Number of surrenders
        double_count: Number of doubles
        split_count: Number of times player split
        hand_results: Optional list of individual hand results (for sampling/export)
    """
    hands_played: int = 0
    total_payout: float = 0.0
    total_wagered: float = 0.0
    win_count: int = 0
    loss_count: int = 0
    push_count: int = 0
    blackjack_count: int = 0
    bust_count: int = 0
    surrender_count: int = 0
    double_count: int = 0
    split_count: int = 0
    hand_results: List[GameResult] = field(default_factory=list)

    @property
    def ev_per_hand(self) -> float:
        """Expected value per hand."""
        if self.hands_played == 0:
            return 0.0
        return self.total_payout / self.hands_played

    @property
    def ev_per_unit_bet(self) -> float:
        """Expected value per unit wagered."""
        if self.total_wagered == 0:
            return 0.0
        return self.total_payout / self.total_wagered

    @property
    def win_rate(self) -> float:
        """Percentage of hands won (excluding pushes)."""
        total_decided = self.win_count + self.loss_count
        if total_decided == 0:
            return 0.0
        return self.win_count / total_decided


@dataclass
class SimulationResult:
    """
    Results from a complete simulation.

    Attributes:
        total_hands: Total number of hands played
        total_payout: Total net payout across all hands
        sessions: List of individual session results (for multi-session sims)
        win_count: Total wins
        loss_count: Total losses
        push_count: Total pushes
        blackjack_count: Total player blackjacks
        bust_count: Total player busts
        surrender_count: Total surrenders
        double_count: Total doubles
        split_count: Total splits
    """
    total_hands: int = 0
    total_payout: float = 0.0
    total_wagered: float = 0.0
    sessions: List[SessionResult] = field(default_factory=list)
    win_count: int = 0
    loss_count: int = 0
    push_count: int = 0
    blackjack_count: int = 0
    bust_count: int = 0
    surrender_count: int = 0
    double_count: int = 0
    split_count: int = 0
    elapsed_seconds: float = 0.0

    @property
    def ev_per_hand(self) -> float:
        """Overall expected value per hand."""
        if self.total_hands == 0:
            return 0.0
        return self.total_payout / self.total_hands

    @property
    def ev_per_unit_bet(self) -> float:
        """Expected value per unit wagered."""
        if self.total_wagered == 0:
            return 0.0
        return self.total_payout / self.total_wagered

    @property
    def win_rate(self) -> float:
        """Overall win rate (excluding pushes)."""
        total_decided = self.win_count + self.loss_count
        if total_decided == 0:
            return 0.0
        return self.win_count / total_decided

    @property
    def session_ev_mean(self) -> float:
        """Mean EV across sessions."""
        if not self.sessions:
            return self.ev_per_hand
        return statistics.mean(s.ev_per_hand for s in self.sessions)

    @property
    def session_ev_stdev(self) -> float:
        """Standard deviation of EV across sessions."""
        if len(self.sessions) < 2:
            return 0.0
        return statistics.stdev(s.ev_per_hand for s in self.sessions)

    def summary(self) -> str:
        """
        Generate a summary string of the simulation results.

        Returns:
            Formatted summary string
        """
        # Format elapsed time
        if self.elapsed_seconds >= 60:
            time_str = f"{self.elapsed_seconds / 60:.1f} minutes"
        else:
            time_str = f"{self.elapsed_seconds:.2f} seconds"

        lines = [
            f"=== Simulation Results ===",
            f"Total hands: {self.total_hands:,}",
            f"Elapsed time: {time_str}",
            f"Total payout: {self.total_payout:+.2f}",
            f"EV per hand: {self.ev_per_hand:+.6f} ({self.ev_per_hand * 100:+.4f}%)",
            f"",
            f"Outcomes:",
            f"  Wins: {self.win_count:,} ({self.win_count / self.total_hands * 100:.2f}%)",
            f"  Losses: {self.loss_count:,} ({self.loss_count / self.total_hands * 100:.2f}%)",
            f"  Pushes: {self.push_count:,} ({self.push_count / self.total_hands * 100:.2f}%)",
            f"  Win rate: {self.win_rate * 100:.2f}% (excl. pushes)",
            f"",
            f"Special outcomes:",
            f"  Blackjacks: {self.blackjack_count:,}",
            f"  Busts: {self.bust_count:,}",
            f"  Surrenders: {self.surrender_count:,}",
            f"  Doubles: {self.double_count:,}",
        ]

        if self.sessions:
            lines.extend([
                f"",
                f"Session statistics ({len(self.sessions)} sessions):",
                f"  Mean EV: {self.session_ev_mean:+.6f}",
                f"  StdDev: {self.session_ev_stdev:.6f}",
            ])

        return "\n".join(lines)


class Simulator:
    """
    Blackjack simulation engine.

    Runs single-session or multi-session simulations to analyze strategy
    performance across different game conditions.
    """

    def __init__(
        self,
        rules: Optional[GameRules] = None,
        num_decks: int = 6,
        penetration: float = 0.75,
        infinite_shoe: bool = False
    ):
        """
        Initialize the simulator.

        Args:
            rules: Game rules (uses defaults if None)
            num_decks: Number of decks in the shoe
            penetration: Shoe penetration (0.0-1.0, ignored if infinite_shoe=True)
            infinite_shoe: If True, use infinite shoe (CSM simulation)
        """
        self.rules = rules or GameRules()
        self.num_decks = num_decks
        self.penetration = penetration
        self.infinite_shoe = infinite_shoe

    def run_session(
        self,
        num_hands: int,
        strategy_func: Callable[[Hand, Card], PlayerAction],
        shoe: Optional[Shoe] = None,
        betting_strategy=None,
        track_hands: bool = False,
        max_tracked_hands: int = 100
    ) -> SessionResult:
        """
        Run a single session of blackjack.

        Args:
            num_hands: Number of hands to play
            strategy_func: Strategy function (player_hand, dealer_upcard) -> PlayerAction
            shoe: Optional shoe to use (creates new one if None)
            betting_strategy: Optional BettingStrategy for variable bet sizing
            track_hands: If True, store individual hand results for export
            max_tracked_hands: Maximum number of hands to track (default 100)

        Returns:
            SessionResult with statistics
        """
        if shoe is None:
            shoe = Shoe(
                num_decks=self.num_decks,
                penetration=self.penetration,
                infinite=self.infinite_shoe
            )

        if betting_strategy:
            betting_strategy.reset()
            if hasattr(betting_strategy, 'set_shoe'):
                betting_strategy.set_shoe(shoe)

        session = SessionResult()

        for _ in range(num_hands):
            # Get bet from betting strategy
            bet = betting_strategy.get_bet() if betting_strategy else 1.0

            game = BlackjackGame(shoe, rules=self.rules, bet=bet)
            result = game.play_hand(strategy_func=strategy_func)

            # Update betting strategy with outcome
            if betting_strategy:
                if result.payout > 0:
                    outcome = 'win'
                elif result.payout < 0:
                    outcome = 'loss'
                else:
                    outcome = 'push'
                betting_strategy.update(outcome, result.payout, result.bet)

            # Update statistics
            session.hands_played += 1
            session.total_payout += result.payout
            session.total_wagered += result.bet

            # Track outcomes
            if result.payout > 0:
                session.win_count += 1
            elif result.payout < 0:
                session.loss_count += 1
            else:
                session.push_count += 1

            # Track special outcomes
            if result.outcome == HandOutcome.PLAYER_BLACKJACK:
                session.blackjack_count += 1
            elif result.outcome == HandOutcome.PLAYER_BUST:
                session.bust_count += 1

            # Track surrenders (payout is half the bet)
            if result.outcome == HandOutcome.DEALER_WIN and abs(result.payout) == bet * 0.5:
                session.surrender_count += 1

            # Track doubles (actions contain double)
            if any('double' in action for action in result.actions):
                session.double_count += 1

            # Track splits (split_hands_count > 1)
            if result.split_hands_count > 1:
                session.split_count += 1

            # Store hand result if tracking is enabled
            if track_hands and len(session.hand_results) < max_tracked_hands:
                session.hand_results.append(result)

        return session

    def run_simulation(
        self,
        total_hands: int,
        strategy_func: Callable[[Hand, Card], PlayerAction],
        num_sessions: int = 1,
        betting_strategy=None,
        track_hands: bool = False,
        max_tracked_hands: int = 100
    ) -> SimulationResult:
        """
        Run a complete simulation.

        Two modes:
        1. Single session (num_sessions=1): Run total_hands in one long session
        2. Multiple sessions (num_sessions>1): Run num_sessions sessions of
           (total_hands / num_sessions) hands each

        Args:
            total_hands: Total number of hands to play across all sessions
            strategy_func: Strategy function
            num_sessions: Number of sessions (1 for single long session)
            betting_strategy: Optional BettingStrategy for variable bet sizing
            track_hands: If True, store sample of individual hand results for export
            max_tracked_hands: Maximum number of hands to track (default 100)

        Returns:
            SimulationResult with complete statistics
        """
        result = SimulationResult()
        start_time = time.perf_counter()

        if num_sessions == 1:
            # Single session mode - one long session
            session = self.run_session(
                total_hands,
                strategy_func,
                betting_strategy=betting_strategy,
                track_hands=track_hands,
                max_tracked_hands=max_tracked_hands
            )
            result.sessions = [session]
        else:
            # Multi-session mode - divide hands across sessions
            hands_per_session = total_hands // num_sessions

            for _ in range(num_sessions):
                session = self.run_session(
                    hands_per_session,
                    strategy_func,
                    betting_strategy=betting_strategy,
                    track_hands=track_hands,
                    max_tracked_hands=max_tracked_hands
                )
                result.sessions.append(session)

        result.elapsed_seconds = time.perf_counter() - start_time

        # Aggregate results from all sessions
        for session in result.sessions:
            result.total_hands += session.hands_played
            result.total_payout += session.total_payout
            result.total_wagered += session.total_wagered
            result.win_count += session.win_count
            result.loss_count += session.loss_count
            result.push_count += session.push_count
            result.blackjack_count += session.blackjack_count
            result.bust_count += session.bust_count
            result.surrender_count += session.surrender_count
            result.double_count += session.double_count
            result.split_count += session.split_count

        return result

    def estimate_time(
        self,
        total_hands: int,
        strategy_func: Callable[[Hand, Card], PlayerAction],
        num_sessions: int = 1,
        calibration_hands: int = 5000
    ) -> float:
        """
        Estimate how long a simulation will take by running a small calibration.

        Runs a short simulation with the same configuration and extrapolates
        linearly to the requested size. For multi-session simulations, uses
        the same hands-per-session as the real run so that per-session
        overhead is accurately captured.

        Args:
            total_hands: Total number of hands for the full simulation
            strategy_func: Strategy function to use
            num_sessions: Number of sessions for the full simulation
            calibration_hands: Number of hands to use for calibration (single-session)

        Returns:
            Estimated time in seconds
        """
        if num_sessions > 1:
            # Use same hands-per-session as the real run, but fewer sessions
            hands_per_session = total_hands // num_sessions
            cal_sessions = max(10, min(num_sessions, 50))
            cal_total = hands_per_session * cal_sessions

            start = time.perf_counter()
            self.run_simulation(cal_total, strategy_func, num_sessions=cal_sessions)
            elapsed = time.perf_counter() - start

            # Scale by number of sessions
            return elapsed * (num_sessions / cal_sessions)
        else:
            cal_total = calibration_hands

            start = time.perf_counter()
            self.run_simulation(cal_total, strategy_func, num_sessions=1)
            elapsed = time.perf_counter() - start

            return elapsed * (total_hands / cal_total)

    def compare_strategies(
        self,
        strategy_funcs: List[Callable[[Hand, Card], PlayerAction]],
        strategy_names: List[str],
        hands_per_strategy: int = 10000
    ) -> dict:
        """
        Compare multiple strategies.

        Args:
            strategy_funcs: List of strategy functions
            strategy_names: List of strategy names (same length as strategy_funcs)
            hands_per_strategy: Number of hands to test each strategy

        Returns:
            Dict mapping strategy names to SimulationResults
        """
        results = {}

        for func, name in zip(strategy_funcs, strategy_names):
            result = self.run_simulation(hands_per_strategy, func, num_sessions=1)
            results[name] = result

        return results
