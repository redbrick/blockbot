import logging
import asyncio
import enum
import random
import copy
import math
import interactions as discord


class GameState(enum.IntEnum):
    empty = 0
    player = -1
    ai = +1


def remove_id_format(text: str) -> int:
    """Remove the symbol arround a Discord ID string."""

    return int(text.replace("<", "").replace(">", "").replace("@", ""))


def render_board(board: list, disable=False) -> list:
    """
    Converts the test_board into a visual representation using discord components.
    :param board: The game test_board
    :param disable: Disable the buttons on the test_board
    :return: List[action-rows]
    """

    buttons = []
    for i in range(3):
        for x in range(3):
            if board[i][x] == GameState.empty:
                style = discord.ButtonStyle.GRAY
                label = "‎"
            elif board[i][x] == GameState.player:
                style = discord.ButtonStyle.PRIMARY
                label = "x"
            else:
                style = discord.ButtonStyle.RED
                label = "o"
            buttons.append(
                discord.Button(
                    style=style,
                    label=label,
                    custom_id=f"tic_tac_toe_button||{i},{x}",
                    disabled=disable,
                )
            )
    return discord.spread_to_rows(*buttons, max_in_row=3)


def alternate_render_board(board: list, disable=False) -> list:
    """
    Converts the test_board into a visual representation using discord components.
    This is used for the 2nd player mode since I have not found the way to combine
    everything into one callback yet.
    :param board: The game test_board
    :param disable: Disable the buttons on the test_board
    :return: List[action-rows]
    """

    buttons = []
    for i in range(3):
        for x in range(3):
            if board[i][x] == GameState.empty:
                style = discord.ButtonStyle.GRAY
                label = "‎"
            elif board[i][x] == GameState.player:
                style = discord.ButtonStyle.PRIMARY
                label = "x"
            else:
                style = discord.ButtonStyle.RED
                label = "o"
            buttons.append(
                discord.Button(
                    style=style,
                    label=label,
                    custom_id=f"tic_tac_toe_2p||{i},{x}",
                    disabled=disable,
                )
            )
    return discord.spread_to_rows(*buttons, max_in_row=3)


def board_state(components: list) -> list[list]:
    """
    Extrapolate the current state of the game based on the components of a message
    :param components: The components object from a message
    :return: The test_board state
    :rtype: list[list]
    """

    board = copy.deepcopy(BoardTemplate)
    for i in range(3):
        for x in range(3):
            button = components[i].components[x]
            if button.style == 2:
                board[i][x] = GameState.empty
            elif button.style == 1:
                board[i][x] = GameState.player
            elif button.style == 4:
                board[i][x] = GameState.ai
    return board


def win_state(board: list, player: GameState) -> bool:
    """
    Determines if the specified player has won
    :param board: The game test_board
    :param player: The player to check for
    :return: bool, have they won
    """
    win_states = [
        [board[0][0], board[0][1], board[0][2]],
        [board[1][0], board[1][1], board[1][2]],
        [board[2][0], board[2][1], board[2][2]],
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
        [board[0][0], board[1][1], board[2][2]],
        [board[2][0], board[1][1], board[0][2]],
    ]
    if [player, player, player] in win_states:
        return True
    return False


def get_possible_positions(board: list) -> list[list[int]]:
    """
    Determines all the possible positions in the current game state
    :param board: The game test_board
    :return: A list of possible positions
    """

    possible_positions = []
    for i in range(3):
        for x in range(3):
            if board[i][x] == GameState.empty:
                possible_positions.append([i, x])
    return possible_positions


def evaluate(board):
    if win_state(board, GameState.ai):
        score = +1
    elif win_state(board, GameState.player):
        score = -1
    else:
        score = 0
    return score


def min_max(test_board: list, depth: int, player: GameState):
    if player == GameState.ai:
        best = [-1, -1, -math.inf]
    else:
        best = [-1, -1, +math.inf]

    if (
        depth == 0
        or win_state(test_board, GameState.player)
        or win_state(test_board, GameState.ai)
    ):
        score = evaluate(test_board)
        return [-1, -1, score]

    for cell in get_possible_positions(test_board):
        x, y = cell[0], cell[1]
        test_board[x][y] = player
        score = min_max(test_board, depth - 1, -player)
        test_board[x][y] = GameState.empty
        score[0], score[1] = x, y

        if player == GameState.ai:
            if score[2] > best[2]:
                best = score
        else:
            if score[2] < best[2]:
                best = score
    return best


BoardTemplate = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


class TicTacToe(discord.Extension):
    def __init__(self, client: discord.Client):
        self.client: discord.Client = client

    @discord.slash_command(
        name="tictactoe",
        description="Play TicTacToe in 2 players mode.",
    )
    @discord.slash_option(
        name="user",
        description="The user you want to play against.",
        opt_type=discord.OptionType.USER,
        required=True,
    )
    async def ttt_2p(
        self, ctx: discord.SlashContext, user: discord.User
    ) -> None:
        """Play TicTacToee in 2 players mode."""

        if int(ctx.user.id) == int(user.id):
            return await ctx.send("You cannot challenge yourself.")

        if int(user.id) == int(self.client.user.id):
            return await ctx.send(
                "To challenge, you must tag a user, not a bot."
            )

        accept_deny = [
            discord.ActionRow(
                discord.Button(
                    style=discord.ButtonStyle.SUCCESS,
                    label="Accept",
                    custom_id="accept",
                ),
                discord.Button(
                    style=discord.ButtonStyle.DANGER,
                    label="Deny",
                    custom_id="deny",
                ),
            )
        ]

        msg = await ctx.send(
            content=f"{ctx.user.mention} challenged {user.mention}.",
            components=accept_deny,
            allowed_mentions={"users": [int(user.id)]},
        )

        opn: discord.Member = None
        async for _user in msg.mention_users:
            if int(_user.id) != int(ctx.user.id):
                opn = _user

        try:

            def _check(_ctx: discord.ComponentContext) -> bool:
                return int(_ctx.ctx.user.id) == int(opn.user.id) and int(
                    _ctx.ctx.channel_id
                ) == int(ctx.channel_id)

            res = await self.client.wait_for_component(
                components=accept_deny,
                messages=int(msg.id),
                check=_check,
                timeout=15,
            )

            if res.ctx.custom_id == "accept":
                goes_first: discord.Member = random.choice(
                    [opn.user, ctx.user]
                )
                await res.ctx.edit_origin(
                    content="".join(
                        [
                            f"{ctx.author.mention} **VS** {opn.mention} tic tac toe game.\n",
                            f"<@{goes_first.id}> turn.",
                        ]
                    ),
                    components=alternate_render_board(
                        copy.deepcopy(BoardTemplate)
                    ),
                )

            elif res.ctx.custom_id == "deny":
                await res.ctx.edit_origin(
                    content="Challenge cancelled.",
                    components=[],
                )

        except asyncio.TimeoutError:
            pass

    @discord.component_callback(
        discord.get_components_ids(
            alternate_render_board(board=copy.deepcopy(BoardTemplate))
        )
    )
    async def alternate_process_turn(
        self, ctx: discord.ComponentContext
    ) -> None:
        og = remove_id_format(ctx.message.content.split()[0])
        chd = remove_id_format(ctx.message.content.split()[2])

        await ctx.defer(edit_origin=True)
        player1 = remove_id_format(ctx.message.content.split()[-2])
        player2 = og if og != player1 else chd

        if int(ctx.user.id) not in [player1, player2]:
            return

        if int(ctx.user.id) != player1:
            return

        button_pos = (ctx.custom_id.split("||")[-1]).split(",")
        button_pos = [int(button_pos[0]), int(button_pos[1])]
        components = ctx.message.components

        board = board_state(components)

        # We will reuse the GameState object.
        # Original challenger will be assigned as .player
        # Challenged user will be assigned as .ai
        if board[button_pos[0]][button_pos[1]] == GameState.empty:
            if og == int(ctx.user.id):
                board[button_pos[0]][button_pos[1]] = GameState.player
            elif chd == int(ctx.user.id):
                board[button_pos[0]][button_pos[1]] = GameState.ai
        else:
            return

        if win_state(board, GameState.player):
            winner = og
        elif win_state(board, GameState.ai):
            winner = chd
        elif len(get_possible_positions(board)) == 0:
            winner = "Nobody"
        else:
            winner = None

        if winner == "Nobody":
            content = "Nobody has won!"
        elif winner in [og, chd]:
            content = f"<@{winner}> is the winner!"
        else:
            content = "".join(
                [
                    f"<@{og}> **VS** <@{chd}> tic tac toe game.\n",
                    f"<@{player2}> turn.",
                ]
            )

        allowed_mentions = None
        if winner is not None:
            if isinstance(winner, int):
                allowed_mentions = {"users": [winner]}
            else:
                allowed_mentions = None
        else:
            allowed_mentions = None

        await ctx.edit_origin(
            content=content,
            components=alternate_render_board(
                board, disable=winner is not None
            ),
            allowed_mentions=allowed_mentions,
        )
