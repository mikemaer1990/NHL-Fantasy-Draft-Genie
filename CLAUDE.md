# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

NHL Fantasy Draft Assistant is a single-page web application for conducting fantasy hockey drafts. It provides intelligent draft recommendations based on consensus rankings from multiple sources and real-time position scarcity analysis.

## Architecture

### Core Files
- **`index.html`** - Main application containing all HTML, CSS, and JavaScript
- **`consensus_player_data.json`** - Consolidated player rankings from 5 major fantasy sources
- **`ranking_consolidator.py`** - Python script to process and consolidate ranking data
- **`datasets/`** - Raw ranking data from ESPN, FantasyPros, Yahoo, NHL.com, and Hockey Handbook

### Data Processing Pipeline

```bash
# Regenerate consensus rankings from raw datasets
python ranking_consolidator.py
```

This processes all files in `datasets/` folder and outputs `consensus_player_data.json` with:
- Consensus rankings averaged across 5 sources
- Position corrections and dual-eligibility handling
- Metadata about sources and methodology

### Application Structure

**Frontend**: Pure HTML/CSS/JavaScript (no build system)
- Requires local file server for JSON loading
- Grid-based responsive layout
- Real-time search and filtering

**Data Model**:
```javascript
// Player object structure
{
  id: number,
  name: string,
  position: "C"|"LW"|"RW"|"D"|"G",
  team: string,
  overallRank: number,
  positionRank: number,
  espnPosition: string,
  dualEligible: boolean
}

// Roster configuration
roster = {
  C: [null, null, null],      // 3 centers
  LW: [null, null, null],     // 3 left wings
  RW: [null, null, null],     // 3 right wings
  D: [null, null, null, null, null], // 5 defensemen
  G: [null, null],            // 2 goalies
  BENCH: [null, null, null, null]    // 4 bench spots
}
```

## Key JavaScript Functions

### Data Management
- `loadPlayerData()` - Fetches and initializes player data
- `filterPlayers()` - Handles search functionality
- `updateDisplays()` - Refreshes all UI components

### Draft Logic
- `draftPlayer(playerId)` - Drafts player to team and assigns roster slot
- `assignToRoster(player)` - Handles roster position assignment logic
- `removePlayer(playerId)` - Undrafts player and updates availability

### Smart Recommendation System
- `generateDraftRecommendations()` - Core recommendation engine
- `getBalancedSmartRecommendations()` - Smart tab algorithm balancing value/scarcity
- `calculateValueScore(player)` - Value calculation considering rank and position scarcity
- `isPlayerElite(player)` - Determines if player is elite tier for their position
- `getUrgencyIndicator(player)` - Calculates draft urgency based on scarcity

### UI Management
- `switchTab(tabName)` - Handles tab navigation
- `updateTabContent()` - Updates active tab display
- `updatePositionTab(position)` - Filters players by position

### Value Algorithm Details

The smart recommendation system uses multi-factor scoring:

```javascript
// Base value calculation
const baseValue = 1000 - player.overallRank;

// Position scarcity multipliers
const positionScarcity = {
    'G': 1.8,   // Goalies most scarce
    'C': 1.4,   // Centers moderately scarce
    'D': 1.2,   // Defensemen slightly scarce
    'LW': 1.0,  // Wings baseline
    'RW': 1.0
};

// Elite player thresholds by position
const eliteThresholds = {
    'C': 20, 'LW': 20, 'RW': 20,
    'D': 30, 'G': 15
};
```

## Development Notes

### Position Handling
- Players have primary `position` and `espnPosition` fields
- `dualEligible` flag indicates multi-position flexibility
- Smart system considers both primary position and dual eligibility for recommendations

### Data Integrity
- Consensus data is pre-processed and validated
- All player IDs are unique integers
- Position abbreviations are standardized across sources

### UI State Management
- Global variables: `allPlayers`, `availablePlayers`, `myTeam`, `currentTab`
- No external state management - pure JavaScript
- Local state updates trigger cascade refreshes

### Common Tasks
- **Add new ranking source**: Update `ranking_consolidator.py` with new parser method
- **Modify roster config**: Update `roster` object and related validation functions
- **Adjust value algorithm**: Modify `calculateValueScore()` and scarcity multipliers
- **Add new position**: Update position arrays, thresholds, and validation logic

### Dual Eligible Player Logic
When filtering by position, the code handles both single positions and comma-separated lists:
```javascript
const eligiblePositions = player.espnPosition.includes(',') ?
    player.espnPosition.split(',').map(p => p.trim()) :
    [player.espnPosition];
```

### Grid Layout System
The tab navigation uses CSS Grid for equal distribution:
```css
.tab-nav {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
}
```

Always ensure `updateDisplays()` sets `display: 'grid'` to maintain layout consistency.