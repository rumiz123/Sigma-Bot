import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os

COINS_FILE = "economy.json"

class Gamble(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.load_data()

    def load_data(self):
        if os.path.exists(COINS_FILE):
            with open(COINS_FILE, "r") as f:
                content = f.read().strip()
                self.economy_data = json.loads(content) if content else {}
        else:
            self.economy_data = {}

    def save_data(self):
        with open(COINS_FILE, "w") as f:
            json.dump(self.economy_data, f, indent=4)

    def get_user_data(self, user_id):
        user_id = str(user_id)
        if user_id not in self.economy_data:
            self.economy_data[user_id] = {"coins": 0, "bank": 0}
        return self.economy_data[user_id]

    @app_commands.command(name="coinflip", description="Bet your coins on a coin flip")
    async def coinflip(self, interaction: discord.Interaction, bet: int, choice: str):
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)

        if bet <= 0:
            await interaction.response.send_message("❌ You must bet a positive amount of coins.")
            return

        if user_data["coins"] < bet:
            await interaction.response.send_message("❌ You don't have enough coins to place this bet.")
            return

        choice = choice.lower()
        if choice not in ["heads", "tails"]:
            await interaction.response.send_message("❌ Invalid choice! Choose 'Heads' or 'Tails'.")
            return

        result = random.choice(["heads", "tails"])
        if choice == result:
            winnings = bet * 2
            user_data["coins"] += winnings
            await interaction.response.send_message(f"🎉 The coin landed on **{result}**! You won **${winnings}**!")
        else:
            user_data["coins"] -= bet
            await interaction.response.send_message(f"😢 The coin landed on **{result}**. You lost **${bet}**.")
        
        self.save_data()

    @app_commands.command(name="dice", description="Bet on a dice roll (1-6)")
    async def dice(self, interaction: discord.Interaction, bet: int, guess: int):
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)

        if bet <= 0:
            await interaction.response.send_message("❌ You must bet a positive amount of coins.")
            return

        if user_data["coins"] < bet:
            await interaction.response.send_message("❌ You don't have enough coins to place this bet.")
            return

        if guess < 1 or guess > 6:
            await interaction.response.send_message("❌ Invalid guess! Choose a number between 1 and 6.")
            return

        roll = random.randint(1, 6)
        if guess == roll:
            winnings = bet * 6
            user_data["coins"] += winnings
            await interaction.response.send_message(f"🎲 The dice rolled **{roll}**! You won **${winnings}**!")
        else:
            user_data["coins"] -= bet
            await interaction.response.send_message(f"😢 The dice rolled **{roll}**. You lost **${bet}**.")
        
        self.save_data()

    @app_commands.command(name="guess", description="Play the guessing game with coins")
    async def guess(self, interaction: discord.Interaction, bet: int):
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)

        if bet <= 0:
            await interaction.response.send_message("❌ You must bet a positive amount of coins.")
            return

        if user_data["coins"] < bet:
            await interaction.response.send_message("❌ You don't have enough coins to place this bet.")
            return

        number = random.randint(1, 10)
        await interaction.response.send_message(f"Guess a number between 1 and 10! Bet: ${bet}. Type your guess in the chat.")

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel and msg.content.isdigit()

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=15)
            guess = int(msg.content)

            if guess == number:
                winnings = bet * 2
                user_data["coins"] += winnings
                await interaction.followup.send(f"🎉 Correct! The number was {number}. You won **${winnings}**!")
            else:
                user_data["coins"] -= bet
                await interaction.followup.send(f"❌ Wrong! The correct number was {number}. You lost **${bet}**.")
        except:
            await interaction.followup.send("⏳ Time's up! You didn't guess in time. You lost your bet.")
        
        self.save_data()

    @app_commands.command(name="rockpaperscissors", description="Play rock-paper-scissors with coins")
    async def rps(self, interaction: discord.Interaction, bet: int, choice: str):
        user_id = str(interaction.user.id)
        user_data = self.get_user_data(user_id)

        if bet <= 0:
            await interaction.response.send_message("❌ You must bet a positive amount of coins.")
            return

        if user_data["coins"] < bet:
            await interaction.response.send_message("❌ You don't have enough coins to place this bet.")
            return

        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        if choice.lower() not in choices:
            await interaction.response.send_message("Invalid choice! Choose rock, paper, or scissors.")
            return

        result = "You win!" if (
                (choice == "rock" and bot_choice == "scissors") or
                (choice == "paper" and bot_choice == "rock") or
                (choice == "scissors" and bot_choice == "paper")
        ) else "You lose!" if choice != bot_choice else "It's a tie!"

        if result == "You win!":
            winnings = bet * 2
            user_data["coins"] += winnings
            await interaction.response.send_message(f"You chose {choice}, I chose {bot_choice}. {result} You won **${winnings}**!")
        elif result == "You lose!":
            user_data["coins"] -= bet
            await interaction.response.send_message(f"You chose {choice}, I chose {bot_choice}. {result} You lost **${bet}**.")
        else:  # It's a tie
            await interaction.response.send_message(f"You chose {choice}, I chose {bot_choice}. {result}. Your bet of **${bet}** is returned.")
        
        self.save_data()

async def setup(bot: commands.Bot):
    await bot.add_cog(Gamble(bot))