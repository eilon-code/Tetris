import math
import random
import time

from utils import Point


class TetrisGame:
    hold_piece = None
    columns = 10
    rows = 20
    score = 0
    best_score = -1
    pieces = []
    next_reveals = 5
    next_pieces = []
    grid = []
    is_game_running = False

    @staticmethod
    def initialize():
        TetrisGame.best_score = max(TetrisGame.best_score, TetrisGame.score)
        TetrisGame.score = 0
        TetrisGame.is_game_running = True
        TetrisGame.hold_piece = None
        for i in range(len(TetrisGame.pieces))[::-1]:
            TetrisGame.pieces.pop(i)
        for i in range(len(TetrisGame.next_pieces))[::-1]:
            TetrisGame.next_pieces.pop(i)

        for row in range(len(TetrisGame.grid))[::-1]:
            for column in range(TetrisGame.columns)[::-1]:
                TetrisGame.grid[row].pop(column)
            TetrisGame.grid.pop(row)

        for row in range(TetrisGame.rows):
            TetrisGame.grid.append([])
            for column in range(TetrisGame.columns):
                TetrisGame.grid[row].append(-1)

    @staticmethod
    def render(window=None):
        start_time = time.time()
        if not TetrisGame.is_game_running:
            return
        TetrisGame.pop_full_rows()
        TetrisGame.move_all_down()
        some_piece_of_user = False
        for piece in TetrisGame.pieces:
            if piece.is_piece_of_user:
                some_piece_of_user = True

        if not some_piece_of_user:
            game_ended = False
            for piece in TetrisGame.pieces:
                if game_ended:
                    continue
                for node in piece.nodes_centers:
                    if round(node.y) >= TetrisGame.rows - 1:
                        game_ended = True
            if not game_ended:
                TetrisGame.add_piece()
            else:
                TetrisGame.is_game_running = False
                if window is not None:
                    window.is_game_running = False

        end_time = time.time()
        total_time = end_time - start_time
        if total_time > 1 / 120.0:
            print(f"Render Over-run: {total_time}")

    @staticmethod
    def rotate_piece_90(clockwise):
        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].rotate_90_degrees(clockwise)

    @staticmethod
    def move_x_steps(x):
        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].move_on_x_axis(x)

    @staticmethod
    def move_all_down():
        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].moved_down = False

        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].move_down()

    @staticmethod
    def move_down_user_pieces():
        for i in range(len(TetrisGame.pieces)):
            if TetrisGame.pieces[i].is_piece_of_user:
                TetrisGame.pieces[i].moved_down = False

        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].move_down()

    @staticmethod
    def check_user_pieces_down():
        for i in range(len(TetrisGame.pieces)):
            if TetrisGame.pieces[i].is_piece_of_user:
                if TetrisGame.pieces[i].min_y > 0:
                    if not TetrisGame.pieces[i].check_move_down():
                        return False
        return True

    @staticmethod
    def force_down(window):
        while TetrisGame.is_game_running:
            piece = TetrisGame.next_pieces[0]
            TetrisGame.render(window)
            if piece != TetrisGame.next_pieces[0]:
                break

    @staticmethod
    def pop_full_rows():
        rows_to_pop = []
        for i in range(TetrisGame.rows):
            if -1 in TetrisGame.grid[i]:
                continue

            row_i_to_pop = True
            for j in range(TetrisGame.columns):
                if not TetrisGame.pieces[TetrisGame.grid[i][j]].above_ground:
                    row_i_to_pop = False

            if row_i_to_pop:
                rows_to_pop.append(i)

        if len(rows_to_pop) > 0:
            for i in range(len(TetrisGame.pieces)):
                for row in rows_to_pop:
                    TetrisGame.pieces[i].split_in_popped_row(row)

            for i in range(len(TetrisGame.pieces))[::-1]:
                if len(TetrisGame.pieces[i].nodes) == 0:
                    TetrisGame.pieces.pop(i)
                    if i == len(TetrisGame.pieces):
                        continue
                    for row in range(TetrisGame.rows):
                        for column in range(TetrisGame.columns):
                            if TetrisGame.grid[row][column] > i:
                                TetrisGame.grid[row][column] -= 1

            for i in range(len(TetrisGame.pieces)):
                if TetrisGame.pieces[i].above_ground and TetrisGame.pieces[i].min_y > min(rows_to_pop):
                    TetrisGame.pieces[i].above_ground = False

            for i in rows_to_pop:
                for j in range(TetrisGame.columns):
                    TetrisGame.grid[i][j] = -1

            if len(rows_to_pop) == 1:
                TetrisGame.score += 40
            elif len(rows_to_pop) == 2:
                TetrisGame.score += 100
            elif len(rows_to_pop) == 3:
                TetrisGame.score += 300
            else:
                TetrisGame.score += 1200

    @staticmethod
    def add_piece(piece=None):
        while len(TetrisGame.next_pieces) < TetrisGame.next_reveals:
            TetrisGame.generate_next_piece()

        TetrisGame.generate_next_piece(piece)
        next_piece = TetrisGame.next_pieces.pop(0)
        next_piece.is_active = True
        TetrisGame.pieces.append(next_piece)

    @staticmethod
    def generate_next_piece(piece=None):
        angle = 0   # random.randint(0, 3) * 90
        hold_piece = piece is not None

        if piece is None:
            tetris_pieces_types = [LinePiece, LBlock, ReverseLBlock, Square, Squiggly, ReverseSquiggly, TBlock]
            index = random.randint(0, len(tetris_pieces_types) - 1)
            piece = tetris_pieces_types[index](TetrisGame.columns // 2, TetrisGame.rows, angle, False)
            if index == 0 or index == 3:
                piece.center_x += 0.5
                piece.center_y += 0.5

        min_x = TetrisGame.columns - 1
        max_x = 0
        min_y = TetrisGame.rows

        for node in piece.nodes_centers:
            if round(node.x) > max_x:
                max_x = round(node.x)
            if round(node.x) < min_x:
                min_x = round(node.x)
            if round(node.y) < min_y:
                min_y = round(node.y)

        piece.center_y += TetrisGame.rows - min_y
        width = max_x - min_x + 1
        shift = (TetrisGame.columns-width) // 2     # random.randint(0, TetrisGame.columns - 1 - width)
        piece.center_x += shift - min_x
        piece.update()

        if hold_piece:
            TetrisGame.next_pieces.insert(0, piece)
        else:
            TetrisGame.next_pieces.append(piece)

    @staticmethod
    def switch_hold():
        index_to_switch = -1
        for i in range(len(TetrisGame.pieces)):
            if index_to_switch != -1:
                continue
            if TetrisGame.pieces[i].is_piece_of_user:
                index_to_switch = i

        for row in range(TetrisGame.rows):
            for column in range(TetrisGame.columns):
                if TetrisGame.grid[row][column] == index_to_switch:
                    TetrisGame.grid[row][column] = -1

        piece_to_hold = TetrisGame.pieces.pop(index_to_switch)
        TetrisGame.add_piece(TetrisGame.hold_piece)
        TetrisGame.hold_piece = None
        TetrisGame.hold_piece = piece_to_hold


class Piece:
    nodes_num = 4

    def __init__(self, center_x, center_y, color, nodes, angle, is_active):
        self.color = color
        self.is_piece_of_user = True
        self.above_ground = False
        self.moved_down = False
        self.center_x = center_x
        self.center_y = center_y
        self.min_y = 0
        self.max_y = TetrisGame.rows
        self.min_x = 0
        self.max_x = TetrisGame.columns

        self.nodes = nodes
        self.angle = angle
        self.nodes_centers = []
        self.is_active = is_active

        self.update()
        if self.is_active:
            TetrisGame.pieces.append(self)

    def update(self):
        self.min_y = TetrisGame.rows
        self.max_y = -1
        self.min_x = TetrisGame.columns
        self.max_x = -1
        for i in range(len(self.nodes_centers))[::-1]:
            self.nodes_centers.pop(i)
        for node in self.nodes:
            radius = math.sqrt(node.x ** 2 + node.y ** 2)
            theta = math.atan2(node.y, node.x)

            node_center_x = radius * math.cos(math.radians(self.angle) + theta)
            node_center_y = radius * math.sin(math.radians(self.angle) + theta)
            self.nodes_centers.append(Point(self.center_x + node_center_x, self.center_y + node_center_y))
            if round(self.center_y + node_center_y) < self.min_y:
                self.min_y = round(self.center_y + node_center_y)
            if round(self.center_y + node_center_y) > self.max_y:
                self.max_y = round(self.center_y + node_center_y)
            if round(self.center_x + node_center_x) < self.min_x:
                self.min_x = round(self.center_x + node_center_x)
            if round(self.center_x + node_center_x) > self.max_x:
                self.max_x = round(self.center_x + node_center_x)

    def move_down(self):
        if self.moved_down or self.above_ground or (not self.is_active):
            return False
        self.moved_down = True

        for node in self.nodes_centers:
            if round(node.y) >= TetrisGame.rows:
                continue
            if round(node.y) < 1:
                self.above_ground = True
                if self.is_piece_of_user:
                    self.is_piece_of_user = False
                return False  # unable to move down

            index_of_piece_down = TetrisGame.grid[round(node.y - 1)][round(node.x)]
            if index_of_piece_down != -1:
                piece_down = TetrisGame.pieces[index_of_piece_down]
                if piece_down != self and not piece_down.move_down():
                    self.above_ground = True
                    if self.is_piece_of_user:
                        self.is_piece_of_user = False
                    return False  # unable to move down

        index_of_piece = TetrisGame.pieces.index(self)
        for node in self.nodes_centers:
            if round(node.y) >= TetrisGame.rows:
                continue
            TetrisGame.grid[round(node.y)][round(node.x)] = -1
        self.center_y -= 1
        self.update()
        for node in self.nodes_centers:
            if round(node.y) >= TetrisGame.rows:
                continue
            TetrisGame.grid[round(node.y)][round(node.x)] = index_of_piece
        return True

    def check_move_down(self):
        if self.above_ground or (not self.is_active):
            return False

        for node in self.nodes_centers:
            if round(node.y) >= TetrisGame.rows:
                continue
            if round(node.y) < 1:
                return False  # unable to move down

            index_of_piece_down = TetrisGame.grid[round(node.y - 1)][round(node.x)]
            if index_of_piece_down != -1:
                piece_down = TetrisGame.pieces[index_of_piece_down]
                if piece_down != self and not piece_down.check_move_down():
                    return False  # unable to move down
        return True

    def move_on_x_axis(self, step):
        if self.is_active and self.is_piece_of_user:
            for node in self.nodes_centers:
                if round(node.x) + step < 0 or round(node.x) + step >= TetrisGame.columns:
                    return False  # illegal move

                if round(node.y) < TetrisGame.rows:
                    if TetrisGame.grid[round(node.y)][round(node.x + step)] != -1:
                        if TetrisGame.pieces[TetrisGame.grid[round(node.y)][round(node.x + step)]] != self:
                            return False  # illegal move

            index_of_piece = TetrisGame.pieces.index(self)
            for node in self.nodes_centers:
                if round(node.y) >= TetrisGame.rows:
                    continue
                TetrisGame.grid[round(node.y)][round(node.x)] = -1
            self.center_x += step
            self.update()
            for node in self.nodes_centers:
                if round(node.y) >= TetrisGame.rows:
                    continue
                TetrisGame.grid[round(node.y)][round(node.x)] = index_of_piece

            return True
        return False

    def rotate_90_degrees(self, clockwise):
        if self.is_active and self.is_piece_of_user:
            previous_angle = self.angle
            if clockwise:
                self.angle += 90
            else:
                self.angle -= 90
            self.update()

            if self.min_y < 0:
                self.angle = previous_angle
                self.update()
                return False  # illegal move

            x_offset = 0
            if self.max_x > TetrisGame.columns - 1:
                x_offset = TetrisGame.columns - 1 - self.max_x
            if self.min_x < 0:
                x_offset = 0 - self.min_x

            for node in self.nodes_centers:
                if round(node.y) >= TetrisGame.rows:
                    continue
                if not 0 <= round(node.x + x_offset) < TetrisGame.columns:
                    self.angle = previous_angle
                    self.update()
                    return False  # illegal move
                if TetrisGame.grid[round(node.y)][round(node.x + x_offset)] != -1:
                    if TetrisGame.pieces[TetrisGame.grid[round(node.y)][round(node.x + x_offset)]] != self:
                        self.angle = previous_angle
                        self.update()
                        return False  # illegal move

            self.angle, previous_angle = previous_angle, self.angle
            self.update()
            index_of_piece = TetrisGame.pieces.index(self)
            for node in self.nodes_centers:
                if round(node.y) >= TetrisGame.rows:
                    continue
                TetrisGame.grid[round(node.y)][round(node.x)] = -1
            self.angle, previous_angle = previous_angle, self.angle
            self.center_x += x_offset
            self.update()
            for node in self.nodes_centers:
                if round(node.y) >= TetrisGame.rows:
                    continue
                TetrisGame.grid[round(node.y)][round(node.x)] = index_of_piece
            return True
        return False

    def split_in_popped_row(self, row):
        if row < self.min_y or row > self.max_y:
            pass    # row is not related to piece
        split_nodes = []
        removed_nodes = []
        for i in range(len(self.nodes_centers)):
            if round(self.nodes_centers[i].y) < row:
                split_nodes.append(i)
            elif round(self.nodes_centers[i].y) == row:
                removed_nodes.append(i)

        split_piece = Piece(self.center_x, self.center_y, self.color,
                            [self.nodes[i] for i in split_nodes], self.angle, self.is_active)
        split_piece.is_piece_of_user = False

        for i in split_nodes:
            TetrisGame.grid[round(self.nodes_centers[i].y)][round(self.nodes_centers[i].x)] = len(TetrisGame.pieces) - 1
        for i in sorted(removed_nodes + split_nodes)[::-1]:
            self.nodes.pop(i)
        self.update()
        self.above_ground = False


class LinePiece(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (51, 153, 255)
        nodes = [Point(1.5, 0.5), Point(0.5, 0.5), Point(-0.5, 0.5), Point(-1.5, 0.5)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class LBlock(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (255, 128, 0)
        nodes = [Point(-1, 0), Point(0, 0), Point(1, 0), Point(1, 1)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class ReverseLBlock(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (0, 0, 204)
        nodes = [Point(-1, 1), Point(-1, 0), Point(0, 0), Point(1, 0)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class Square(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (238, 238, 7)
        nodes = [Point(0.5, 0.5), Point(0.5, -0.5), Point(-0.5, 0.5), Point(-0.5, -0.5)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class Squiggly(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (255, 0, 0)
        nodes = [Point(-1, 1), Point(0, 1), Point(0, 0), Point(1, 0)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class ReverseSquiggly(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (0, 204, 0)
        nodes = [Point(-1, 0), Point(0, 0), Point(0, 1), Point(1, 1)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class TBlock(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (102, 0, 204)
        nodes = [Point(-1, 0), Point(0, 0), Point(0, 1), Point(1, 0)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)
