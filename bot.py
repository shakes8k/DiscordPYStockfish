import discord
import asyncio
from discord.ext import commands, tasks
from discord.utils import get
import sqlite3
import os
import random
from PIL import Image, ImageDraw
import chess
import chess.engine
import random
import stockfish
from io import BytesIO

current_dir = os.path.dirname(os.path.abspath(__file__))
pieces_dir = os.path.join(current_dir, 'pieces')
database_file = os.path.join(current_dir, 'games.db')
intents = discord.Intents.default()
intents.message_content = True

async def create_database():
    conn = sqlite3.connect(database_file)
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS ongoing_games (
                    player_id INTEGER PRIMARY KEY,
                    game TEXT,
                    moves TEXT
                )''')

    conn.commit()
    conn.close()

# Call create_database function to ensure the table exists
asyncio.run(create_database())

bot = commands.Bot(command_prefix='', intents=intents) # Insert Preferred Bot Prefix
token = '' # Insert Bot Token or however you handle the bot Token

games = ['Chess', 'With Neural Engine']

async def change_activity():
    while True:
        game = random.choice(games)
        await bot.change_presence(activity=discord.Game(name=game))
        await asyncio.sleep(12 * 60 * 60) # 12 hours

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command()
async def sfplay(ctx):
    engine = stockfish.Stockfish('') # Path to Stockfish (Powerful Chess Engine). Stockfish 15.1 https://stockfishchess.org/. 64-bit Windows is recommend.
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
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute("INSERT INTO ongoing_games (player_id, game, moves) VALUES (?, ?, ?)", (ctx.author.id, 'Chess', str(board)))
    conn.commit()
    conn.close()

    while not board.is_game_over():
        if board.turn == player_color:
            await ctx.send(f"Current board:\n")
            await send_board_image(ctx, board)  # Send board as an image

            # Check for stalemate
            if board.is_stalemate():
                await ctx.send("Stalemate. The game is a draw.")
                return

            # Check for checkmate
            if board.is_checkmate():
                await ctx.send("Checkmate.")
                return

            await ctx.send("Your move (e.g., 'e2e4, g1f3, f1b5', 'quit' to end the game):")
            message = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            move_str = message.content.lower()

            if move_str == 'quit':
                conn = sqlite3.connect(database_file)
                c = conn.cursor()
                c.execute("DELETE FROM ongoing_games WHERE player_id = ?", (ctx.author.id,))
                conn.commit()
                conn.close()
                await ctx.send("Game ended. You quit the game.")
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

        # Check for stalemate
        if board.is_stalemate():
            await ctx.send("Stalemate. The game is a draw.")
            return

        # Check for checkmate
        if board.is_checkmate():
            await ctx.send("Checkmate.")
            return
    
    # Game completed, delete the ongoing game from the database
    conn = sqlite3.connect(database_file)
    c = conn.cursor()
    c.execute("DELETE FROM ongoing_games WHERE player_id = ?", (ctx.author.id,))
    conn.commit()
    conn.close()
    await ctx.send("Game over. Result: " + board.result())


async def send_board_image(ctx, board):
    # Create a blank image for the board
    square_size = 100  # Size of each square in pixels
    image_size = 8 * square_size
    image = Image.new('RGBA', (image_size, image_size))
    draw = ImageDraw.Draw(image)

    # Define colors for the light and dark squares
    light_square_color = (240, 217, 181, 255)
    dark_square_color = (181, 136, 99, 255)

    # Draw the squares and pieces on the board
    for rank in range(8):
        for file in range(8):
            x1 = file * square_size
            y1 = rank * square_size
            x2 = x1 + square_size
            y2 = y1 + square_size

            square_color = light_square_color if (file + rank) % 2 == 0 else dark_square_color
            draw.rectangle([(x1, y1), (x2, y2)], fill=square_color)

            piece = board.piece_at(chess.square(file, 7 - rank))
            if piece is not None:
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_name = piece.symbol().lower()
                piece_path = os.path.join(pieces_dir, f'{piece_color}{piece_name}.png')
                if os.path.exists(piece_path):
                    piece_image = Image.open(piece_path).convert("RGBA")
                    piece_image = piece_image.resize((square_size, square_size))
                    image.paste(piece_image, (x1, y1), mask=piece_image)

    # Save the image as a temporary file
    temp_image_path = os.path.join(current_dir, 'temp_board.png')
    image.save(temp_image_path)

    # Send the image as a message
    with open(temp_image_path, 'rb') as fp:
        file = discord.File(fp, 'board.png')
        await ctx.send(file=file)

    # Delete the temporary image file
    os.remove(temp_image_path)

bot.run(token)
