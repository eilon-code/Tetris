import pyglet
from pyglet.gl import *

import utils
from tetris import *


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_size = 24

        self.batch = pyglet.graphics.Batch()
        background_color = [150, 150, 150, 255]
        background_color = [i / 255 for i in background_color]
        glClearColor(*background_color)
        TetrisGame.initialize()

        self.defeat_button = \
            utils.AnimatedButton(self.batch,
                                 self.width // 2, self.height // 2 - self.cell_size * 6.5,
                                 self.cell_size * 6, self.cell_size * 2, self.cell_size * 0.2,
                                 "Decline >",
                                 (200, 0, 20, 200), (100, 0, 0, 200), (50, 0, 0, 150),
                                 (40, 40, 40, 200),
                                 font_name='Arial', font_size=18, border_radius=4)
        self.award_button = \
            utils.AnimatedButton(self.batch,
                                 self.width // 2, self.height // 2 - self.cell_size * 6.5,
                                 self.cell_size * 6, self.cell_size * 2, self.cell_size * 0.2,
                                 "Accept :)",
                                 (20, 230, 0, 200), (10, 140, 0, 200), (0, 70, 0, 150),
                                 (40, 40, 40, 200),
                                 font_name='Arial', font_size=18, border_radius=4)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            TetrisGame.move_left()
        elif symbol == pyglet.window.key.RIGHT:
            TetrisGame.move_right()
        if symbol == pyglet.window.key.A:
            TetrisGame.rotate_piece_90(True)
        elif symbol == pyglet.window.key.D:
            TetrisGame.rotate_piece_90(False)
        elif symbol == pyglet.window.key.DOWN:
            TetrisGame.force_down()
        else:
            pass

        self.on_draw()

    def on_key_release(self, symbol, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        if (self.defeat_button.release() or self.award_button.release()) and not TetrisGame.is_game_running:
            TetrisGame.initialize()

    def on_mouse_press(self, x, y, button, modifiers):
        self.defeat_button.click(x, y)
        self.award_button.click(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        self.defeat_button.update_mouse_movement(x, y, dx, dy)
        self.award_button.update_mouse_movement(x, y, dx, dy)

    def on_draw(self):
        self.clear()  # Clear the window
        self.change_mouse_curser()
        self.draw_grid()
        self.draw_score()
        self.draw_next_piece()
        if not TetrisGame.is_game_running:
            if TetrisGame.score <= TetrisGame.best_score:
                self.draw_defeat()
            else:
                self.draw_award()
        self.batch.draw()

    def change_mouse_curser(self):
        default_cursor = self.get_system_mouse_cursor(self.CURSOR_DEFAULT)
        text_cursor = self.get_system_mouse_cursor(self.CURSOR_TEXT)
        help_cursor = self.get_system_mouse_cursor(self.CURSOR_HELP)
        crosshair_cursor = self.get_system_mouse_cursor(self.CURSOR_CROSSHAIR)
        no_cursor = self.get_system_mouse_cursor(self.CURSOR_NO)
        size_cursor = self.get_system_mouse_cursor(self.CURSOR_SIZE)
        wait_cursor = self.get_system_mouse_cursor(self.CURSOR_WAIT)
        wait_arrow_cursor = self.get_system_mouse_cursor(self.CURSOR_WAIT_ARROW)

        cursor = default_cursor
        self.set_mouse_cursor(cursor)

    def draw_grid(self):
        x_center = self.width / 2
        y_center = self.height / 2

        x_start = round(x_center - (TetrisGame.columns / 2) * self.cell_size)
        x_end = round(x_center + (TetrisGame.columns / 2) * self.cell_size)

        y_start = round(y_center - (TetrisGame.rows / 2) * self.cell_size)
        y_end = round(y_center + (TetrisGame.rows / 2) * self.cell_size)

        for x in range(x_start, x_end + 1, self.cell_size):
            utils.draw_line(x, y_start, x, y_end, (0, 0, 0), 2, 255, self.batch)

        for y in range(y_start, y_end + 1, self.cell_size):
            utils.draw_line(x_start, y, x_end, y, (0, 0, 0), 2, 255, self.batch)

        for piece in TetrisGame.pieces:
            self.draw_tetris_piece(piece, x_start, y_start, self.cell_size)

    def draw_score(self):
        score_label = pyglet.text.Label(f"Score: {TetrisGame.score}",
                                        font_name='Times New Roman',
                                        font_size=36,
                                        x=self.width // 2,
                                        y=self.height // 2 + self.cell_size * (TetrisGame.rows // 2 + 3),
                                        anchor_x='center', anchor_y='center')
        score_label.draw()
        best_score_label = pyglet.text.Label(f"Best Score: {TetrisGame.best_score}",
                                             font_name='Times New Roman',
                                             font_size=18,
                                             x=self.width // 2,
                                             y=self.height // 2 + round(self.cell_size * (TetrisGame.rows // 2 + 1)),
                                             anchor_x='center', anchor_y='center')
        best_score_label.draw()

    def draw_next_piece(self):
        start_x = self.width // 2 + self.cell_size * (TetrisGame.columns // 2 + 1)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2)

        utils.draw_rectangle(start_x, start_y, self.cell_size * 6, -self.cell_size * 9, (230, 230, 230), 255,
                             self.batch)
        label = pyglet.text.Label(f"Next Piece:", font_name='David', font_size=20,
                                  x=start_x + self.cell_size // 2, y=start_y - self.cell_size // 4,
                                  anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
        label.draw()

        if len(TetrisGame.next_pieces) > 0:
            piece_to_draw = TetrisGame.next_pieces[0]
            self.draw_tetris_piece(piece_to_draw, start_x + self.cell_size * 2.25, start_y - self.cell_size * 6,
                                   self.cell_size * 1.4, True)

    def draw_defeat(self):
        start_x = self.width // 2 - self.cell_size * (TetrisGame.columns // 2 + 6)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2 - 2)

        utils.draw_rectangle(start_x, start_y,
                             self.cell_size * (TetrisGame.columns + 12),
                             -self.cell_size * 16, (100, 100, 200), 200, self.batch)

        label = pyglet.text.Label(f"Dear looser, you lost.",
                                  font_name='David', font_size=24,
                                  x=start_x + self.cell_size // 2, y=start_y - self.cell_size // 4,
                                  anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
        label.draw()
        loss_reasons = pyglet.text.Label(f"Reasons of loss:",
                                         font_name='David', font_size=18,
                                         x=start_x + self.cell_size * 2, y=start_y - self.cell_size * 3,
                                         anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
        loss_reasons.draw()
        reasons = [f"1. inability to grasp the shape of the pieces",
                   f"2. lack of thinking skills",
                   f"3. low quality of gaming in general"]

        for i in range(len(reasons)):
            reason_label = pyglet.text.Label(reasons[i],
                                             font_name='David', font_size=18,
                                             x=start_x + self.cell_size * 3, y=start_y - self.cell_size * (5 + i * 1.5),
                                             anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
            reason_label.draw()

        conclusions = [f"Please understand you are unqualified",
                       f"to achieve a new high score and stop playing",
                       f"this game, it's not ment for the likes of you."]

        for i in range(len(conclusions)):
            conclusion = pyglet.text.Label(conclusions[i],
                                           font_name='David', font_size=18,
                                           x=start_x + self.cell_size * 2, y=start_y - self.cell_size * (10 + i),
                                           anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
            conclusion.draw()

        self.defeat_button.draw()

    def draw_award(self):
        start_x = self.width // 2 - self.cell_size * (TetrisGame.columns // 2 + 6)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2 - 2)

        utils.draw_rectangle(start_x, start_y,
                             self.cell_size * (TetrisGame.columns + 12),
                             -self.cell_size * 16, (150, 200, 200), 200, self.batch)

        label = pyglet.text.Label(f"Lucky bastard!, a new high score.",
                                  font_name='David', font_size=24,
                                  x=start_x + self.cell_size // 2, y=start_y - self.cell_size // 4,
                                  anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
        label.draw()
        loss_reasons = pyglet.text.Label(f"Assumptions:",
                                         font_name='David', font_size=18,
                                         x=start_x + self.cell_size * 2, y=start_y - self.cell_size * 3,
                                         anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
        loss_reasons.draw()
        reasons = [f"1. the game isn't that hard",
                   f"2. your score is good relative to yourself alone",
                   f"3. probably you were close to loose earlier"]

        for i in range(len(reasons)):
            reason_label = pyglet.text.Label(reasons[i],
                                             font_name='David', font_size=18,
                                             x=start_x + self.cell_size * 3, y=start_y - self.cell_size * (5 + i * 1.5),
                                             anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
            reason_label.draw()

        conclusions = [f"Please try again I asure you can't score better",
                       f"than this due to the reasons above.",
                       f"You only won yourself by luck."]

        for i in range(len(conclusions)):
            conclusion = pyglet.text.Label(conclusions[i],
                                           font_name='David', font_size=18,
                                           x=start_x + self.cell_size * 2, y=start_y - self.cell_size * (10 + i),
                                           anchor_x='left', anchor_y='top', color=(0, 0, 0, 255))
            conclusion.draw()

        self.award_button.draw()

    def draw_tetris_piece(self, piece, x, y, cell_size, ignore_center=False):
        for node in piece.nodes_centers:
            if round(node.y) < TetrisGame.rows or (not piece.is_active):
                if not ignore_center:
                    utils.draw_rectangle(
                        x + round(node.x) * cell_size, y + round(node.y) * cell_size,
                        cell_size, cell_size, piece.color, 255, self.batch)
                    # self.draw_piece_rectangle(
                    #     x + round(node.x) * cell_size,
                    #     y + round(node.y) * cell_size,
                    #     piece.color, cell_size)
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

        utils.draw_rectangle(
            round(x + edges), round(y + cell_size - edges),
            round(cell_size - 2 * edges), round(edges), bright, 255, self.batch)
        utils.draw_triangle(
            round(x), round(y + cell_size),
            round(x + edges), round(y + cell_size),
            round(x + edges), round(y + cell_size - edges),
            bright, 255, self.batch)
        utils.draw_triangle(
            round(x + cell_size), round(y + cell_size),
            round(x + cell_size - edges), round(y + cell_size),
            round(x + cell_size - edges), round(y + cell_size - edges),
            bright, 255, self.batch)

        utils.draw_rectangle(round(x + edges), round(y), round(cell_size - 2 * edges), round(edges), dark, 255,
                             self.batch)
        utils.draw_triangle(round(x), round(y), round(x + edges), round(y), round(x + edges), round(y + edges), dark,
                            255, self.batch)
        utils.draw_triangle(
            round(x + cell_size - edges), round(y),
            round(x + cell_size), round(y),
            round(x + cell_size - edges), round(y + edges),
            dark, 255, self.batch)

        utils.draw_rectangle(
            round(x), round(y + edges),
            round(edges), round(cell_size - 2 * edges), light_dark, 255, self.batch)
        utils.draw_triangle(
            round(x), round(y),
            round(x), round(y + edges),
            round(x + edges), round(y + edges),
            light_dark, 255, self.batch)
        utils.draw_triangle(
            round(x), round(y + cell_size),
            round(x), round(y + cell_size - edges),
            round(x + edges), round(y + cell_size - edges),
            light_dark, 255, self.batch)

        utils.draw_rectangle(
            round(x + cell_size - edges), round(y + edges),
            round(edges), round(cell_size - 2 * edges), light_dark, 255, self.batch)
        utils.draw_triangle(
            round(x + cell_size), round(y),
            round(x + cell_size), round(y + edges),
            round(x + cell_size - edges), round(y + edges),
            light_dark, 255, self.batch)
        utils.draw_triangle(
            round(x + cell_size), round(y + cell_size),
            round(x + cell_size), round(y + cell_size - edges),
            round(x + cell_size - edges), round(y + cell_size - edges),
            light_dark, 255, self.batch)

        utils.draw_rectangle(
            round(x + edges), round(y + edges),
            round(cell_size - 2 * edges), round(cell_size - 2 * edges), color, 255, self.batch)
