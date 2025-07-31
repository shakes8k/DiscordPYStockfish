# DiscordPYStockfish
A Simple Discord.py bot source that plays chess via Stockfish 15.1 (https://stockfishchess.org/). Interactive with users.
# How To Use?
1. Install requirements.txt ("pip install -r requirements.txt") Remember to chose the path correctly.
3. Insert Your Discord.PY Bot Prefix.
4. Download Stockfish 64-Bit (https://stockfishchess.org/download/windows/).
5. Add Path/To/Stockfish to the designated place where Stockfish is downloaded.
# What's special?
- **parsemove.py** provides a robust utility for interpreting chess moves written in a variety of human-friendly formats. This script supports standard UCI notation (e2e4), long algebraic (e2-e4), short algebraic (e4), and even natural language-like commands (e.g., "pawn to e4" or "knight e5"). It seamlessly maps these inputs to valid moves on a given python-chess board, enabling flexible move parsing without the need for any AI integration. Ideal for user-driven chess applications where move input format may vary.
