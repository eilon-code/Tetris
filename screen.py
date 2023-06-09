import time

import pyglet
from pyglet.gl import *
from pyglet.media import StaticSource

import utils
from tetris import *


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_size = 24
        self.outer_cell_size = 24
        self.tetris_game = TetrisGame(columns=10, rows=20, next_pieces_reveals=5)
        self.tetris_game.initialize()

        self.is_fast_mode = False
        self.was_direction_0 = True
        self.direction_x_step = 0
        self.iteration = 0
        self.extra_frames_help = 2
        self.iterations_blocked = 0

        self.batch = pyglet.graphics.Batch()
        self.grid_lines = []
        self.grid_cells = []
        self.add_grid_to_batch()
        self.clear_grid()

        self.extra_graphics = []
        self.extra_graphics_texts = {}
        self.add_extra_graphics()

        self.outer_pieces_graphics = []
        self.add_outer_pieces_to_batch()
        self.clear_outer_pieces()

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
        self.elements_to_draw = []
        self.texts_to_draw = []

        background_color = [150, 150, 150, 255]
        background_color = [i / 255 for i in background_color]
        glClearColor(*background_color)

        self.background_sound = StaticSource(pyglet.media.load('resources/Tetris.mp3'))
        self.popping_sound = StaticSource(pyglet.media.load('resources/clear.wav'))
        self.force_down_sound = StaticSource(pyglet.media.load('resources/SFX_PieceFall.ogg'))

        self.music_player = utils.play_audio(self.background_sound, volume=0.03, loop=True)
        self.is_sound_on = True
        self.sound_rectangle = utils.draw_rectangle(
            x=self.width / 10, y=self.height / 10, width=self.width / 15, height=self.width / 15,
            color=(255, 255, 255), batch=self.batch)

        self.sound_icons = {
            True: pyglet.image.load("resources/sound_on.png"),
            False: pyglet.image.load("resources/sound_off.png")
        }
        self.sound_sprite = pyglet.sprite.Sprite(img=self.sound_icons[self.is_sound_on], batch=self.batch,
                                                 x=self.sound_rectangle.x, y=self.sound_rectangle.y)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            self.direction_x_step = -1
            self.tetris_game.move_piece_x_steps(self.direction_x_step)
        elif symbol == pyglet.window.key.RIGHT:
            self.direction_x_step = 1
            self.tetris_game.move_piece_x_steps(self.direction_x_step)
        elif symbol == pyglet.window.key.UP:
            self.tetris_game.rotate_piece_90(False)
        elif symbol == pyglet.window.key.Z:
            self.tetris_game.rotate_piece_90(True)
        elif symbol == pyglet.window.key.SPACE:
            if self.is_sound_on and not self.tetris_game.has_game_ended:
                utils.play_audio(self.force_down_sound)
            self.tetris_game.force_down()
        elif symbol == pyglet.window.key.TAB:
            self.tetris_game.switch_hold()
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
        if (self.defeat_button.release() or self.award_button.release()) and self.tetris_game.has_game_ended:
            self.clear_grid()
            self.clear_outer_pieces()
            self.tetris_game.initialize()

    def on_mouse_press(self, x, y, button, modifiers):
        self.defeat_button.click(x, y)
        self.award_button.click(x, y)

        if self.sound_rectangle.x < x < self.sound_rectangle.x + self.sound_rectangle.width and \
                self.sound_rectangle.y < y < self.sound_rectangle.y + self.sound_rectangle.height:
            self.is_sound_on = not self.is_sound_on
            if self.is_sound_on:
                self.music_player.play()
            else:
                self.music_player.pause()

    def on_mouse_motion(self, x, y, dx, dy):
        self.defeat_button.update_mouse_movement(x, y, dx, dy)
        self.award_button.update_mouse_movement(x, y, dx, dy)

        if self.sound_rectangle.x < x < self.sound_rectangle.x + self.sound_rectangle.width and \
                self.sound_rectangle.y < y < self.sound_rectangle.y + self.sound_rectangle.height:
            self.change_mouse_curser('hand_cursor')
        else:
            self.change_mouse_curser()

    def on_draw(self):
        start_time = time.time()
        self.clear()  # Clear the window
        self.sound_sprite.image = self.sound_icons[self.is_sound_on]

        clear_time = time.time()

        self.update_score()
        grid_time = time.time()

        self.draw_tetris_piece_to_grid(self.tetris_game.get_drop_mark(), opacity=80, outer_opacity=40)
        # self.draw_pieces_to_grid()
        self.draw_tetris_grid_pieces()
        grid_pieces_time = time.time()

        self.draw_next_pieces()
        self.draw_hold_piece()
        out_pieces_time = time.time()

        if self.tetris_game.has_game_ended:
            if self.tetris_game.score <= self.tetris_game.best_score:
                self.draw_defeat()
            else:
                self.draw_award()

        message_time = time.time()
        self.batch.draw()

        self.clear_grid()
        batch_time = time.time()

        for text in self.extra_graphics_texts.values():
            text.draw()

        while len(self.texts_to_draw) > 0:
            self.texts_to_draw.pop(0).draw()
        texts_time = time.time()

        while len(self.elements_to_draw) > 0:
            self.elements_to_draw.pop(0)
        end_time = time.time()

        if end_time - start_time > 0.06:
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
        start_time = time.time()

        if self.iteration % 2 == 0:
            if self.direction_x_step != 0 and not self.was_direction_0:
                self.tetris_game.move_piece_x_steps(self.direction_x_step)
            self.was_direction_0 = self.direction_x_step == 0
        elif self.iteration % 3 == 0:
            if self.tetris_game.check_user_piece_down() or self.iterations_blocked >= self.extra_frames_help:
                self.tetris_game.render()
                self.iterations_blocked = 0
            else:
                self.iterations_blocked += 1
        else:
            if self.iteration % 3 == 2:
                some_rows_popped = self.tetris_game.pop_full_rows()
                if some_rows_popped and self.is_sound_on:
                    utils.play_audio(self.popping_sound, volume=0.3)
            if self.is_fast_mode:
                self.tetris_game.move_down_user_piece()

        self.iteration += 1
        self.iteration %= 12

        end_time = time.time()
        total_time = end_time - start_time
        if total_time > 1 / 200.0:
            print("--------------------------------------")
            print(f"Update Over-run: {total_time}")
            print("--------------------------------------")

    def change_mouse_curser(self, cursor_key='default_cursor'):
        cursors = {
            'default_cursor': self.get_system_mouse_cursor(self.CURSOR_DEFAULT),
            'text_cursor': self.get_system_mouse_cursor(self.CURSOR_TEXT),
            'help_cursor': self.get_system_mouse_cursor(self.CURSOR_HELP),
            'crosshair_cursor': self.get_system_mouse_cursor(self.CURSOR_CROSSHAIR),
            'no_cursor': self.get_system_mouse_cursor(self.CURSOR_NO),
            'size_cursor': self.get_system_mouse_cursor(self.CURSOR_SIZE),
            'wait_cursor': self.get_system_mouse_cursor(self.CURSOR_WAIT),
            'wait_arrow_cursor': self.get_system_mouse_cursor(self.CURSOR_WAIT_ARROW),
            'hand_cursor': self.get_system_mouse_cursor(self.CURSOR_HAND)
        }

        self.set_mouse_cursor(cursors[cursor_key])

    def add_grid_to_batch(self):
        x_center = self.width / 2
        y_center = self.height / 2

        x_start = round(x_center - (self.tetris_game.columns / 2) * self.cell_size)
        x_end = round(x_center + (self.tetris_game.columns / 2) * self.cell_size)

        y_start = round(y_center - (self.tetris_game.rows / 2) * self.cell_size)
        y_end = round(y_center + (self.tetris_game.rows / 2) * self.cell_size)

        self.grid_lines.append(utils.draw_rectangle(x_start, y_start, x_end - x_start, y_end - y_start,
                                                    (0, 0, 0), batch=self.batch))

        # for x in range(x_start, x_end + 1, self.cell_size):
        #     self.grid_lines.append(utils.draw_line(x, y_start, x, y_end, (0, 0, 0), 2, batch=self.batch))
        #
        # for y in range(y_start, y_end + 1, self.cell_size):
        #     self.grid_lines.append(utils.draw_line(x_start, y, x_end, y, (0, 0, 0), 2, batch=self.batch))

        for row in range(self.tetris_game.rows):
            for col in range(self.tetris_game.columns):
                self.grid_cells.append([])
                self.add_piece_rectangle_to_batch(
                    round(x_start + col * self.cell_size),
                    round(y_start + row * self.cell_size), (255, 255, 255), self.cell_size, self.grid_cells[-1])

    def draw_pieces_to_grid(self):
        for piece in self.tetris_game.grid_pieces:
            self.draw_tetris_piece_to_grid(piece)

    def update_score(self):
        self.extra_graphics_texts['score'].text = f"Score: {self.tetris_game.score}"
        self.extra_graphics_texts['best_score'].text = f"Best Score: {self.tetris_game.best_score}"

    def draw_next_pieces(self):
        start_x = self.width // 2 + self.cell_size * (self.tetris_game.columns // 2 + 1)
        start_y = self.height // 2 + self.cell_size * (self.tetris_game.rows // 2)

        for i in range(min(self.tetris_game.next_pieces_reveals, len(self.tetris_game.next_pieces))):
            piece_to_draw = self.tetris_game.next_pieces[i]
            self.draw_outer_tetris_piece(piece_to_draw, i,
                                         start_x + self.cell_size * 2.25,
                                         start_y -
                                         (self.cell_size + self.outer_cell_size) * 2 - self.outer_cell_size * 3 * i,
                                         )

    def draw_hold_piece(self):
        start_x = self.width // 2 - self.cell_size * (self.tetris_game.columns // 2 + 7)
        start_y = self.height // 2 + self.cell_size * (self.tetris_game.rows // 2)

        if self.tetris_game.hold_piece is not None:
            self.draw_outer_tetris_piece(self.tetris_game.hold_piece, -1,
                                         start_x + self.cell_size * 2.25,
                                         start_y - (self.cell_size + self.outer_cell_size) * 2)

    def draw_defeat(self):
        start_x = self.width // 2 - self.cell_size * (self.tetris_game.columns // 2 + 6)
        start_y = self.height // 2 + self.cell_size * (self.tetris_game.rows // 2 - 2)

        self.elements_to_draw.append(utils.draw_rectangle(start_x, start_y,
                                                          self.cell_size * (self.tetris_game.columns + 12),
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
        start_x = self.width // 2 - self.cell_size * (self.tetris_game.columns // 2 + 6)
        start_y = self.height // 2 + self.cell_size * (self.tetris_game.rows // 2 - 2)

        self.elements_to_draw.append(utils.draw_rectangle(start_x, start_y,
                                                          self.cell_size * (self.tetris_game.columns + 12),
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

    def draw_outer_tetris_piece(self, piece, piece_index, x, y):
        y_min = 0
        for node in piece.relative_nodes:
            y_min = min(node.y, y_min)
        for node_index in range(len(piece.relative_nodes)):
            bright = [round(0.6 * i + 0.4 * 255) for i in piece.color]
            light_dark = [round(0.9 * i + 0.1 * 0) for i in piece.color]
            dark = [round(0.7 * i + 0.3 * 0) for i in piece.color]

            graphics_node = self.outer_pieces_graphics[piece_index][node_index]
            for i in range(len(graphics_node)):
                graphics_node[i].anchor_position = \
                    (
                        -round(x + piece.relative_nodes[node_index].x * self.outer_cell_size),
                        -round(y + (piece.relative_nodes[node_index].y - y_min) * self.outer_cell_size)
                    )
                graphics_node[i].opacity = 255
                if i < 3:
                    graphics_node[i].color = bright
                elif i < 6:
                    graphics_node[i].color = dark
                elif i < 12:
                    graphics_node[i].color = light_dark
                else:
                    graphics_node[i].color = piece.color

    def add_piece_rectangle_to_batch(self, x, y, color, cell_size, array):
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

    def draw_tetris_piece_to_grid(self, piece, opacity=255, outer_opacity=255):
        if piece is not None:
            for node in piece.nodes:
                if round(node.y) < self.tetris_game.rows:
                    cell = self.grid_cells[round(node.y) * self.tetris_game.columns + round(node.x)]
                    bright = [round(0.6 * i + 0.4 * 255) for i in piece.color]
                    light_dark = [round(0.9 * i + 0.1 * 0) for i in piece.color]
                    dark = [round(0.7 * i + 0.3 * 0) for i in piece.color]

                    for i in range(len(cell)):
                        if i == len(cell) - 1:
                            cell[i].opacity = opacity
                        else:
                            cell[i].opacity = outer_opacity
                        if i < 3:
                            cell[i].color = bright
                        elif i < 6:
                            cell[i].color = dark
                        elif i < 12:
                            cell[i].color = light_dark
                        else:
                            cell[i].color = piece.color

    def draw_tetris_grid_pieces(self, opacity=255):
        for row in range(self.tetris_game.rows):
            for column in range(self.tetris_game.columns):
                if self.tetris_game.grid[row][column] is not None:
                    node_color = self.tetris_game.grid[row][column].color
                    cell = self.grid_cells[row * self.tetris_game.columns + column]
                    bright = [round(0.6 * i + 0.4 * 255) for i in node_color]
                    light_dark = [round(0.9 * i + 0.1 * 0) for i in node_color]
                    dark = [round(0.7 * i + 0.3 * 0) for i in node_color]

                    for i in range(len(cell)):
                        cell[i].opacity = opacity
                        if i < 3:
                            cell[i].color = bright
                        elif i < 6:
                            cell[i].color = dark
                        elif i < 12:
                            cell[i].color = light_dark
                        else:
                            cell[i].color = node_color

    def clear_grid(self):
        for cell in self.grid_cells:
            for shape in cell:
                shape.opacity = 0

    def add_extra_graphics(self):
        start_x = self.width // 2 + round(self.cell_size * (self.tetris_game.columns / 2 + 1))
        start_y = self.height // 2 + round(self.cell_size * (self.tetris_game.rows / 2))

        self.extra_graphics.append(utils.draw_rectangle(
            start_x, start_y,
            self.cell_size * 6, -self.cell_size * 2 - self.outer_cell_size * self.tetris_game.next_pieces_reveals * 3,
            (230, 230, 230), 255, self.batch))
        self.extra_graphics_texts['next'] = pyglet.text.Label(f"Next Pieces:", font_name='David', font_size=20,
                                                              x=start_x + round(self.cell_size * 3),
                                                              y=start_y - self.cell_size // 4,
                                                              anchor_x='center', anchor_y='top', color=(0, 0, 0, 255))

        self.extra_graphics.append(
            utils.draw_rectangle(start_x - round(self.cell_size * (self.tetris_game.columns + 8)), start_y,
                                 self.cell_size * 6,
                                 -self.cell_size * 2 - self.outer_cell_size * 3,
                                 (230, 230, 230), 255,
                                 self.batch))
        self.extra_graphics_texts['hold'] = pyglet.text.Label(f"Hold Piece:", font_name='David', font_size=20,
                                                              x=round(
                                                                  start_x - self.cell_size * (
                                                                          self.tetris_game.columns + 5)),
                                                              y=round(start_y - self.cell_size / 4),
                                                              anchor_x='center', anchor_y='top', color=(0, 0, 0, 255))

        self.extra_graphics_texts['score'] = pyglet.text.Label(f"Score: {self.tetris_game.score}",
                                                               font_name='Times New Roman',
                                                               font_size=36,
                                                               x=self.width // 2,
                                                               y=self.height // 2 + self.cell_size * (
                                                                       self.tetris_game.rows // 2 + 3),
                                                               anchor_x='center', anchor_y='center')
        self.extra_graphics_texts['best_score'] = pyglet.text.Label(f"Best Score: {self.tetris_game.best_score}",
                                                                    font_name='Times New Roman',
                                                                    font_size=18,
                                                                    x=self.width // 2,
                                                                    y=self.height // 2 + round(
                                                                        self.cell_size * (
                                                                                self.tetris_game.rows // 2 + 1)),
                                                                    anchor_x='center', anchor_y='center')

    def add_outer_pieces_to_batch(self):
        for i in range(self.tetris_game.next_pieces_reveals + 1):
            self.outer_pieces_graphics.append([])
            for j in range(Piece.nodes_num):
                self.outer_pieces_graphics[-1].append([])
                self.add_piece_rectangle_to_batch(0, 0, (255, 255, 255), self.outer_cell_size,
                                                  self.outer_pieces_graphics[-1][-1])

    def clear_outer_pieces(self):
        for piece_graphics in self.outer_pieces_graphics:
            for cell_graphics in piece_graphics:
                for shape in cell_graphics:
                    shape.opacity = 0
