import discord
import asyncio
from discord.ext import commands, tasks
from discord.utils import get
import os
import random
import chess
import chess.engine
import random
import stockfish

current_dir = os.getcwd()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents) # Bot Prefix goes here
token = '' # Bot token goes here or however you store the token of the bot

games = ['Chess', 'Neural Engine'] # Random Bot Activity
ongoing_games = {}  # Dictionary to store ongoing game contexts

async def change_activity():
    while True:
        game = random.choice(games)
        await bot.change_presence(activity=discord.Game(name=game))
        await asyncio.sleep(12 * 60 * 60) 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

# Main Command
@bot.command()
async def sfplay(ctx):
    engine = stockfish.Stockfish('path/to/stockfish') # Path to Stockfish (Powerful Chess Engine). Stockfish 15.1 https://stockfishchess.org/. 64-bit Windows is recommend.
    await ctx.send("Do you want to play as black or white? (Type 'black' or 'white')")
    message = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
    color = message.content.lower()

    if color == 'black':
        player_color = chess.BLACK
    elif color == 'white':
        player_color = chess.WHITE
    else:
        await ctx.send("Invalid color. Please choose 'black' or 'white'.")
        return

    board = chess.Board()

    while not board.is_game_over():
        if board.turn == player_color:
            await ctx.send(f"Current board:\n```\n{board}\n```")
            await ctx.send("Your move (e.g., 'e2e4, g1f3, f1b5', 'quit' to end the game):")
            message = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            move_str = message.content.lower()

            if move_str == 'quit':
                await ctx.send("Game ended. You quit the game.")
                del ongoing_games[ctx.author.id]  # Remove the ongoing game context
                return

            try:
                move = chess.Move.from_uci(move_str)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    await ctx.send("Invalid move.")
            except ValueError:
                await ctx.send("Invalid move.")
        else:
            engine.set_fen_position(board.fen())
            best_move = engine.get_best_move()
            board.push(chess.Move.from_uci(best_move))
            await ctx.send(f"Bot's move: {best_move}")

    await ctx.send("Game over. Result: " + board.result())
    del ongoing_games[ctx.author.id] 


@bot.command()
async def sfquit(ctx):
    if ctx.author.id in ongoing_games:
        del ongoing_games[ctx.author.id]
        await ctx.send("Game ended. You quit the game.")
    else:
        await ctx.send("There is no ongoing game for you.")

bot.run(token)