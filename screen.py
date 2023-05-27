import pyglet
from pyglet import shapes
from pyglet.gl import *

from tetris import *


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_size = 24
        self.i = 0

        self.batch = pyglet.graphics.Batch()
        background_color = [150, 150, 150, 255]
        background_color = [i / 255 for i in background_color]
        glClearColor(*background_color)
        TetrisGame.initialize()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            TetrisGame.move_left()
        elif symbol == pyglet.window.key.RIGHT:
            TetrisGame.move_right()
        if symbol == pyglet.window.key.A:
            TetrisGame.rotate_piece_90(True)
        elif symbol == pyglet.window.key.D:
            TetrisGame.rotate_piece_90(False)

    def on_key_release(self, symbol, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_draw(self):
        self.clear()  # Clear the window
        self.draw_grid()
        self.draw_score()
        self.draw_next_piece()
        self.batch.draw()

    def draw_rectangle(self, x, y, width, height, color, opacity):
        rectangle = shapes.Rectangle(x, y, width, height, color=color, batch=self.batch)
        rectangle.opacity = opacity
        rectangle.draw()

    def draw_triangle(self, x1, y1, x2, y2, x3, y3, color, opacity):
        rectangle = shapes.Triangle(x1, y1, x2, y2, x3, y3, color=color, batch=self.batch)
        rectangle.opacity = opacity
        rectangle.draw()

    def draw_line(self, x1, y1, x2, y2, color, width, opacity):
        line = shapes.Line(x1, y1, x2, y2, color=color, batch=self.batch, width=width)
        line.opacity = opacity
        line.draw()

    def update(self, dt):
        TetrisGame.render(dt)
        self.on_draw()

    def draw_grid(self):
        x_center = self.width / 2
        y_center = self.height / 2

        x_start = round(x_center - (TetrisGame.columns / 2) * self.cell_size)
        x_end = round(x_center + (TetrisGame.columns / 2) * self.cell_size)

        y_start = round(y_center - (TetrisGame.rows / 2) * self.cell_size)
        y_end = round(y_center + (TetrisGame.rows / 2) * self.cell_size)

        for x in range(x_start, x_end + 1, self.cell_size):
            self.draw_line(x, y_start, x, y_end, (0, 0, 0), 2, 255)

        for y in range(y_start, y_end + 1, self.cell_size):
            self.draw_line(x_start, y, x_end, y, (0, 0, 0), 2, 255)

        for piece in TetrisGame.pieces:
            self.draw_tetris_piece(piece, x_start, y_start, self.cell_size)

    def draw_score(self):
        label = pyglet.text.Label(f"Score: {TetrisGame.score}",
                                  font_name='Times New Roman',
                                  font_size=36,
                                  x=self.width // 2, y=self.height // 2 + self.cell_size * (TetrisGame.rows // 2 + 2),
                                  anchor_x='center', anchor_y='center')
        label.draw()

    def draw_next_piece(self):
        start_x = self.width // 2 + self.cell_size * (TetrisGame.columns // 2 + 1)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2)

        self.draw_rectangle(start_x, start_y, self.cell_size * 6, -self.cell_size * 9, (230, 230, 230), 255)
        label = pyglet.text.Label(f"Next Piece:", font_name='David', font_size=20,
                                  x=start_x + self.cell_size // 2, y=start_y - self.cell_size // 4,
                                  anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
        label.draw()

        if len(TetrisGame.next_pieces) > 0:
            piece_to_draw = TetrisGame.next_pieces[0]
            self.draw_tetris_piece(piece_to_draw, start_x + self.cell_size * 2.25, start_y - self.cell_size * 6,
                                   self.cell_size * 1.4, True)

    def draw_tetris_piece(self, piece, x, y, cell_size, ignore_center=False):
        for node in piece.nodes_centers:
            if round(node.y) < TetrisGame.rows or (not piece.is_active):
                if not ignore_center:
                    self.draw_piece_rectangle(
                        x + round(node.x) * cell_size,
                        y + round(node.y) * cell_size,
                        piece.color, cell_size)
                else:
                    self.draw_piece_rectangle(
                        round(x + (node.x - piece.center_x) * cell_size),
                        round(y + (node.y - piece.center_y) * cell_size),
                        piece.color, cell_size)

    def draw_piece_rectangle(self, x, y, color, cell_size):
        edges = 0.12 * cell_size

        bright = [round(0.6 * i + 0.4 * 255) for i in color]
        light_dark = [round(0.9 * i + 0.1 * 0) for i in color]
        dark = [round(0.7 * i + 0.3 * 0) for i in color]

        self.draw_rectangle(
            round(x + edges), round(y + cell_size - edges),
            round(cell_size - 2 * edges), round(edges), bright, 255)
        self.draw_triangle(
            round(x), round(y + cell_size),
            round(x + edges), round(y + cell_size),
            round(x + edges), round(y + cell_size - edges),
            bright, 255)
        self.draw_triangle(
            round(x + cell_size), round(y + cell_size),
            round(x + cell_size - edges), round(y + cell_size),
            round(x + cell_size - edges), round(y + cell_size - edges),
            bright, 255)

        self.draw_rectangle(round(x + edges), round(y), round(cell_size - 2 * edges), round(edges), dark, 255)
        self.draw_triangle(round(x), round(y), round(x + edges), round(y), round(x + edges), round(y + edges), dark, 255)
        self.draw_triangle(
            round(x + cell_size - edges), round(y),
            round(x + cell_size), round(y),
            round(x + cell_size - edges), round(y + edges),
            dark, 255)

        self.draw_rectangle(
            round(x), round(y + edges),
            round(edges), round(cell_size - 2 * edges), light_dark, 255)
        self.draw_triangle(
            round(x), round(y),
            round(x), round(y + edges),
            round(x + edges), round(y + edges),
            light_dark, 255)
        self.draw_triangle(
            round(x), round(y + cell_size),
            round(x), round(y + cell_size - edges),
            round(x + edges), round(y + cell_size - edges),
            light_dark, 255)

        self.draw_rectangle(
            round(x + cell_size - edges), round(y + edges),
            round(edges), round(cell_size - 2 * edges), light_dark, 255)
        self.draw_triangle(
            round(x + cell_size), round(y),
            round(x + cell_size), round(y + edges),
            round(x + cell_size - edges), round(y + edges),
            light_dark, 255)
        self.draw_triangle(
            round(x + cell_size), round(y + cell_size),
            round(x + cell_size), round(y + cell_size - edges),
            round(x + cell_size - edges), round(y + cell_size - edges),
            light_dark, 255)

        self.draw_rectangle(
            round(x + edges), round(y + edges),
            round(cell_size - 2 * edges), round(cell_size - 2 * edges), color, 255)
