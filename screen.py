import time

import pyglet
from pyglet.gl import *

import utils
from tetris import *


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_size = 24
        self.outer_cell_size = 24
        self.is_game_running = True
        self.is_fast_mode = False
        self.was_direction_0 = True
        self.direction_x_step = 0
        self.iteration = 0
        self.extra_frames_help = 2
        self.i = 0

        self.batch = pyglet.graphics.Batch()
        self.grid_cells = []

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
        self.base_elements_to_draw = []
        self.elements_to_draw = []
        self.texts_to_draw = []

        self.add_grid_to_batch()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            self.direction_x_step = -1
            TetrisGame.move_x_steps(self.direction_x_step)
        elif symbol == pyglet.window.key.RIGHT:
            self.direction_x_step = 1
            TetrisGame.move_x_steps(self.direction_x_step)
        elif symbol == pyglet.window.key.UP:
            TetrisGame.rotate_piece_90(False)
        elif symbol == pyglet.window.key.Z:
            TetrisGame.rotate_piece_90(True)
        elif symbol == pyglet.window.key.SPACE:
            TetrisGame.force_down(self)
        elif symbol == pyglet.window.key.TAB:
            TetrisGame.switch_hold()
        elif symbol == pyglet.window.key.DOWN:
            self.is_fast_mode = True
            pass
        else:
            pass

        self.on_draw()

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.DOWN:
            self.is_fast_mode = False
        elif symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.RIGHT:
            self.direction_x_step = 0

    def on_mouse_release(self, x, y, button, modifiers):
        if (self.defeat_button.release() or self.award_button.release()) and not self.is_game_running:
            TetrisGame.initialize()
            self.is_game_running = True

    def on_mouse_press(self, x, y, button, modifiers):
        self.defeat_button.click(x, y)
        self.award_button.click(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        self.defeat_button.update_mouse_movement(x, y, dx, dy)
        self.award_button.update_mouse_movement(x, y, dx, dy)

    def on_draw(self):
        start_time = time.time()
        self.clear()  # Clear the window
        clear_time = time.time()

        self.change_mouse_curser()
        self.draw_score()
        grid_time = time.time()

        self.draw_pieces_to_grid()
        grid_pieces_time = time.time()

        self.draw_next_pieces()
        self.draw_hold_piece()
        out_pieces_time = time.time()

        if not self.is_game_running:
            if TetrisGame.score <= TetrisGame.best_score:
                self.draw_defeat()
            else:
                self.draw_award()

        message_time = time.time()
        self.batch.draw()

        self.clear_grid()
        batch_time = time.time()

        while len(self.texts_to_draw) > 0:
            self.texts_to_draw.pop(0).draw()
        texts_time = time.time()

        while len(self.elements_to_draw) > 0:
            self.elements_to_draw.pop(0)
        end_time = time.time()

        if end_time - start_time > 0.1:
            print("----------------- time overran ------------------")
            print("Details:")
            print(f"clear_time: {clear_time - start_time}")
            print(f"grid_time: {grid_time - clear_time}")
            print(f"grid_pieces_time: {grid_pieces_time - grid_time}")
            print(f"out_pieces_time: {out_pieces_time - grid_pieces_time}")
            print(f"message_time: {message_time - out_pieces_time}")
            print(f"batch_time: {batch_time - message_time}")
            print(f"texts_time: {texts_time - batch_time}")
            print(f"end_time: {end_time - texts_time}")
            print(f"total_time: {end_time - start_time}")

    def update(self, dt):
        if self.direction_x_step != 0:
            if not self.was_direction_0:
                TetrisGame.move_x_steps(self.direction_x_step)
        self.was_direction_0 = self.direction_x_step == 0
        if TetrisGame.check_user_pieces_down() or self.i > self.extra_frames_help:
            if self.iteration % 4 == 0 or self.i > self.extra_frames_help:
                TetrisGame.render(self)
                self.iteration = 0
            if self.iteration % 4 == 2 and self.is_fast_mode:
                TetrisGame.move_down_user_pieces()

            self.i = 0
        else:
            self.i += 1
            if self.is_fast_mode:
                self.i += 1

        self.iteration += 1
        self.iteration %= 4

    def change_mouse_curser(self):
        default_cursor = self.get_system_mouse_cursor(self.CURSOR_DEFAULT)
        # text_cursor = self.get_system_mouse_cursor(self.CURSOR_TEXT)
        # help_cursor = self.get_system_mouse_cursor(self.CURSOR_HELP)
        # crosshair_cursor = self.get_system_mouse_cursor(self.CURSOR_CROSSHAIR)
        # no_cursor = self.get_system_mouse_cursor(self.CURSOR_NO)
        # size_cursor = self.get_system_mouse_cursor(self.CURSOR_SIZE)
        # wait_cursor = self.get_system_mouse_cursor(self.CURSOR_WAIT)
        # wait_arrow_cursor = self.get_system_mouse_cursor(self.CURSOR_WAIT_ARROW)

        cursor = default_cursor
        self.set_mouse_cursor(cursor)

    def add_grid_to_batch(self):
        x_center = self.width / 2
        y_center = self.height / 2

        x_start = round(x_center - (TetrisGame.columns / 2) * self.cell_size)
        x_end = round(x_center + (TetrisGame.columns / 2) * self.cell_size)

        y_start = round(y_center - (TetrisGame.rows / 2) * self.cell_size)
        y_end = round(y_center + (TetrisGame.rows / 2) * self.cell_size)

        for x in range(x_start, x_end + 1, self.cell_size):
            self.base_elements_to_draw.append(utils.draw_line(x, y_start, x, y_end, (0, 0, 0), 2, 255, self.batch))

        for y in range(y_start, y_end + 1, self.cell_size):
            self.base_elements_to_draw.append(utils.draw_line(x_start, y, x_end, y, (0, 0, 0), 2, 255, self.batch))

        for row in range(TetrisGame.rows):
            for col in range(TetrisGame.columns):
                self.grid_cells.append([])
                self.draw_piece_rectangle(
                    round(x_start + col * self.cell_size),
                    round(y_start + row * self.cell_size), (255, 255, 255), self.cell_size, self.grid_cells[-1])

        for cell in self.grid_cells:
            for shape in cell:
                shape.opacity = 0

    def draw_pieces_to_grid(self):
        for piece in TetrisGame.pieces:
            self.draw_tetris_piece_to_grid(piece, opacity=255)

    def draw_score(self):
        self.texts_to_draw.append(pyglet.text.Label(f"Score: {TetrisGame.score}",
                                                    font_name='Times New Roman',
                                                    font_size=36,
                                                    x=self.width // 2,
                                                    y=self.height // 2 + self.cell_size * (TetrisGame.rows // 2 + 3),
                                                    anchor_x='center', anchor_y='center'))
        self.texts_to_draw.append(pyglet.text.Label(f"Best Score: {TetrisGame.best_score}",
                                                    font_name='Times New Roman',
                                                    font_size=18,
                                                    x=self.width // 2,
                                                    y=self.height // 2 + round(
                                                        self.cell_size * (TetrisGame.rows // 2 + 1)),
                                                    anchor_x='center', anchor_y='center'))

    def draw_next_pieces(self):
        start_x = self.width // 2 + self.cell_size * (TetrisGame.columns // 2 + 1)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2)

        self.elements_to_draw.append(utils.draw_rectangle(
            start_x, start_y,
            self.cell_size * 6, -self.cell_size * 2 - self.outer_cell_size * TetrisGame.next_reveals * 3,
            (230, 230, 230), 255, self.batch))
        self.texts_to_draw.append(pyglet.text.Label(f"Next Pieces:", font_name='David', font_size=20,
                                                    x=start_x + round(self.cell_size * 3),
                                                    y=start_y - self.cell_size // 4,
                                                    anchor_x='center', anchor_y='top', color=(0, 0, 0, 255)))

        for i in range(len(TetrisGame.next_pieces)):
            piece_to_draw = TetrisGame.next_pieces[i]
            self.draw_tetris_piece(piece_to_draw,
                                   start_x + self.cell_size * 2.25,
                                   start_y - (self.cell_size + self.outer_cell_size) * 2 - self.outer_cell_size * 3 * i,
                                   self.outer_cell_size)

    def draw_hold_piece(self):
        start_x = self.width // 2 - self.cell_size * (TetrisGame.columns // 2 + 7)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2)

        self.elements_to_draw.append(
            utils.draw_rectangle(start_x, start_y, self.cell_size * 6, -self.cell_size * 2 - self.outer_cell_size * 3,
                                 (230, 230, 230), 255,
                                 self.batch))
        self.texts_to_draw.append(pyglet.text.Label(f"Hold Piece:", font_name='David', font_size=20,
                                                    x=start_x + round(self.cell_size * 3),
                                                    y=start_y - self.cell_size // 4,
                                                    anchor_x='center', anchor_y='top', color=(0, 0, 0, 255)))

        if TetrisGame.hold_piece is not None:
            self.draw_tetris_piece(TetrisGame.hold_piece,
                                   start_x + self.cell_size * 2.25,
                                   start_y - (self.cell_size + self.outer_cell_size) * 2,
                                   self.outer_cell_size)

    def draw_defeat(self):
        start_x = self.width // 2 - self.cell_size * (TetrisGame.columns // 2 + 6)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2 - 2)

        self.elements_to_draw.append(utils.draw_rectangle(start_x, start_y,
                                                          self.cell_size * (TetrisGame.columns + 12),
                                                          -self.cell_size * 16, (100, 100, 200), 200, self.batch))

        self.texts_to_draw.append(pyglet.text.Label(f"Dear looser, you lost.",
                                                    font_name='David', font_size=24,
                                                    x=start_x + self.cell_size // 2, y=start_y - self.cell_size // 4,
                                                    anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))
        self.texts_to_draw.append(pyglet.text.Label(f"Reasons of loss:",
                                                    font_name='David', font_size=18,
                                                    x=start_x + self.cell_size * 2, y=start_y - self.cell_size * 3,
                                                    anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))
        reasons = [f"1. inability to grasp the shape of the pieces",
                   f"2. lack of thinking skills",
                   f"3. low quality of gaming in general"]

        for i in range(len(reasons)):
            self.texts_to_draw.append(pyglet.text.Label(reasons[i],
                                                        font_name='David', font_size=18,
                                                        x=start_x + self.cell_size * 3,
                                                        y=start_y - self.cell_size * (5 + i * 1.5),
                                                        anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))

        conclusions = [f"Please understand you are unqualified",
                       f"to achieve a new high score and stop playing",
                       f"this game, it's not ment for the likes of you."]

        for i in range(len(conclusions)):
            self.texts_to_draw.append(pyglet.text.Label(conclusions[i],
                                                        font_name='David', font_size=18,
                                                        x=start_x + self.cell_size * 2,
                                                        y=start_y - self.cell_size * (10 + i),
                                                        anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))

        elements, label = self.defeat_button.draw()
        for elem in elements:
            self.elements_to_draw.append(elem)
        self.texts_to_draw.append(label)

    def draw_award(self):
        start_x = self.width // 2 - self.cell_size * (TetrisGame.columns // 2 + 6)
        start_y = self.height // 2 + self.cell_size * (TetrisGame.rows // 2 - 2)

        self.elements_to_draw.append(utils.draw_rectangle(start_x, start_y,
                                                          self.cell_size * (TetrisGame.columns + 12),
                                                          -self.cell_size * 16, (150, 200, 200), 200, self.batch))

        self.texts_to_draw.append(pyglet.text.Label(f"Lucky bastard!, a new high score.",
                                                    font_name='David', font_size=24,
                                                    x=start_x + self.cell_size // 2, y=start_y - self.cell_size // 4,
                                                    anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))
        self.texts_to_draw.append(pyglet.text.Label(f"Assumptions:",
                                                    font_name='David', font_size=18,
                                                    x=start_x + self.cell_size * 2, y=start_y - self.cell_size * 3,
                                                    anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))
        reasons = [f"1. the game isn't that hard",
                   f"2. your score is good relative to yourself alone",
                   f"3. probably you were close to loose earlier"]

        for i in range(len(reasons)):
            self.texts_to_draw.append(pyglet.text.Label(reasons[i],
                                                        font_name='David', font_size=18,
                                                        x=start_x + self.cell_size * 3,
                                                        y=start_y - self.cell_size * (5 + i * 1.5),
                                                        anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))

        conclusions = [f"Please try again I asure you can't score better",
                       f"than this due to the reasons above.",
                       f"You only won yourself by luck."]

        for i in range(len(conclusions)):
            self.texts_to_draw.append(pyglet.text.Label(conclusions[i],
                                                        font_name='David', font_size=18,
                                                        x=start_x + self.cell_size * 2,
                                                        y=start_y - self.cell_size * (10 + i),
                                                        anchor_x='left', anchor_y='top', color=(0, 0, 0, 255)))

        elements, label = self.award_button.draw()
        for elem in elements:
            self.elements_to_draw.append(elem)
        self.texts_to_draw.append(label)

    def draw_tetris_piece(self, piece, x, y, cell_size):
        y_min = 0
        for node in piece.nodes:
            y_min = min(node.y, y_min)
        for node in piece.nodes:
            # self.elements_to_draw.append(utils.draw_rectangle(
            #     round(x + node.x * cell_size),
            #     round(y + (node.y - y_min) * cell_size),
            #     cell_size, cell_size, piece.color, 255, self.main_batch))
            self.draw_piece_rectangle(
                round(x + node.x * cell_size),
                round(y + (node.y - y_min) * cell_size),
                piece.color, cell_size, self.elements_to_draw)

    def draw_piece_rectangle(self, x, y, color, cell_size, array):
        edges = 0.12 * cell_size

        bright = [round(0.6 * i + 0.4 * 255) for i in color]
        light_dark = [round(0.9 * i + 0.1 * 0) for i in color]
        dark = [round(0.7 * i + 0.3 * 0) for i in color]

        array.append(utils.draw_rectangle(
            round(x + edges), round(y + cell_size - edges),
            round(cell_size - 2 * edges), round(edges), bright, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x), round(y + cell_size),
            round(x + edges), round(y + cell_size),
            round(x + edges), round(y + cell_size - edges),
            bright, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x + cell_size), round(y + cell_size),
            round(x + cell_size - edges), round(y + cell_size),
            round(x + cell_size - edges), round(y + cell_size - edges),
            bright, 255, self.batch))

        array.append(utils.draw_rectangle(
            round(x + edges), round(y),
            round(cell_size - 2 * edges), round(edges), dark, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x), round(y),
            round(x + edges), round(y),
            round(x + edges), round(y + edges), dark, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x + cell_size - edges), round(y),
            round(x + cell_size), round(y),
            round(x + cell_size - edges), round(y + edges),
            dark, 255, self.batch))

        array.append(utils.draw_rectangle(
            round(x), round(y + edges),
            round(edges), round(cell_size - 2 * edges), light_dark, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x), round(y),
            round(x), round(y + edges),
            round(x + edges), round(y + edges),
            light_dark, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x), round(y + cell_size),
            round(x), round(y + cell_size - edges),
            round(x + edges), round(y + cell_size - edges),
            light_dark, 255, self.batch))

        array.append(utils.draw_rectangle(
            round(x + cell_size - edges), round(y + edges),
            round(edges), round(cell_size - 2 * edges), light_dark, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x + cell_size), round(y),
            round(x + cell_size), round(y + edges),
            round(x + cell_size - edges), round(y + edges),
            light_dark, 255, self.batch))
        array.append(utils.draw_triangle(
            round(x + cell_size), round(y + cell_size),
            round(x + cell_size), round(y + cell_size - edges),
            round(x + cell_size - edges), round(y + cell_size - edges),
            light_dark, 255, self.batch))

        array.append(utils.draw_rectangle(
            round(x + edges), round(y + edges),
            round(cell_size - 2 * edges), round(cell_size - 2 * edges), color, 255, self.batch))

    def draw_tetris_piece_to_grid(self, piece, opacity):
        for node in piece.nodes_centers:
            if round(node.y) < TetrisGame.rows or (not piece.is_active):
                cell = self.grid_cells[round(node.y)*TetrisGame.columns + round(node.x)]
                bright = [round(0.6 * i + 0.4 * 255) for i in piece.color]
                light_dark = [round(0.9 * i + 0.1 * 0) for i in piece.color]
                dark = [round(0.7 * i + 0.3 * 0) for i in piece.color]

                for i in range(len(cell)):
                    cell[i].opacity = opacity
                    if i < 3:
                        cell[i].color = bright
                    elif i < 6:
                        cell[i].color = dark
                    elif i < 12:
                        cell[i].color = light_dark
                    else:
                        cell[i].color = piece.color

    def clear_grid(self):
        for cell in self.grid_cells:
            for shape in cell:
                shape.opacity = 0
