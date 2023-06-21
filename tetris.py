import math
import random
import time

from utils import Point


class TetrisGame:
    def __init__(self, columns, rows, next_pieces_reveals):
        self.columns = columns
        self.rows = rows
        self.next_pieces_reveals = next_pieces_reveals
        self.has_game_ended = False
        self.score = 0
        self.best_score = -1

        self.user_piece = None
        self.hold_piece = None
        self.next_pieces = []

        self.grid = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.grid_pieces = []

    def initialize(self):
        self.best_score = max(self.best_score, self.score)
        self.has_game_ended = False
        self.score = 0
        self.user_piece = None
        self.hold_piece = None

        while len(self.next_pieces) > 0:
            self.next_pieces.pop(0)

        for row in range(self.rows):
            for column in range(self.columns):
                self.grid[row][column] = None

        while len(self.grid_pieces) > 0:
            self.grid_pieces.pop(0)

    def rotate_piece_90(self, clockwise):
        self.user_piece.rotate_90_degrees(self, clockwise)

    def move_piece_x_steps(self, x):
        if self.user_piece is not None:
            self.user_piece.move_on_x_axis(self, x)

    def move_all_down(self):
        for piece in self.grid_pieces:
            piece.called_move_down = False

        for piece in self.grid_pieces:
            if not piece.called_move_down:
                piece.move_down(self)

        if self.user_piece is not None and self.user_piece.above_ground:
            self.user_piece = None

    def move_down_user_piece(self):
        if self.user_piece is not None and self.user_piece.count_moves_down(self) > 0:
            self.user_piece.move_down(self, False)

    def check_user_piece_down(self):
        return self.user_piece is None or not self.user_piece.check_move_down(self)

    def force_down(self):
        if self.user_piece is not None:
            while self.user_piece.count_moves_down(self) > 0:
                self.move_down_user_piece()
            self.user_piece = None
        self.add_piece()

    def pop_full_rows(self):
        rows_to_pop = []
        for row in range(self.rows):
            if None in self.grid[row]:
                continue

            pop = True
            for column in range(self.columns):
                if not self.grid[row][column].above_ground:
                    pop = False

            if pop:
                rows_to_pop.append(row)

        if len(rows_to_pop) > 0:
            split_pieces = []
            for row in rows_to_pop:
                for piece in self.grid_pieces:
                    split_piece = piece.split_in_popped_row(row)
                    piece.update_nodes()
                    if split_piece is not None:
                        split_pieces.append(split_piece)
                for column in range(self.columns):
                    self.grid[row][column] = None
            for split_piece in split_pieces:
                self.grid_pieces.append(split_piece)
                for node in split_piece.nodes:
                    self.grid[round(node.y)][round(node.x)] = split_piece

            empty_pieces = []
            for piece in self.grid_pieces:
                if len(piece.nodes) == 0:
                    empty_pieces.append(piece)
            for piece in empty_pieces:
                self.grid_pieces.remove(piece)

            for piece in self.grid_pieces:
                if piece.min_y > min(rows_to_pop):
                    piece.above_ground = False

            if len(rows_to_pop) == 1:
                self.score += 40
            elif len(rows_to_pop) == 2:
                self.score += 100
            elif len(rows_to_pop) == 3:
                self.score += 300
            else:
                self.score += 1200
            return True
        return False

    def add_piece(self, piece=None):
        while len(self.next_pieces) <= self.next_pieces_reveals:
            self.next_pieces.append(TetrisGame.generate_piece(self))

        next_piece = self.next_pieces.pop(0) if piece is None else TetrisGame.generate_piece(self, piece)
        self.grid_pieces.append(next_piece)
        self.user_piece = next_piece

    @staticmethod
    def generate_piece(game, piece=None):
        angle = 0  # random.randint(0, 3) * 90

        if piece is None:
            tetris_pieces_types = [LinePiece, LBlock, ReverseLBlock, Square, Squiggly, ReverseSquiggly, TBlock]
            index = random.randint(0, len(tetris_pieces_types) - 1)
            piece = tetris_pieces_types[index](Point(game.columns // 2, game.rows), angle)
            if piece.is_center_half_shifted:
                piece.center.x += 0.5
                piece.center.y += 0.5
        else:
            piece.angle = angle
        piece.update_nodes()

        piece.center.y += game.rows - piece.min_y
        width = piece.max_x - piece.min_x + 1
        shift = (game.columns - width) // 2  # random.randint(0, TetrisGame.columns - 1 - width)
        piece.center.x += shift - piece.min_x
        piece.update_nodes()

        return piece

    def switch_hold(self):
        for node in self.user_piece.nodes:
            if round(node.y) < self.rows:
                self.grid[round(node.y)][round(node.x)] = None

        piece_to_hold = self.user_piece
        self.grid_pieces.remove(piece_to_hold)
        self.add_piece(self.hold_piece)
        self.hold_piece = None
        self.hold_piece = piece_to_hold

    def render(self):
        start_time = time.time()
        if self.has_game_ended:
            return False
        self.pop_full_rows()
        self.move_all_down()

        if self.user_piece is None:
            game_ended = False
            for piece in self.grid_pieces:
                if game_ended:
                    continue
                for node in piece.nodes:
                    if round(node.y) >= self.rows - 1:
                        game_ended = True
            if not game_ended:
                self.add_piece()
            else:
                self.has_game_ended = True

        end_time = time.time()
        total_time = end_time - start_time
        if total_time > 1 / 200.0:
            print(f"Render Over-run: {total_time}")

        return False

    def get_drop_mark(self):
        if self.user_piece is None:
            return None
        return Piece(
            self.user_piece.color,
            Point(self.user_piece.center.x, self.user_piece.center.y - self.user_piece.count_moves_down(self)),
            self.user_piece.relative_nodes,
            self.user_piece.angle
        )


class Piece:
    nodes_num = 4

    def __init__(self, color, center, relative_nodes, angle, is_center_half_shifted=False):
        self.color = color
        self.center = center
        self.relative_nodes = relative_nodes
        self.angle = angle
        self.is_center_half_shifted = is_center_half_shifted

        self.above_ground = False

        self.nodes = []
        self.min_y = None
        self.max_y = None
        self.min_x = None
        self.max_x = None
        self.update_nodes()

        self.called_move_down = False

    def update_nodes(self):
        self.min_y = None
        self.max_y = None
        self.min_x = None
        self.max_x = None
        while len(self.nodes) > 0:
            self.nodes.pop(0)
        if not len(self.relative_nodes) > 0:
            pass
        for relative_node in self.relative_nodes:
            radius = math.sqrt(relative_node.x ** 2 + relative_node.y ** 2)
            theta = math.atan2(relative_node.y, relative_node.x)

            node_relative_to_grid = Point(
                x=self.center.x + radius * math.cos(math.radians(self.angle) + theta),
                y=self.center.y + radius * math.sin(math.radians(self.angle) + theta)
            )
            self.nodes.append(node_relative_to_grid)

        for node in self.nodes:
            self.min_y = round(node.y) if self.min_y is None else min(round(node.y), self.min_y)
            self.max_y = round(node.y) if self.max_y is None else max(round(node.y), self.max_y)
            self.min_x = round(node.x) if self.min_x is None else min(round(node.x), self.min_x)
            self.max_x = round(node.x) if self.max_x is None else max(round(node.x), self.max_x)

    def move_down(self, game, call=True):
        self.called_move_down = call if call else self.called_move_down
        if self.above_ground:
            return False

        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            if round(node.y) <= 0:
                self.above_ground = True
                return False  # unable to move down

            piece_down = game.grid[round(node.y - 1)][round(node.x)]
            if piece_down is not None and piece_down != self:
                if not piece_down.move_down(game):
                    self.above_ground = True
                    return False  # unable to move down

        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            game.grid[round(node.y)][round(node.x)] = None

        self.center.y -= 1
        self.update_nodes()

        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            game.grid[round(node.y)][round(node.x)] = self
        return True

    def check_move_down(self, game):
        if self.above_ground:
            return False

        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            if round(node.y) <= 0:
                return False  # unable to move down

            piece_down = game.grid[round(node.y - 1)][round(node.x)]
            if piece_down is not None and piece_down != self:
                if not piece_down.check_move_down(game):
                    return False  # unable to move down
        return True

    def count_moves_down(self, game):
        moves_to_block = game.rows
        for node in self.nodes:
            steps = 1
            while round(node.y) - steps >= 0:
                piece_down = game.grid[min(round(node.y) - steps, game.rows-1)][round(node.x)]
                if piece_down is not None and piece_down != self:
                    break
                steps += 1
            moves_to_block = min(moves_to_block, steps - 1)
        return moves_to_block

    def move_on_x_axis(self, game, step):
        for node in self.nodes:
            if round(node.x) + step < 0 or round(node.x) + step >= game.columns:
                return False  # illegal move

            if round(node.y) < game.rows:
                other_piece = game.grid[round(node.y)][round(node.x + step)]
                if other_piece is not None and other_piece != self:
                    return False  # illegal move

        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            game.grid[round(node.y)][round(node.x)] = None

        self.center.x += step
        self.update_nodes()
        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            game.grid[round(node.y)][round(node.x)] = self

    def rotate_90_degrees(self, game, clockwise):
        previous_angle = self.angle
        if clockwise:
            self.angle += 90
        else:
            self.angle -= 90
        self.update_nodes()

        if self.min_y < 0:
            self.angle = previous_angle
            self.update_nodes()
            return False  # illegal move

        x_offset = 0
        if self.max_x > game.columns - 1:
            x_offset = game.columns - 1 - self.max_x
        if self.min_x < 0:
            x_offset = 0 - self.min_x

        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            if not 0 <= round(node.x + x_offset) < game.columns:
                self.angle = previous_angle
                self.update_nodes()
                return False  # illegal move
            other_piece = game.grid[round(node.y)][round(node.x + x_offset)]
            if other_piece is not None and other_piece != self:
                self.angle = previous_angle
                self.update_nodes()
                return False  # illegal move

        self.angle, previous_angle = previous_angle, self.angle
        self.update_nodes()
        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            game.grid[round(node.y)][round(node.x)] = None
        self.angle, previous_angle = previous_angle, self.angle
        self.center.x += x_offset
        self.update_nodes()
        for node in self.nodes:
            if round(node.y) >= game.rows:
                continue
            game.grid[round(node.y)][round(node.x)] = self

    def split_in_popped_row(self, row):
        if not len(self.relative_nodes) > 0:
            return None
        if self.min_y > row or row > self.max_y:
            return None     # row is not related to piece
        split_nodes = []
        for i in range(len(self.nodes))[::-1]:
            if round(self.nodes[i].y) <= row:
                if round(self.nodes[i].y) < row:
                    split_nodes.append(self.relative_nodes[i])
                self.relative_nodes.pop(i)
        if len(split_nodes) > 0:
            split_piece = Piece(self.color, Point(self.center.x, self.center.y), split_nodes, self.angle)
            return split_piece
        return None


class LinePiece(Piece):
    def __init__(self, center, angle):
        color = (51, 153, 255)
        nodes = [Point(1.5, 0.5), Point(0.5, 0.5), Point(-0.5, 0.5), Point(-1.5, 0.5)]
        super().__init__(color, center, nodes, angle, is_center_half_shifted=True)


class LBlock(Piece):
    def __init__(self, center, angle):
        color = (255, 128, 0)
        nodes = [Point(-1, 0), Point(0, 0), Point(1, 0), Point(1, 1)]
        super().__init__(color, center, nodes, angle)


class ReverseLBlock(Piece):
    def __init__(self, center, angle):
        color = (0, 0, 204)
        nodes = [Point(-1, 1), Point(-1, 0), Point(0, 0), Point(1, 0)]
        super().__init__(color, center, nodes, angle)


class Square(Piece):
    def __init__(self, center, angle):
        color = (238, 238, 7)
        nodes = [Point(0.5, 0.5), Point(0.5, -0.5), Point(-0.5, 0.5), Point(-0.5, -0.5)]
        super().__init__(color, center, nodes, angle, is_center_half_shifted=True)


class Squiggly(Piece):
    def __init__(self, center, angle):
        color = (255, 0, 0)
        nodes = [Point(-1, 1), Point(0, 1), Point(0, 0), Point(1, 0)]
        super().__init__(color, center, nodes, angle)


class ReverseSquiggly(Piece):
    def __init__(self, center, angle):
        color = (0, 204, 0)
        nodes = [Point(-1, 0), Point(0, 0), Point(0, 1), Point(1, 1)]
        super().__init__(color, center, nodes, angle)


class TBlock(Piece):
    def __init__(self, center, angle):
        color = (102, 0, 204)
        nodes = [Point(-1, 0), Point(0, 0), Point(0, 1), Point(1, 0)]
        super().__init__(color, center, nodes, angle)
