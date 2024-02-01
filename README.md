# Blockbot

Blockbot is a Discord bot, written in Python, that is maintained by the Redbrick Webgroup. This project uses [`hikari`](https://github.com/hikari-py/hikari/), an opinionated microframework, to interface with the Discord API. [`hikari-arc`](https://github.com/hypergonial/hikari-arc) is the command handler of choice.

## Resources

- [`hikari` Documentation](https://docs.hikari-py.dev/en/latest/)
- [`hikari-arc` Documentation](https://arc.hypergonial.com/)
- [Examples](https://github.com/hypergonial/hikari-arc/tree/main/examples/gateway)

## File Structure

- `bot.py`
  - This is the file that contains the bot configuration and instantiation, while also being responsible for loading the bot extensions.
- `extensions/`
  - This directory is home to the custom extensions (known as cogs in `discord.py`, or command groups) that are loaded when the bot is started. Extensions are classes that encapsulate command logic and can be dynamically loaded/unloaded. In `hikari-arc`, an intuitive [plugin system](https://arc.hypergonial.com/guides/plugins_extensions/) is used.
- `config.py`
  - Configuration secrets and important constants (such as identifiers) are stored here. The secrets are loaded from environment variables, so you can set them in your shell or in a `.env` file.
- `utils.py`
  - Simple utility functions are stored here, that can be reused across the codebase.

## Installation

### Discord Developer Portal

As a prerequisite, you need to have a bot application registered on the Discord developer portal.

1. Create a Discord bot application [here](https://discord.com/developers/applications/). 
2. When you have a bot application, register it for slash commands:
3. Go to *"OAuth2 > URL Generator"* on the left sidebar, select the `bot` and `applications.commands` scopes, scroll down & select the bot permissions you need (for development, you can select `Administator`).
4. Copy and visit the generated URL at the bottom of the page to invite it to the desired server.

#### Bot Token

- Go to the Discord developer portal and under *"Bot"* on the left sidebar, click `Reset Token`. Copy the generated token.

### Source Code
1. `git clone` and `cd` into this repository.
2. It's generally advised to work in a Python [virtual environment](https://docs.python.org/3/library/venv.html):
```sh
python3 -m venv .venv
source .venv/bin/activate
```
3. Create a new file called `.env` inside the repo folder and paste your bot token into the file as such:
```
TOKEN=<Discord bot token here>
```
4. Run `pip install -r requirements.txt` to install the required packages.
5. Once that's done, start the bot by running `python3 -m src`.

## FAQ

- If you get errors related to missing token environment variables, run `source .env`.
