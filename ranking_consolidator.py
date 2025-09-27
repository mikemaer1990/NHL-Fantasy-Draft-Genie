#!/usr/bin/env python3
"""
NHL Fantasy Rankings Consolidator
Parses multiple ranking sources and creates a consensus ranking JSON file.
"""

import csv
import json
import re
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

class RankingParser:
    def __init__(self):
        self.position_map = {
            'C': 'C',
            'LW': 'LW',
            'RW': 'RW',
            'D': 'D',
            'G': 'G',
            'F': 'F'  # Forward (C/LW/RW eligible)
        }

        self.team_abbreviations = {
            'ANA': 'ANA', 'BOS': 'BOS', 'BUF': 'BUF', 'CAR': 'CAR', 'CBJ': 'CBJ',
            'CGY': 'CGY', 'CHI': 'CHI', 'COL': 'COL', 'DAL': 'DAL', 'DET': 'DET',
            'EDM': 'EDM', 'FLA': 'FLA', 'LAK': 'LAK', 'MIN': 'MIN', 'MTL': 'MTL',
            'NJ': 'NJ', 'NSH': 'NSH', 'NYI': 'NYI', 'NYR': 'NYR', 'OTT': 'OTT',
            'PHI': 'PHI', 'PIT': 'PIT', 'SEA': 'SEA', 'SJ': 'SJ', 'STL': 'STL',
            'TB': 'TB', 'TOR': 'TOR', 'UTA': 'UTA', 'VAN': 'VAN', 'VGK': 'VGK',
            'WPG': 'WPG', 'WSH': 'WSH',
            # Alternative names
            'TBL': 'TB', 'SJS': 'SJ', 'LAK': 'LAK', 'LAS': 'VGK', 'Wpg': 'WPG',
            'Tor': 'TOR', 'Edm': 'EDM', 'Col': 'COL', 'Bos': 'BOS', 'Ott': 'OTT',
            'Nsh': 'NSH', 'Dal': 'DAL'
        }

    def normalize_name(self, name: str) -> str:
        """Normalize player name for matching across sources."""
        # Remove extra whitespace and convert to title case
        name = ' '.join(name.strip().split())
        # Handle some common variations
        name = name.replace('Jr.', 'Jr').replace('Sr.', 'Sr')
        return name

    def parse_fantasyprops_csv(self, filepath: str) -> List[Dict]:
        """Parse FantasyPros CSV files."""
        players = []

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = self.normalize_name(row['PLAYER NAME'])
                team = self.team_abbreviations.get(row['TEAM'], row['TEAM'])

                # Extract position from filename
                filename = os.path.basename(filepath)
                if '_C_' in filename:
                    position = 'C'
                elif '_LW_' in filename:
                    position = 'LW'
                elif '_RW_' in filename:
                    position = 'RW'
                elif '_D_' in filename:
                    position = 'D'
                elif '_G_' in filename:
                    position = 'G'
                else:
                    position = 'F'

                players.append({
                    'name': name,
                    'team': team,
                    'position': position,
                    'overall_rank': int(row['RK']),
                    'position_rank': int(row['RK']),
                    'multi_position': position == 'F'
                })

        return players

    def parse_espn_text(self, filepath: str) -> List[Dict]:
        """Parse ESPN format: '1. Nathan MacKinnon, Col (C1)'"""
        players = []

        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                # Pattern: "1. Nathan MacKinnon, Col (C1)"
                match = re.match(r'(\d+)\.\s+([^,]+),\s+(\w+)\s+\(([A-Z]+)(\d+)\)', line)
                if match:
                    overall_rank = int(match.group(1))
                    name = self.normalize_name(match.group(2))
                    team = self.team_abbreviations.get(match.group(3), match.group(3))
                    position = match.group(4)
                    position_rank = int(match.group(5))

                    players.append({
                        'name': name,
                        'team': team,
                        'position': position,
                        'overall_rank': overall_rank,
                        'position_rank': position_rank,
                        'multi_position': position == 'F'
                    })

        return players

    def parse_yahoo_text(self, filepath: str) -> List[Dict]:
        """Parse Yahoo format (complex table)."""
        players = []

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        overall_rank = 1

        while i < len(lines):
            line = lines[i].strip()

            # Look for player name pattern (skip Photo lines)
            if line and not line.startswith('Photo') and not line.startswith('Player'):
                # Check if this looks like a player name
                if not re.match(r'^\d+$', line) and not re.match(r'^\d+%$', line) and not re.match(r'^\d+\.\d+$', line):
                    name = self.normalize_name(line)

                    # Look for team/position in next few lines
                    team = None
                    position = None

                    for j in range(i+1, min(i+5, len(lines))):
                        next_line = lines[j].strip()
                        # Pattern: "EDM - C" or similar
                        team_pos_match = re.match(r'([A-Z]{2,3})\s*-\s*([A-Z]+)', next_line)
                        if team_pos_match:
                            team = self.team_abbreviations.get(team_pos_match.group(1), team_pos_match.group(1))
                            position = team_pos_match.group(2)
                            break

                    if team and position:
                        # Determine position rank (simplified)
                        position_rank = overall_rank  # We'll calculate this properly later

                        players.append({
                            'name': name,
                            'team': team,
                            'position': position,
                            'overall_rank': overall_rank,
                            'position_rank': position_rank,
                            'multi_position': position in ['C', 'LW', 'RW']  # Yahoo allows multi-position
                        })

                        overall_rank += 1

            i += 1

        return players

    def parse_nhl_text(self, filepath: str) -> List[Dict]:
        """Parse NHL.com format: '1. Nathan MacKinnon, F, COL'"""
        players = []

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Pattern: "1. Nathan MacKinnon, F, COL"
                match = re.match(r'(\d+)\.\s+([^,]+),\s+([A-Z]+),\s+(\w+)', line)
                if match:
                    overall_rank = int(match.group(1))
                    name = self.normalize_name(match.group(2))
                    position = match.group(3)
                    team = self.team_abbreviations.get(match.group(4), match.group(4))

                    players.append({
                        'name': name,
                        'team': team,
                        'position': position,
                        'overall_rank': overall_rank,
                        'position_rank': overall_rank,  # Will calculate properly later
                        'multi_position': position == 'F'
                    })

        return players

    def parse_hh_text(self, filepath: str) -> List[Dict]:
        """Parse Hockey Handbook format (table with stats)."""
        players = []

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for lines starting with rank number and containing player info
            parts = line.split('\t')
            if len(parts) >= 4 and parts[0].isdigit():
                try:
                    overall_rank = int(parts[0])
                    name = self.normalize_name(parts[1])
                    position = parts[2]
                    team = self.team_abbreviations.get(parts[3], parts[3])

                    players.append({
                        'name': name,
                        'team': team,
                        'position': position,
                        'overall_rank': overall_rank,
                        'position_rank': overall_rank,  # Will calculate properly later
                        'multi_position': position == 'F'
                    })
                except (ValueError, IndexError):
                    continue

        return players

    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse a ranking file based on its format."""
        filename = os.path.basename(filepath).lower()

        if filepath.endswith('.csv'):
            return self.parse_fantasyprops_csv(filepath)
        elif 'espn' in filename:
            return self.parse_espn_text(filepath)
        elif 'yahoo' in filename:
            return self.parse_yahoo_text(filepath)
        elif 'nhl' in filename:
            return self.parse_nhl_text(filepath)
        elif 'hh' in filename:
            return self.parse_hh_text(filepath)
        else:
            print(f"Unknown format for file: {filepath}")
            return []

    def calculate_position_ranks(self, players: List[Dict]) -> List[Dict]:
        """Calculate position ranks."""
        # Group by position
        by_position = defaultdict(list)

        for player in players:
            by_position[player['position']].append(player)

        # Sort and assign position ranks
        for position, position_players in by_position.items():
            position_players.sort(key=lambda x: x['overall_rank'])
            for i, player in enumerate(position_players, 1):
                player['position_rank'] = i

        return players

    def create_consensus_ranking(self, all_players: List[Dict]) -> List[Dict]:
        """Create consensus ranking from all sources."""
        # Group players by normalized name
        player_groups = defaultdict(list)

        for player in all_players:
            player_groups[player['name']].append(player)

        consensus_players = []

        for name, players in player_groups.items():
            if not players:
                continue

            # Use the most common values for team/position
            teams = [p['team'] for p in players if p['team']]
            positions = [p['position'] for p in players if p['position']]

            most_common_team = max(set(teams), key=teams.count) if teams else 'UNK'
            most_common_position = max(set(positions), key=positions.count) if positions else 'F'

            # Calculate average rankings
            overall_ranks = [p['overall_rank'] for p in players if p['overall_rank']]
            position_ranks = [p['position_rank'] for p in players if p['position_rank']]

            avg_overall = sum(overall_ranks) / len(overall_ranks) if overall_ranks else 999
            avg_position = sum(position_ranks) / len(position_ranks) if position_ranks else 999

            # Check for multi-position eligibility
            multi_position = any(p['multi_position'] for p in players)

            consensus_players.append({
                'name': name,
                'team': most_common_team,
                'position': most_common_position,
                'multi_position_eligible': multi_position,
                'overall_rank': round(avg_overall, 1),
                'position_rank': round(avg_position, 1)
            })

        # Sort by average overall rank
        consensus_players.sort(key=lambda x: x['overall_rank'])

        # Assign final consensus ranks
        for i, player in enumerate(consensus_players, 1):
            player['consensus_overall_rank'] = i

        # Assign consensus position ranks
        by_position = defaultdict(list)
        for player in consensus_players:
            by_position[player['position']].append(player)

        for position, pos_players in by_position.items():
            pos_players.sort(key=lambda x: x['overall_rank'])
            for i, player in enumerate(pos_players, 1):
                player['consensus_position_rank'] = i

        return consensus_players

def main():
    parser = RankingParser()
    datasets_dir = 'datasets'

    all_players = []

    # Parse all files in datasets directory
    for filename in os.listdir(datasets_dir):
        filepath = os.path.join(datasets_dir, filename)
        if os.path.isfile(filepath):
            print(f"Parsing {filename}...")
            players = parser.parse_file(filepath)
            print(f"  Found {len(players)} players")
            all_players.extend(players)

    print(f"\nTotal players parsed: {len(all_players)}")

    # Calculate position ranks
    all_players = parser.calculate_position_ranks(all_players)

    # Create consensus ranking
    consensus_players = parser.create_consensus_ranking(all_players)

    print(f"Consensus players: {len(consensus_players)}")

    # Output to JSON
    output_data = {
        'metadata': {
            'generated_date': '2025-09-27',
            'total_players': len(consensus_players)
        },
        'players': consensus_players
    }

    with open('consensus_rankings.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\nConsensus rankings saved to consensus_rankings.json")

    # Print top 20 for preview
    print("\nTop 20 Consensus Rankings:")
    print("Rank | Name | Team | Pos | Overall")
    print("-" * 50)
    for player in consensus_players[:20]:
        print(f"{player['consensus_overall_rank']:4d} | {player['name']:<20} | {player['team']:<3} | {player['position']:<2} | {player['overall_rank']:8.1f}")

if __name__ == "__main__":
    main()