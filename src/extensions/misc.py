import arc
from src.models import Blockbot, BlockbotContext, BlockbotPlugin

plugin = BlockbotPlugin(name="Misc")

plugin.load_commands_from("./src/misc")

@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)