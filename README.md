# 🏒 NHL Fantasy Draft Assistant

A smart, web-based fantasy hockey draft tool that provides intelligent player recommendations based on consensus rankings and real-time position scarcity analysis.

## ✨ Features

### 🎯 Smart Draft Recommendations
- **Position Scarcity Analysis**: Prioritizes goalies and defensemen when top forwards are drafted
- **Real-time Urgency Indicators**: Shows when elite players at scarce positions are running out
- **Consensus Rankings**: Combines data from 5 major fantasy sources (ESPN, FantasyPros, Yahoo, NHL.com, Hockey Handbook)

### 📊 Advanced Filtering & Views
- **Overall Rankings**: Top available players by consensus rank
- **Smart Tab**: Value-based recommendations balancing rank and scarcity
- **Position Tabs**: Filter by C, LW, RW, D, G with position-specific rankings
- **Real-time Search**: Instant player name filtering

### 🏆 Draft Management
- **Visual Roster Builder**: Drag-and-drop style roster management
- **Dual Position Support**: Handles players eligible for multiple positions
- **Undo Functionality**: Remove players or mark as "drafted by others"
- **Progress Tracking**: Visual indicators for roster completion

## 🚀 Quick Start

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Local web server (Python, Node.js, or any HTTP server)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mikemaer1990/NHL-Fantasy-Draft-Genie.git
   cd NHL-Fantasy-Draft-Genie
   ```

2. **Start a local web server**
   ```bash
   # Option 1: Python 3
   python -m http.server 8000

   # Option 2: Node.js (if you have http-server installed)
   npx http-server

   # Option 3: Any other local server
   ```

3. **Open in browser**
   ```
   http://localhost:8000
   ```

## 📈 Scoring System

The app is optimized for standard fantasy hockey scoring:

### Skaters
- **Goals**: 3 pts
- **Assists**: 2 pts
- **Plus/Minus**: 0.5 pts
- **Power Play Goals/Assists**: +1 pt bonus
- **Short Handed Goals**: +2 pts bonus
- **Hat Tricks**: +2 pts bonus
- **Hits**: 0.1 pts
- **Blocked Shots**: 0.3 pts

### Goalies
- **Wins**: 5 pts
- **Shutouts**: 5 pts
- **Overtime Losses**: 2.5 pts
- **Saves**: 0.1 pts each
- **Goals Against**: -0.5 pts

## 🧠 Smart Algorithm

### Position Scarcity Multipliers
```javascript
G: 4.0    // Goalies - Unique scoring, limited roster spots
D: 3.5    // Defense - Blocks/hits bonuses + fewer elite producers
LW: 3.0   // Left Wing - Rare elite talent at this position
C: 2.0    // Centers - High value but more depth available
RW: 1.5   // Right Wing - More elite options than LW
```

### Elite Player Thresholds
- **Goalies**: Top 6 (very limited elite options)
- **Left Wing**: Top 8 (scarcest skater position)
- **Defense**: Top 10 (limited fantasy producers)
- **Right Wing**: Top 12 (decent elite depth)
- **Centers**: Top 15 (most elite depth available)

### Draft Recommendation Logic
The algorithm calculates urgency scores based on:
1. **Remaining elite players** at each position
2. **Position scarcity multipliers**
3. **Current roster needs**
4. **Player quality** (elite vs non-elite)

## 📁 Project Structure

```
├── index.html              # Main application (HTML + CSS + JS)
├── consensus_player_data.json  # Consolidated player rankings
├── ranking_consolidator.py     # Data processing script
├── datasets/               # Raw ranking data
│   ├── espn_rankings.json
│   ├── fantasypros_rankings.json
│   ├── yahoo_rankings.json
│   ├── nhl_rankings.json
│   └── hockey_handbook_rankings.json
├── CLAUDE.md              # Development instructions
├── scoring.txt            # League scoring system
└── README.md              # This file
```

## 🔄 Updating Player Data

To refresh rankings with new data:

1. **Update source files** in the `datasets/` folder
2. **Run the consolidator**:
   ```bash
   python ranking_consolidator.py
   ```
3. **Refresh the browser** to load new data

## 🎮 Usage Tips

### During Your Draft
1. **Start with Overall tab** to see consensus top picks
2. **Switch to Smart tab** as top players get drafted
3. **Monitor recommendations panel** for position-specific urgency
4. **Use position tabs** when targeting specific roles
5. **Mark other teams' picks** to keep data current

### Reading the Interface
- **🔴 Elite G!** - Top-tier goalie available
- **🟠 Rare D!** - High-value defenseman
- **🟢 Top LW!** - Elite left winger (rare)
- **🔵 Elite C!** - Top center available
- **🟣 Elite RW!** - High-end right winger

- **GRAB NOW!** - Critical urgency (≤2 elite left)
- **Grab Soon!** - High urgency (≤4 elite left)
- **Consider** - Medium urgency (≤6 elite left)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🙏 Data Sources

Player rankings aggregated from:
- ESPN Fantasy Hockey
- FantasyPros
- Yahoo Fantasy Sports
- NHL.com
- Hockey Handbook

---

**Built for fantasy hockey enthusiasts who want data-driven draft decisions! 🏒📊**