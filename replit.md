# Luschin Casino Telegram Bot

## Overview
A Telegram casino bot built with aiogram (v3) that provides interactive games and collectible cards. The bot features slot machines, poker games, cookie surprises, and a collectible card system with prizes.

## Purpose
Entertainment bot that gamifies interaction through casino-style games and card collection mechanics. Users can play games, collect cards, and unlock rewards based on their wins.

## Current State
✅ **Fully configured and running** in Replit environment
- Bot is actively polling and responding to Telegram messages
- All dependencies installed
- User data persistence configured
- Card images available in the `cards/` directory

## Project Structure
```
.
├── study.py              # Main bot application file
├── requirements.txt      # Python dependencies (aiogram)
├── users.json           # Persistent user data (scores, collections, prizes)
├── cards/               # Directory with 33 collectible card images
├── start.sh             # Legacy start script (not used)
└── .gitignore           # Python project ignores
```

## Games & Features

### 🎰 Slot Machine (Слот із завозом)
Classic 3-reel slot game with emoji symbols

### 🃏 Poker with Walter (Покер із Волтером)
5-card poker game where users can replace cards and compete for combinations:
- Straight Flush (10 points)
- Four of a Kind (8 points)
- Full House (7 points)
- Flush (6 points)
- Straight (5 points)
- Three of a Kind (4 points)
- Two Pairs (3 points)
- Pair (2 points)

### 🍪 Cookie Surprise (Печеньковий сюрприз)
Fortune cookie-style game

### 📦 Card Packs
Users can open packs to collect cards (33 unique cards with rarities: common, medium, rare)

### 🗂 Collection
Track collected cards with rarity indicators

## Prize System
Progressive rewards based on total wins:
- 5 wins: Weekly subscription
- 10 wins: Pack of 3 cards
- 15 wins: Horror movie viewing
- 20-100 wins: Various card packs and special prizes

## Technical Details

### Dependencies
- **Python**: 3.11
- **aiogram**: 3.22.0 (Telegram Bot framework)
- **Additional**: aiofiles, aiohttp, pydantic

### Environment Variables
- `BOT_TOKEN`: Telegram bot token (required) - stored in Replit Secrets

### Data Persistence
User data stored in `users.json` includes:
- Points and wins tracking
- Card collections
- Prize history
- Awarded tier tracking
- Subscription status

### Workflow
- **Name**: Telegram Bot
- **Command**: `python study.py`
- **Type**: Console application (background service)
- **Status**: Running and polling

## How to Use

### For Users
1. Find the bot on Telegram: @studybtarukbot
2. Send `/start` to begin
3. Choose games from the main menu
4. Collect cards and unlock prizes

### For Developers
1. Bot automatically starts when Replit runs
2. View logs in the Replit console to monitor activity
3. User data persists across restarts in `users.json`
4. To add new cards: Add images to `cards/` directory and update `CARD_POOL` in `study.py`

## Recent Changes (October 22, 2025)
- ✅ Fixed corrupted `requirements.txt` file
- ✅ Installed Python 3.11 and aiogram dependency
- ✅ Configured BOT_TOKEN secret
- ✅ Set up Telegram Bot workflow (console mode)
- ✅ Created `.gitignore` for Python project
- ✅ Verified bot is running and polling successfully

## Notes
- This is a console application (no web interface)
- Bot runs continuously in the background
- All card images are already present in the `cards/` directory
- User interface is entirely through Telegram
