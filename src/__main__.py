from hikari import Activity, ActivityType

from src.bot import bot

if __name__ == '__main__':
    bot.run(activity=Activity(name='Webgroup issues', type=ActivityType.WATCHING))
