"""Entrypoint script to load extensions and start the client."""
import hikari

from src.bot import bot

if __name__ == "__main__":
    bot.run(activity=hikari.Activity(name="Webgroup issues", type=hikari.ActivityType.WATCHING))
