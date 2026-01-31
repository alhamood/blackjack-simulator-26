"""
Results reporting and export functionality.

Functions:
    export_summary_csv: Export overall simulation statistics to CSV
    export_sessions_csv: Export per-session statistics to CSV
    export_hands_csv: Export individual hand results to CSV
    export_to_json: Export simulation results to JSON
"""

import csv
import json
from pathlib import Path
from typing import List
from dataclasses import asdict
from src.simulator import SimulationResult, SessionResult
from src.game import GameResult


def export_summary_csv(result: SimulationResult, filepath: str) -> None:
    """
    Export overall simulation summary to CSV (single row).

    Args:
        result: SimulationResult to export
        filepath: Path to output CSV file
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'total_hands',
            'total_payout',
            'ev_per_hand',
            'ev_percent',
            'win_count',
            'loss_count',
            'push_count',
            'win_rate',
            'blackjack_count',
            'bust_count',
            'surrender_count',
            'double_count',
            'num_sessions',
            'session_ev_mean',
            'session_ev_stdev'
        ])

        # Data
        writer.writerow([
            result.total_hands,
            f'{result.total_payout:.2f}',
            f'{result.ev_per_hand:.6f}',
            f'{result.ev_per_hand * 100:.4f}',
            result.win_count,
            result.loss_count,
            result.push_count,
            f'{result.win_rate:.6f}',
            result.blackjack_count,
            result.bust_count,
            result.surrender_count,
            result.double_count,
            len(result.sessions),
            f'{result.session_ev_mean:.6f}' if result.sessions else '',
            f'{result.session_ev_stdev:.6f}' if len(result.sessions) > 1 else ''
        ])


def export_sessions_csv(result: SimulationResult, filepath: str) -> None:
    """
    Export per-session statistics to CSV (one row per session).

    Args:
        result: SimulationResult with session data
        filepath: Path to output CSV file
    """
    if not result.sessions:
        return

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'session_num',
            'hands_played',
            'total_payout',
            'ev_per_hand',
            'ev_percent',
            'win_count',
            'loss_count',
            'push_count',
            'win_rate',
            'blackjack_count',
            'bust_count',
            'surrender_count',
            'double_count'
        ])

        # Data rows
        for i, session in enumerate(result.sessions, start=1):
            writer.writerow([
                i,
                session.hands_played,
                f'{session.total_payout:.2f}',
                f'{session.ev_per_hand:.6f}',
                f'{session.ev_per_hand * 100:.4f}',
                session.win_count,
                session.loss_count,
                session.push_count,
                f'{session.win_rate:.6f}',
                session.blackjack_count,
                session.bust_count,
                session.surrender_count,
                session.double_count
            ])


def export_hands_csv(result: SimulationResult, filepath: str) -> None:
    """
    Export individual hand results to CSV.

    Exports hand-level data from the first session if available.
    Useful for spot-checking simulation results.

    Args:
        result: SimulationResult with tracked hand results
        filepath: Path to output CSV file
    """
    # Get hand results from first session
    if not result.sessions or not result.sessions[0].hand_results:
        return

    hands = result.sessions[0].hand_results
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'hand_num',
            'outcome',
            'player_value',
            'player_soft',
            'player_blackjack',
            'player_bust',
            'dealer_value',
            'dealer_soft',
            'dealer_blackjack',
            'dealer_bust',
            'bet',
            'payout'
        ])

        # Data rows
        for i, hand in enumerate(hands, start=1):
            writer.writerow([
                i,
                hand.outcome.name,
                hand.player_hand.value(),
                hand.player_hand.is_soft(),
                hand.player_hand.is_blackjack(),
                hand.player_hand.is_bust(),
                hand.dealer_hand.value(),
                hand.dealer_hand.is_soft(),
                hand.dealer_hand.is_blackjack(),
                hand.dealer_hand.is_bust(),
                f'{hand.bet:.2f}',
                f'{hand.payout:.2f}'
            ])


def export_all_csv(result: SimulationResult, base_path: str) -> dict:
    """
    Export all available data to CSV files.

    Creates up to three files:
    - {base_path}_summary.csv: Overall statistics (always)
    - {base_path}_sessions.csv: Per-session stats (if multi-session)
    - {base_path}_hands.csv: Sample of hands (if tracked)

    Args:
        result: SimulationResult to export
        base_path: Base path for output files (without extension)

    Returns:
        Dict with paths to created files
    """
    files_created = {}

    # Always create summary
    summary_path = f"{base_path}_summary.csv"
    export_summary_csv(result, summary_path)
    files_created['summary'] = summary_path

    # Create sessions file if multi-session
    if len(result.sessions) > 1:
        sessions_path = f"{base_path}_sessions.csv"
        export_sessions_csv(result, sessions_path)
        files_created['sessions'] = sessions_path

    # Create hands file if hand data is available
    if result.sessions and result.sessions[0].hand_results:
        hands_path = f"{base_path}_hands.csv"
        export_hands_csv(result, hands_path)
        files_created['hands'] = hands_path

    return files_created


def export_to_json(result: SimulationResult, filepath: str, include_hands: bool = False) -> None:
    """
    Export simulation results to JSON format.

    Useful for web API consumption or structured data interchange.

    Args:
        result: SimulationResult to export
        filepath: Path to output JSON file
        include_hands: If True, include individual hand results (can be large)
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    # Build JSON structure
    data = {
        'summary': {
            'total_hands': result.total_hands,
            'total_payout': round(result.total_payout, 2),
            'ev_per_hand': round(result.ev_per_hand, 6),
            'ev_percent': round(result.ev_per_hand * 100, 4),
            'win_count': result.win_count,
            'loss_count': result.loss_count,
            'push_count': result.push_count,
            'win_rate': round(result.win_rate, 6),
            'blackjack_count': result.blackjack_count,
            'bust_count': result.bust_count,
            'surrender_count': result.surrender_count,
            'double_count': result.double_count
        },
        'sessions': []
    }

    # Add session data
    for i, session in enumerate(result.sessions, start=1):
        session_data = {
            'session_num': i,
            'hands_played': session.hands_played,
            'total_payout': round(session.total_payout, 2),
            'ev_per_hand': round(session.ev_per_hand, 6),
            'ev_percent': round(session.ev_per_hand * 100, 4),
            'win_count': session.win_count,
            'loss_count': session.loss_count,
            'push_count': session.push_count,
            'win_rate': round(session.win_rate, 6),
            'blackjack_count': session.blackjack_count,
            'bust_count': session.bust_count,
            'surrender_count': session.surrender_count,
            'double_count': session.double_count
        }

        # Include hand data if requested
        if include_hands and session.hand_results:
            session_data['hands'] = [
                {
                    'outcome': hand.outcome.name,
                    'player_value': hand.player_hand.value(),
                    'player_soft': hand.player_hand.is_soft(),
                    'player_blackjack': hand.player_hand.is_blackjack(),
                    'dealer_value': hand.dealer_hand.value(),
                    'dealer_soft': hand.dealer_hand.is_soft(),
                    'dealer_blackjack': hand.dealer_hand.is_blackjack(),
                    'bet': round(hand.bet, 2),
                    'payout': round(hand.payout, 2)
                }
                for hand in session.hand_results
            ]

        data['sessions'].append(session_data)

    # Add session variance statistics if applicable
    if len(result.sessions) > 1:
        data['variance'] = {
            'session_ev_mean': round(result.session_ev_mean, 6),
            'session_ev_stdev': round(result.session_ev_stdev, 6)
        }

    # Write to file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
