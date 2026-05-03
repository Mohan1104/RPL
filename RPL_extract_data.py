"""
RPL Cricket Analytics - Data Extraction Pipeline
Extracts batting, bowling, and fielding stats from 15 PDFs (5 seasons × 3 categories)
and outputs clean JSON files for the website.
"""

import pdfplumber
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Canonical team name mapping ──────────────────────────────────────────────
TEAM_NAME_MAP = {
    "gully boys":                      "Gully Boyz",
    "gully boyz":                      "Gully Boyz",
    "rcb":                             "Ryland Challengers Birmingham",
    "ryland challengers birmingham":   "Ryland Challengers Birmingham",
    "rsk":                             "Ryland Super Kings",
    "ryland super kings":              "Ryland Super Kings",
    "ryland royals":                   "Ryland Royals",
    "ryland royals (rr)":              "Ryland Royals",
}

def normalize_team(raw):
    """Map any team name variant to its canonical form."""
    if not raw:
        return ""
    key = raw.strip().lower()
    # Try direct lookup first
    if key in TEAM_NAME_MAP:
        return TEAM_NAME_MAP[key]
    # Fuzzy fallback: check if key contains a known substring
    for pattern, canonical in TEAM_NAME_MAP.items():
        if pattern in key or key in pattern:
            return canonical
    return raw.strip()  # Return cleaned original if no match


def normalize_player(name):
    """Clean player name: strip whitespace, title-case, remove stray chars."""
    if not name:
        return ""
    name = str(name).strip()
    # Remove non-alpha characters except spaces
    name = re.sub(r'[^a-zA-Z\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()


def clean_numeric(val):
    """Convert a cell value to float, handling asterisks, blanks, template junk."""
    if val is None:
        return None
    s = str(val).strip()
    if not s or s == '-' or s.startswith('{{'):
        return None
    # Remove asterisks (e.g. "10*" → "10")
    s = s.replace('*', '')
    try:
        return float(s)
    except ValueError:
        return None


def clean_int(val):
    """Convert to int, or None."""
    f = clean_numeric(val)
    if f is None:
        return None
    return int(f)


# ── PDF Table Extraction ─────────────────────────────────────────────────────

def extract_table_rows(filepath):
    """Extract all data rows from a multi-page PDF table."""
    all_rows = []
    headers = None

    with pdfplumber.open(filepath) as pdf:
        for pi, page in enumerate(pdf.pages):
            table = page.extract_table()

            if not table:
                # Fallback: try raw text extraction (handles RPL2 page 2 case)
                text = page.extract_text()
                if text:
                    lines = text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        # Skip page footers and title lines
                        if not line or 'cricheroes' in line.lower() or 'RPL-' in line:
                            continue
                        # Try to parse as space-separated data
                        # Pattern: Rank PlayerName(s) TeamName(s) ... numeric fields
                        # We need headers to know how many trailing numeric fields
                        if headers:
                            parsed = parse_text_row(line, len(headers))
                            if parsed:
                                all_rows.append(parsed)
                continue

            for ri, row in enumerate(table):
                # Skip completely empty rows
                if not row or not any(cell and str(cell).strip() for cell in row if cell is not None):
                    continue

                # Detect header row
                first_cell = str(row[0]).strip() if row[0] else ''
                if first_cell.lower() == 'rank':
                    if headers is None:
                        headers = [str(c).replace('\n', ' ').strip() if c else None for c in row]
                    continue  # Skip header rows on any page

                # Skip rows that are single merged cells (RPL2 page 2 special case)
                non_none = [c for c in row if c is not None and str(c).strip()]
                if len(non_none) == 1 and headers and len(row) < len(headers):
                    # This is a merged cell, try to parse from text
                    text = str(non_none[0]).replace('\n', ' ').strip()
                    # Remove leading title like "RPL- Season 2"
                    text = re.sub(r'^RPL-\s*Season\s*\d+\s*', '', text).strip()
                    if text:
                        parsed = parse_text_row(text, len(headers))
                        if parsed:
                            all_rows.append(parsed)
                    continue

                all_rows.append(row)

    return headers, all_rows


def parse_text_row(text, num_cols):
    """
    Parse a text row like '34 Aakash Borhade Gully Boyz RHB 3 3 1 12 1 0 0.33 8.33 0 0 0 0'
    into a list of the correct number of columns.
    """
    # Known team name tokens for splitting
    team_tokens = [
        'Gully Boyz', 'Gully Boys',
        'Ryland Challengers Birmingham', 'Ryland challengers Birmingham',
        'Ryland Super Kings', 'Ryland Royals', 'Ryland Royals (RR)',
        'RCB', 'RSK',
    ]

    for team in sorted(team_tokens, key=len, reverse=True):
        if team in text:
            idx = text.index(team)
            before = text[:idx].strip()
            after = text[idx + len(team):].strip()

            # Before = "Rank PlayerName" 
            before_parts = before.rsplit(' ', 1) if ' ' in before else [before]
            # For batting: before is "34 Aakash Borhade" → rank + player name
            # Split on first space to get rank, rest is player name
            rank_match = re.match(r'^(\d+)\s+(.+)$', before)
            if rank_match:
                rank = rank_match.group(1)
                player = rank_match.group(2)
            else:
                rank = ''
                player = before

            # After = remaining fields separated by spaces
            after_parts = after.split()
            
            # Build the row
            row = [rank, player, team] + after_parts
            
            # Pad or trim to match expected columns
            while len(row) < num_cols:
                row.append(None)
            return row[:num_cols]

    return None


# ── Category-Specific Parsers ────────────────────────────────────────────────

def parse_batting(headers, rows, season):
    """Parse batting data into clean dicts."""
    records = []
    for row in rows:
        if len(row) < 7:
            continue
        player = normalize_player(row[1])
        if not player:
            continue
        
        record = {
            'player':      player,
            'team':        normalize_team(row[2]),
            'season':      season,
            'bat_hand':    str(row[3]).strip() if row[3] else '',
            'matches':     clean_int(row[4]),
            'innings':     clean_int(row[5]),
            'runs':        clean_int(row[6]),
            'balls':       clean_int(row[7]) if len(row) > 7 else None,
            'highest':     clean_int(row[8]) if len(row) > 8 else None,
            'not_outs':    clean_int(row[9]) if len(row) > 9 else None,
            'average':     clean_numeric(row[10]) if len(row) > 10 else None,
            'strike_rate': clean_numeric(row[11]) if len(row) > 11 else None,
            'fours':       clean_int(row[12]) if len(row) > 12 else None,
            'sixes':       clean_int(row[13]) if len(row) > 13 else None,
            'fifties':     clean_int(row[14]) if len(row) > 14 else None,
            'hundreds':    clean_int(row[15]) if len(row) > 15 else None,
        }
        records.append(record)
    return records


def parse_bowling(headers, rows, season):
    """Parse bowling data into clean dicts."""
    records = []
    for row in rows:
        if len(row) < 7:
            continue
        player = normalize_player(row[1])
        if not player:
            continue

        record = {
            'player':       player,
            'team':         normalize_team(row[2]),
            'season':       season,
            'bowl_style':   str(row[3]).strip() if row[3] else '',
            'matches':      clean_int(row[4]),
            'innings':      clean_int(row[5]),
            'overs':        clean_numeric(row[6]),
            'runs':         clean_int(row[7]) if len(row) > 7 else None,
            'wickets':      clean_int(row[8]) if len(row) > 8 else None,
            'best_figures': clean_int(row[9]) if len(row) > 9 else None,
            'maidens':      clean_int(row[10]) if len(row) > 10 else None,
            'average':      clean_numeric(row[11]) if len(row) > 11 else None,
            'economy':      clean_numeric(row[12]) if len(row) > 12 else None,
            'strike_rate':  clean_numeric(row[13]) if len(row) > 13 else None,
        }
        records.append(record)
    return records


def parse_fielding(headers, rows, season):
    """Parse fielding data into clean dicts. Drop template-placeholder columns."""
    records = []
    for row in rows:
        if len(row) < 5:
            continue
        player = normalize_player(row[1])
        if not player:
            continue

        record = {
            'player':        player,
            'team':          normalize_team(row[2]),
            'season':        season,
            'matches':       clean_int(row[3]),
            'dismissals':    clean_int(row[4]),
            'catches':       clean_int(row[5]) if len(row) > 5 else None,
            'caught_bowled': clean_int(row[6]) if len(row) > 6 else None,
            'caught_behind': clean_int(row[7]) if len(row) > 7 else None,
            'run_outs':      clean_int(row[8]) if len(row) > 8 else None,
            'assist_runouts':clean_int(row[9]) if len(row) > 9 else None,
            'stumpings':     clean_int(row[10]) if len(row) > 10 else None,
            # Columns 11+ are {{template}} placeholders — intentionally skipped
        }
        records.append(record)
    return records


# ── Main Pipeline ────────────────────────────────────────────────────────────

def main():
    batting_all = []
    bowling_all = []
    fielding_all = []

    for season in range(1, 6):
        # ── Batting ──
        fpath = os.path.join(BASE_DIR, f"Batting Leaderboard RPL{season}.pdf")
        headers, rows = extract_table_rows(fpath)
        records = parse_batting(headers, rows, season)
        print(f"Season {season} Batting:  {len(records)} players")
        batting_all.extend(records)

        # ── Bowling ──
        fpath = os.path.join(BASE_DIR, f"Bowling Leaderboard RPL{season}.pdf")
        headers, rows = extract_table_rows(fpath)
        records = parse_bowling(headers, rows, season)
        print(f"Season {season} Bowling:  {len(records)} players")
        bowling_all.extend(records)

        # ── Fielding ──
        fpath = os.path.join(BASE_DIR, f"Fielding Leaderboard RPL{season}.pdf")
        headers, rows = extract_table_rows(fpath)
        records = parse_fielding(headers, rows, season)
        print(f"Season {season} Fielding: {len(records)} players")
        fielding_all.extend(records)

    # ── Verify team name normalization ──
    all_teams = set()
    for r in batting_all + bowling_all + fielding_all:
        all_teams.add(r['team'])
    print(f"\nCanonical teams: {sorted(all_teams)}")

    # ── Verify no duplicate player names from normalization ──
    all_players = set()
    for r in batting_all + bowling_all + fielding_all:
        all_players.add(r['player'])
    print(f"Unique players: {len(all_players)}")

    # ── Write JSON ──
    out_dir = os.path.join(BASE_DIR, 'data')
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'batting.json'), 'w') as f:
        json.dump(batting_all, f, indent=2)
    with open(os.path.join(out_dir, 'bowling.json'), 'w') as f:
        json.dump(bowling_all, f, indent=2)
    with open(os.path.join(out_dir, 'fielding.json'), 'w') as f:
        json.dump(fielding_all, f, indent=2)

    # ── Build unified player index ──
    player_index = {}
    for r in batting_all:
        p = r['player']
        if p not in player_index:
            player_index[p] = {'name': p, 'teams': set(), 'seasons': set()}
        player_index[p]['teams'].add(r['team'])
        player_index[p]['seasons'].add(r['season'])
    for r in bowling_all:
        p = r['player']
        if p not in player_index:
            player_index[p] = {'name': p, 'teams': set(), 'seasons': set()}
        player_index[p]['teams'].add(r['team'])
        player_index[p]['seasons'].add(r['season'])
    for r in fielding_all:
        p = r['player']
        if p not in player_index:
            player_index[p] = {'name': p, 'teams': set(), 'seasons': set()}
        player_index[p]['teams'].add(r['team'])
        player_index[p]['seasons'].add(r['season'])

    # Convert sets to sorted lists for JSON
    players_list = []
    for p in sorted(player_index.values(), key=lambda x: x['name']):
        players_list.append({
            'name': p['name'],
            'teams': sorted(p['teams']),
            'seasons': sorted(p['seasons']),
        })

    with open(os.path.join(out_dir, 'players.json'), 'w') as f:
        json.dump(players_list, f, indent=2)

    print(f"\nData written to {out_dir}/")
    print(f"   batting.json:  {len(batting_all)} records")
    print(f"   bowling.json:  {len(bowling_all)} records")
    print(f"   fielding.json: {len(fielding_all)} records")
    print(f"   players.json:  {len(players_list)} players")


if __name__ == '__main__':
    main()
