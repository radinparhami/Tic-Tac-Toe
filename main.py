from copy import deepcopy
from random import choice
from typing import Callable, Optional

import flet as ft


class Player:
    def __init__(self, name: str, color: str | None = None) -> None:
        self.name = name
        if color is None:
            self.color = ft.colors.random_color()
        elif color in ft.colors.colors_list:
            self.color = color
        else:
            raise ValueError(f"{color} is not a valid color!")

    def __repr__(self) -> str:
        return f"Player(name={self.name!r}, color={self.color!r})"


class Point(ft.IconButton):
    def __init__(
        self,
        icon: Optional[str] = None,
        icon_color: Optional[str] = None,
        icon_size: ft.OptionalNumber = None,
        selected: Optional[bool] = None,
        selected_icon: Optional[str] = None,
        selected_icon_color: Optional[str] = None,
        bgcolor: Optional[str] = None,
        highlight_color: Optional[str] = None,
        style: Optional[ft.ButtonStyle] = None,
        content: Optional[ft.Control] = None,
        autofocus: Optional[bool] = None,
        disabled_color: Optional[str] = None,
        hover_color: Optional[str] = None,
        focus_color: Optional[str] = None,
        splash_color: Optional[str] = None,
        splash_radius: ft.OptionalNumber = None,
        alignment: Optional[ft.Alignment] = None,
        padding: ft.PaddingValue = None,
        enable_feedback: Optional[bool] = None,
        url: Optional[str] = None,
        url_target: Optional[ft.UrlTarget] = None,
        mouse_cursor: Optional[ft.MouseCursor] = None,
        visual_density: Optional[ft.ThemeVisualDensity] = None,
        on_focus: ft.OptionalEventCallable = None,
        on_blur: ft.OptionalEventCallable = None,
    ) -> None:
        super().__init__()
        self.selected = selected
        self.selected_icon = selected_icon
        self.selected_icon_color = selected_icon_color
        self.bgcolor = bgcolor
        self.highlight_color = highlight_color
        self.style = style
        self.content = content
        self.autofocus = autofocus
        self.disabled_color = disabled_color
        self.hover_color = hover_color
        self.focus_color = focus_color
        self.splash_color = splash_color
        self.splash_radius = splash_radius
        self.alignment = alignment
        self.padding = padding
        self.enable_feedback = enable_feedback
        self.url = url
        self.url_target = url_target
        self.mouse_cursor = mouse_cursor
        self.visual_density = visual_density
        self.on_focus = on_focus
        self.on_blur = on_blur
        # Parent attributes
        self.icon_color = icon_color or ft.colors.WHITE
        self.icon = icon or ft.icons.CIRCLE
        self.icon_size = icon_size or 100

    def initial(self, row: int, column: int, owner: Player | None = None):
        # Child attributes
        self.row: int = row
        self.column: int = column

        self.owner: Player | None = owner

    def set_owner(self, player: Player):
        self.owner = player
        return self

    def __repr__(self) -> str:
        return f"Point(row={self.row!r}, column={self.column!r}, owner={self.owner!r})"


class GameBoard_Event:
    WIN = "WIN"
    DRAW = "DRAW"
    NOTHING = "NOTHING"

    def __init__(self, status: str, player: Player, point: Point) -> None:
        self.status = status
        self.player: Player = player
        self.point: Point = point

    def __repr__(self) -> str:
        return f"GameBoard_Event(status={self.status!r}, player={self.player!r}, point={self.point!r})"


class GameBoard(ft.Container):
    def __init__(
        self,
        board_size: int,
        players: list[Player],
        on_click: Callable[[ft.ControlEvent], None],
        turn: Player | None = None,
        point_sample: Point = Point(),
    ):
        super().__init__()
        # Child attributes
        if (players_length := len(players)) < 2:
            if players_length == 1:
                alone_player = players[0]
                raise Exception(
                    f"Dear {alone_player.name}. You can't play this game just by yourself!"
                )
            # if players_length == 0:
            raise Exception("You need two players at least!")

        self._players: dict[Player, list[Point]] = {}
        self._point_sample = point_sample
        self._board_size = board_size
        self._points: list[Point] = []
        self._turn: Player
        for player in players:
            self._add_player(player)

        self._set_turn(turn)
        # Parent attributes
        self.content = ft.Column(controls=[])
        for row in range(self.board_size):
            row_list = ft.Row(controls=[])
            for column in range(self.board_size):
                point = deepcopy(self._point_sample)
                point.initial(row, column)
                point.on_click = on_click

                row_list.controls.append(point)
                self._points.append(point)

            self.content.controls.append(row_list)
        # Save GameBoard backup
        self._backup_content = deepcopy(self.content)
        self._backup__players = deepcopy(self._players)

    @property
    def board_size(self):
        return self._board_size

    @property
    def turn(self):
        return self._turn

    @property
    def all_players(self):
        return list(self._players.keys())

    def _player_exist(self, player: Player) -> bool:
        if self._players.get(player, None) is None:
            return False
        return True

    def _add_player(self, player: Player):
        if self._player_exist(player):
            raise KeyError(f"{player} added before!")

        self._players.setdefault(player, [])

    def _set_turn(self, player: Player | None):
        if player is None:
            player = choice(self.all_players)
        else:
            if not self._player_exist(player):
                raise IndexError(f"{player} are'nt in this GameBoard!")

        self._turn = player

    def _longest_consecutive(self, nums: list[int]) -> bool:
        num_set = set(nums)
        longest_streak = 0

        for num in num_set:
            if num - 1 not in num_set:
                current_num = num
                current_streak = 1

                while current_num + 1 in num_set:
                    current_num += 1
                    current_streak += 1

                longest_streak = max(longest_streak, current_streak)
                if longest_streak >= self.board_size:
                    return True
        return False

    def _win_position_check(self, player: Player) -> bool:
        if not self._player_exist(player):
            raise IndexError(f"{player} are'nt in this GameBoard!")

        player_points: list[Point] = self._players[player]

        horizontal_state: dict[int, list[int]] = {}
        vertical_state: dict[int, list[int]] = {}

        for point in player_points:
            row, column = point.row, point.column
            horizontal_state[row] = horizontal_state.get(row, []) + [column]
            vertical_state[column] = vertical_state.get(column, []) + [row]

        for chain in [list(horizontal_state.values()), list(vertical_state.values())]:
            for consecutive in chain:
                if self._longest_consecutive(consecutive):
                    return True
        return False

    def get_point(self, row: int, column: int) -> Point:
        return self._points[row * self.board_size + column]

    def select_point(
        self, point: Point, player: Player | None = None
    ) -> GameBoard_Event:
        if player is None:
            player = self.turn
        else:
            if not self._player_exist(player):
                raise IndexError(f"{player} are'nt in this GameBoard!")

            if player != self._turn:
                raise Exception(f"{player} is not your turn!")

        if point not in self._points:
            raise IndexError(f"{point} out of GameBoard!")

        if point.owner is not None:
            raise Exception(f"{point} is already selected!")

        all_players = self.all_players
        player_index = all_players.index(player)

        next_player_index = player_index + 1
        if next_player_index == len(self._players):  # if turn is last player
            next_player_index = 0  # set turn to first player

        self._set_turn(self.all_players[next_player_index])
        self._players[player].append(point.set_owner(player))

        status = GameBoard_Event.NOTHING  # default status
        # Get count of this player selected points >= GameBoard size
        if len(self._players[player]) >= self.board_size:
            if self._win_position_check(player):
                status = GameBoard_Event.WIN
            # if all points are selected
            elif (
                sum(1 for point in self._points if point.owner is not None)
                == self.board_size**2
            ):
                status = GameBoard_Event.DRAW

        return GameBoard_Event(status, player, point)


radin = Player("radin", "red")
ali = Player("ali", "blue")

game_board_size: int = 3


def listener(e: ft.ControlEvent):
    global game_board
    point: Point = e.control
    point.icon_color = game_board.turn.color

    g_b_e: GameBoard_Event = game_board.select_point(point)
    turn_bar.controls = [
        ft.Text("Turn:"),
        ft.Text(game_board.turn.name, color=game_board.turn.color),
    ]
    row_content = ft.Row(controls=[], alignment=ft.MainAxisAlignment.CENTER, scale=3)
    dlg = ft.AlertDialog(
        content=ft.Column(
            controls=[row_content],
            alignment=ft.MainAxisAlignment.CENTER,
            height=80,
            width=100,
        )
    )

    match g_b_e.status:
        case GameBoard_Event.WIN:
            player_txt = ft.Text(g_b_e.player.name, color=g_b_e.player.color)
            row_content.controls = [player_txt, ft.Text("Win!")]
        case GameBoard_Event.DRAW:
            row_content.controls = [ft.Text("Draw!", color=ft.colors.LIGHT_BLUE_400)]
        case GameBoard_Event.NOTHING:
            return e.page.update()

    e.page.clean()
    game_board = deepcopy(game_board_backup)
    turn_bar.controls = [
        ft.Text("Turn:"),
        ft.Text(game_board.turn.name, color=game_board.turn.color),
    ]
    e.page.add(turn_bar, ft.Divider(), game_board)
    e.page.update()
    e.page.open(dlg)


point_sample = Point(icon_color=ft.colors.GREEN_200)
game_board = GameBoard(
    game_board_size,
    players=[radin, ali],
    on_click=listener,
    point_sample=point_sample,
)
turn_bar = ft.Row(
    controls=[
        ft.Text("Turn:"),
        ft.Text(game_board.turn.name, color=game_board.turn.color),
    ],
    alignment=ft.MainAxisAlignment.CENTER,
    scale=3,
)
game = turn_bar, ft.Divider(), game_board
game_board_backup = deepcopy(game_board)


def main(page: ft.Page):
    page.title = "Tic-Tac-Toe"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 500
    page.window.width = 500
    page.window.max_height = page.window.height
    page.window.max_width = page.window.width
    page.padding = 50
    page.update()

    page.add(turn_bar, ft.Divider(), game_board)
    page.update()


ft.app(target=main)
