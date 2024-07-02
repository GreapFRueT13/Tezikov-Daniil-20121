from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                               QVBoxLayout, QLabel, QLineEdit, QTextEdit, 
                               QDialog, QDialogButtonBox)
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt
import sys
import itertools
import time

class Board:
    def __init__(self, N: int):
        self.N = N
        self.board = [["0"] * N for _ in range(N)]

    def clear(self):
        self.board = [["0"] * self.N for _ in range(self.N)]

    def __getitem__(self, pos):
        row, col = pos
        return self.board[row][col]

    def __setitem__(self, pos, value):
        row, col = pos
        self.board[row][col] = value

    def display(self):
        for row in self.board:
            print(" ".join(row))

class Figure:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.moves = [(row, col - 1), (row, col - 2),
                      (row, col + 1), (row, col + 2),
                      (row - 1, col), (row - 2, col),
                      (row + 1, col), (row + 2, col)]

    def make_move(self, board):
        board[self.row, self.col] = "#"
        for row_index, col_index in self.moves:
            if 0 <= row_index < board.N and 0 <= col_index < board.N and board[row_index, col_index] != "#":
                board[row_index, col_index] = "*"

class Files:
    def __init__(self, output_file_name="output.txt"):
        self.output_file_name = output_file_name

    def set_data(self, all_steps):
        with open(self.output_file_name, "w", encoding='utf-8') as output_file:
            if not all_steps:
                output_file.write("no steps")
            else:
                for step in all_steps:
                    output_file.write(" ".join(map(str, step)) + "\n")

class Game:
    def __init__(self, console_display=False):
        self.files = Files()
        self.N = 0
        self.L = 0
        self.K = 0
        self.board = None
        self.steps_list = []
        self.all_steps = []
        self.console_display = console_display

    def initialize_game(self, N, L, K, figure_coordinates):
        self.N = N
        self.L = L
        self.K = K
        self.board = Board(N)
        self.board.clear()
        self.steps_list = figure_coordinates

        for row, col in figure_coordinates:
            figure = Figure(row, col)
            figure.make_move(self.board)

    def find_steps(self, L, board, steps, row=0, col=-1):
        if L == 0:
            self.all_steps.append(steps[:])
            return

        for i in range(row, board.N):
            for j in range(col + 1 if i == row else 0, board.N):
                if board[i, j] == "0":
                    new_board = Board(board.N)
                    new_board.board = [row[:] for row in board.board]
                    figure = Figure(i, j)
                    figure.make_move(new_board)
                    steps.append((i, j))
                    self.find_steps(L - 1, new_board, steps, i, j)
                    steps.pop()

    def get_all_steps(self):
        self.all_steps = []
        self.find_steps(self.L, self.board, self.steps_list[:])
        return self.all_steps

    def display_info(self, start_time):
        if self.console_display:
            print("#------Результат------#")
            print(f"Всего решений: {len(self.all_steps)}")
            end_time = time.time()
            print(f"Время выполнения программы: {round(end_time - start_time, 1)}s")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")

        self.layout = QVBoxLayout(self)

        self.field_size_label = QLabel("Размер поля:")
        self.field_size_entry = QLineEdit()
        self.layout.addWidget(self.field_size_label)
        self.layout.addWidget(self.field_size_entry)

        self.num_figures_label = QLabel("Количество фигур:")
        self.num_figures_entry = QLineEdit()
        self.layout.addWidget(self.num_figures_label)
        self.layout.addWidget(self.num_figures_entry)

        self.pre_set_figures_label = QLabel("Предустановленные фигуры:")
        self.pre_set_figures_entry = QLineEdit()
        self.layout.addWidget(self.pre_set_figures_label)
        self.layout.addWidget(self.pre_set_figures_entry)

        self.figures_label = QLabel("Фигуры (x y тип):")
        self.figures_entry = QTextEdit()
        self.layout.addWidget(self.figures_label)
        self.layout.addWidget(self.figures_entry)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Save).setText("Сохранить")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Отмена")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def set_data(self, field_size, num_figures, pre_set_figures, figures):
        self.field_size_entry.setText(str(field_size))
        self.num_figures_entry.setText(str(num_figures))
        self.pre_set_figures_entry.setText(str(pre_set_figures))
        self.figures_entry.setText("\n".join(f"{x} {y} {typ}" for x, y, typ in figures))

    def get_data(self):
        field_size = int(self.field_size_entry.text())
        num_figures = int(self.num_figures_entry.text())
        pre_set_figures = int(self.pre_set_figures_entry.text())
        figures = []
        for line in self.figures_entry.toPlainText().split("\n"):
            x, y, typ = line.split()
            figures.append((int(x), int(y), typ))
        return field_size, num_figures, pre_set_figures, figures

class GameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Игра")
        self.setGeometry(100, 100, 800, 600)

        self.field_size = 16
        self.num_figures = 3
        self.pre_set_figures = 4
        self.figures = []

        self.initUI()
        self.load_settings()

    def initUI(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.canvas = Canvas(self)
        self.layout.addWidget(self.canvas)

        self.settings_button = QPushButton("Настройки", self)
        self.settings_button.clicked.connect(self.open_settings)
        self.layout.addWidget(self.settings_button)

        self.generate_button = QPushButton("Генерировать комбинации", self)
        self.generate_button.clicked.connect(self.generate_combinations)
        self.layout.addWidget(self.generate_button)

    def load_settings(self):
        try:
            with open('input.txt', 'r', encoding='utf-8') as f:
                data = f.readlines()
                self.field_size, self.num_figures, self.pre_set_figures = map(int, data[0].split())
                self.figures = []
                for line in data[1:]:
                    x, y, typ = line.split()
                    self.figures.append((int(x), int(y), typ))
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.field_size = 16
            self.num_figures = 3
            self.pre_set_figures = 4
            self.figures = []

    def save_settings(self):
        try:
            with open('input.txt', 'w', encoding='utf-8') as f:
                f.write(f"{self.field_size} {self.num_figures} {self.pre_set_figures}\n")
                for figure in self.figures:
                    f.write(f"{figure[0]} {figure[1]} {figure[2]}\n")
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.set_data(self.field_size, self.num_figures, self.pre_set_figures, self.figures)
        if dialog.exec() == QDialog.Accepted:
            self.field_size, self.num_figures, self.pre_set_figures, self.figures = dialog.get_data()
            self.save_settings()
            self.canvas.update_settings(self.field_size, self.figures)

    def generate_combinations(self):
        game = Game()
        figure_coords = [(x, y) for x, y, _ in self.figures]
        game.initialize_game(self.field_size, self.num_figures, self.pre_set_figures, figure_coords)
        start_time = time.time()
        all_steps = game.get_all_steps()
        game.display_info(start_time)
        game.files.set_data(all_steps)

class Canvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.board_size = 16
        self.figures = []
        self.cell_size = 30
        self.setFixedSize(self.board_size * self.cell_size, self.board_size * self.cell_size)

    def update_settings(self, board_size, figures):
        self.board_size = board_size
        self.figures = figures
        self.setFixedSize(self.board_size * self.cell_size, self.board_size * self.cell_size)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_board(painter)
        self.draw_figures(painter)

    def draw_board(self, painter):
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = QColor(255, 206, 158) if (row + col) % 2 == 0 else QColor(209, 139, 71)
                painter.fillRect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size, color)

    def draw_figures(self, painter):
        for x, y, typ in self.figures:
            painter.setBrush(Qt.black)
            painter.drawEllipse(y * self.cell_size, x * self.cell_size, self.cell_size, self.cell_size)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_gui = GameGUI()
    game_gui.show()
    sys.exit(app.exec())
