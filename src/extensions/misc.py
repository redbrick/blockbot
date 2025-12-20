from src.models import Blockbot, BlockbotPlugin
import arc

plugin = BlockbotPlugin(name="misc")

from ..misc.copypasta import *
from ..misc.dig import *
from ..misc.fortune import *
from ..misc.gerry import *
from ..misc.figlet import *

@arc.loader
def loader(client: Blockbot) -> None:
    client.add_plugin(plugin)