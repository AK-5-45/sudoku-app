from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.config import Config
from kivy.clock import Clock
from kivy.utils import platform
Config.set('input', 'mouse', 'mouse,disable_multitouch')
import random
import os
if platform not in ('android', 'ios'):
    Window.size = (450, 850)
def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None
def is_valid(board, num, row, col):
    if num in board[row]:
        return False
    if num in [board[i][col] for i in range(9)]:
        return False
    box_r, box_c = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_r, box_r + 3):
        for j in range(box_c, box_c + 3):
            if board[i][j] == num:
                return False
    return True
def solve_board(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty
    for num in range(1, 10):
        if is_valid(board, num, row, col):
            board[row][col] = num
            if solve_board(board):
                return True
            board[row][col] = 0
    return False
def count_solutions(board, limit=2):
    empty = find_empty(board)
    if not empty:
        return 1
    row, col = empty
    solutions = 0
    for num in range(1, 10):
        if is_valid(board, num, row, col):
            board[row][col] = num
            solutions += count_solutions(board, limit)
            board[row][col] = 0
            if solutions >= limit:
                return solutions
    return solutions
def has_unique_solution(board):
    board_copy = [row[:] for row in board]
    return count_solutions(board_copy, limit=2) == 1
def generate_unique_puzzle(holes=40, max_attempts=50):
    for attempt in range(max_attempts):
        full = [[0] * 9 for _ in range(9)]
        solve_board(full)
        puzzle = [row[:] for row in full]
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        for i, j in positions[:holes]:
            puzzle[i][j] = 0
        if has_unique_solution(puzzle):
            return puzzle, full
    return generate_unique_puzzle(holes=holes - 5, max_attempts=max_attempts)
class SudokuCell(Button):
    def __init__(self, row, col, value=0, is_given=False, **kwargs):
        super().__init__(**kwargs)
        self.row = row
        self.col = col
        self.is_given = is_given
        self.value = value
        self.update_display()
    def update_display(self):
        self.text = str(self.value) if self.value != 0 else ""
        if self.is_given:
            self.color = (1, 1, 1, 1)
            self.background_color = (0.3, 0.3, 0.35, 1)
        else:
            self.color = (0.4, 0.8, 1, 1)
            self.background_color = (0.15, 0.15, 0.2, 1)
    def set_error(self):
        if not self.is_given and self.value != 0:
            self.color = (1, 0.3, 0.3, 1)
    def set_correct(self):
        if not self.is_given and self.value != 0:
            self.color = (0.4, 0.8, 1, 1)
class SudokuBoard(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 9
        self.rows = 9
        self.padding = 5
        self.spacing = 1
        self.row_force_default = True
        self.col_force_default = True
        self.size_hint = (1, None)
        self.bind(width=self._update_size)
        self.cells = {}
        self.selected = None
        self.puzzle = None
        self.victory_sound = None
        sound_path = os.path.join(os.path.dirname(__file__), 'victory.mp3')
        if os.path.exists(sound_path):
            self.victory_sound = SoundLoader.load(sound_path)
        self.generate_new_game()
    def _update_size(self, *args):
        self.height = self.width
        cell_size = (self.width - 10 - 8) / 9
        self.row_default_height = cell_size
        self.col_default_width = cell_size
        font_size = int(cell_size * 0.55)
        for cell in self.cells.values():
            cell.font_size = font_size
    def generate_new_game(self):
        self.puzzle, _ = generate_unique_puzzle(holes=40)
        self.clear_widgets()
        self.cells.clear()
        for i in range(9):
            for j in range(9):
                val = self.puzzle[i][j]
                cell = SudokuCell(row=i, col=j, value=val, is_given=(val != 0))
                cell.bind(on_press=self.on_cell_press)
                self.cells[(i, j)] = cell
                self.add_widget(cell)
        Clock.schedule_once(self._update_size, 0)
    def on_cell_press(self, instance):
        if self.selected and self.selected != instance:
            if self.selected.is_given:
                self.selected.background_color = (0.3, 0.3, 0.35, 1)
            else:
                self.selected.background_color = (0.15, 0.15, 0.2, 1)
        self.selected = instance
        instance.background_color = (1, 0.8, 0.2, 1)
    def input_number(self, num):
        if not self.selected or self.selected.is_given:
            return
        self.selected.value = num
        self.selected.update_display()
        self.check_answer()
    def erase(self):
        if self.selected and not self.selected.is_given:
            self.selected.value = 0
            self.selected.update_display()
            self.selected.set_correct()
    def check_answer(self):
        current_board = [[0] * 9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                current_board[i][j] = self.cells[(i, j)].value
        for cell in self.cells.values():
            if cell.value != 0:
                current_board[cell.row][cell.col] = 0
                if is_valid(current_board, cell.value, cell.row, cell.col):
                    if cell.is_given:
                        cell.color = (1, 1, 1, 1)
                    else:
                        cell.set_correct()
                else:
                    cell.set_error()
                current_board[cell.row][cell.col] = cell.value
        self.check_victory()
    def check_victory(self):
        for cell in self.cells.values():
            if cell.value == 0:
                return
        has_errors = False
        for cell in self.cells.values():
            if cell.color == (1, 0.3, 0.3, 1):
                has_errors = True
                break
        if not has_errors:
            self.play_victory_sound()
    def play_victory_sound(self):
        if self.victory_sound:
            self.victory_sound.seek(0)
            self.victory_sound.play()
class NewGameButton(Button):
    def __init__(self, board, **kwargs):
        super().__init__(**kwargs)
        self.text = "Новая игра"
        self.size_hint = (1, None)
        self.height = 60
        self.background_color = (0.2, 0.6, 0.2, 1)
        self.board = board
        self.bind(on_press=lambda x: self.board.generate_new_game())
        self.bind(size=self._update_font)
    def _update_font(self, *args):
        self.font_size = int(self.height * 0.45)
class NumberPad(GridLayout):
    def __init__(self, board, **kwargs):
        super().__init__(**kwargs)
        self.cols = 5
        self.rows = 2
        self.size_hint = (1, None)
        self.height = 140
        self.padding = 10
        self.spacing = 10
        self.board = board
        for n in range(1, 6):
            btn = Button(text=str(n))
            btn.bind(on_press=lambda x, num=n: self.board.input_number(num))
            self.add_widget(btn)
        for n in range(6, 10):
            btn = Button(text=str(n))
            btn.bind(on_press=lambda x, num=n: self.board.input_number(num))
            self.add_widget(btn)
        erase_btn = Button(text="✕", background_color=(0.6, 0.2, 0.2, 1))
        erase_btn.bind(on_press=lambda x: self.board.erase())
        self.add_widget(erase_btn)
        self.bind(size=self._update_fonts)
    def _update_fonts(self, *args):
        btn_width = (self.width - 20 - 40) / 5
        btn_height = (self.height - 20 - 10) / 2
        font_size = int(min(btn_width, btn_height) * 0.5)
        for child in self.children:
            child.font_size = font_size
class SudokuScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 15
        self.board = SudokuBoard()
        self.new_btn = NewGameButton(self.board)
        self.numpad = NumberPad(self.board)
        self.add_widget(self.new_btn)
        self.add_widget(self.board)
        self.add_widget(self.numpad)
class SudokuApp(App):
    def build(self):
        return SudokuScreen()
if __name__ == '__main__':
    SudokuApp().run()
