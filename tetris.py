import math
import random

from utils import Point


class TetrisGame:
    columns = 10
    rows = 20
    score = 0
    pieces = []
    next_pieces = []

    @staticmethod
    def render(dt):
        TetrisGame.pop_full_rows()
        TetrisGame.move_all_down()
        some_piece_of_user = False
        for piece in TetrisGame.pieces:
            if piece.is_piece_of_user and len(piece.nodes) > 0:
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

    @staticmethod
    def rotate_piece_90(clockwise):
        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].rotate_90_degrees(clockwise)

    @staticmethod
    def move_right():
        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].move_right()

    @staticmethod
    def move_left():
        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].move_left()

    @staticmethod
    def move_all_down():
        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].moved_down = False

        for i in range(len(TetrisGame.pieces)):
            TetrisGame.pieces[i].move_down()

    @staticmethod
    def pop_full_rows():
        grid = [[False for _ in range(TetrisGame.columns)] for _ in range(TetrisGame.rows)]
        for piece in TetrisGame.pieces:
            if piece.is_piece_of_user or not piece.above_ground:
                continue
            for node in piece.nodes_centers:
                if round(node.y) < TetrisGame.rows:
                    grid[round(node.y)][round(node.x)] = True

        full_rows = []
        for i in range(len(grid)):
            if False not in grid[i]:
                full_rows.append(i)

        if len(full_rows) > 0:
            for i in range(len(TetrisGame.pieces)):
                for row in full_rows:
                    TetrisGame.pieces[i].split_in_popped_row(row)

            for i in range(len(TetrisGame.pieces))[::-1]:
                if len(TetrisGame.pieces[i].nodes) == 0:
                    TetrisGame.pieces.pop(i)

            for i in range(len(TetrisGame.pieces)):
                if TetrisGame.pieces[i].min_y > min(full_rows):
                    TetrisGame.pieces[i].above_ground = False

            if len(full_rows) == 1:
                TetrisGame.score += 40
            elif len(full_rows) == 2:
                TetrisGame.score += 100
            elif len(full_rows) == 3:
                TetrisGame.score += 300
            else:
                TetrisGame.score += 1200

    @staticmethod
    def add_piece():
        if len(TetrisGame.next_pieces) == 0:
            TetrisGame.generate_next_piece()
        next_piece = TetrisGame.next_pieces.pop(0)
        next_piece.is_active = True
        TetrisGame.pieces.append(next_piece)
        TetrisGame.generate_next_piece()

    @staticmethod
    def generate_next_piece():
        tetris_pieces_types = [LinePiece, LBlock, ReverseLBlock, Square, Squiggly, ReverseSquiggly, TBlock]

        index = random.randint(0, len(tetris_pieces_types) - 1)
        angle = random.randint(0, 3) * 90
        piece = tetris_pieces_types[index](TetrisGame.columns // 2, TetrisGame.rows, angle, False)
        if index == 0 or index == 3:
            piece.center_x += 0.5
            piece.center_y += 0.5

        nodes_centers = piece.get_nodes_centers()
        min_x = TetrisGame.columns - 1
        max_x = 0
        min_y = TetrisGame.rows

        for node in nodes_centers:
            if round(node.x) > max_x:
                max_x = round(node.x)
            if round(node.x) < min_x:
                min_x = round(node.x)
            if round(node.y) < min_y:
                min_y = round(node.y)

        piece.center_y += TetrisGame.rows - min_y
        width = max_x - min_x + 1
        piece.center_x += random.randint(0, TetrisGame.columns - 1 - width) - min_x
        piece.update()

        TetrisGame.next_pieces.append(piece)


class Piece:
    def __init__(self, center_x, center_y, color, nodes, angle, is_active):
        self.color = color
        self.is_piece_of_user = True
        self.above_ground = False
        self.moved_down = False
        self.center_x = center_x
        self.center_y = center_y
        self.min_y = 0

        self.nodes = nodes
        self.angle = angle
        self.nodes_centers = []
        self.is_active = is_active

        self.update()
        if self.is_active:
            TetrisGame.pieces.append(self)

    def update(self):
        self.min_y = TetrisGame.rows
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

    def move_down(self):
        if self.moved_down or (not self.is_active) or self.above_ground:
            return False
        self.moved_down = True

        for node in self.nodes_centers:
            if round(node.y) < 1:
                self.above_ground = True
                if self.is_piece_of_user:
                    self.is_piece_of_user = False
                return False  # unable to move down
            for piece in TetrisGame.pieces:
                if piece == self:
                    continue
                for other_node in piece.nodes_centers:
                    if round(other_node.x) == round(node.x) and round(other_node.y) == round(node.y - 1):
                        if not piece.move_down():
                            self.above_ground = True
                            if self.is_piece_of_user:
                                self.is_piece_of_user = False
                            return False    # unable to move down
        self.center_y -= 1
        self.update()
        return True

    def move_right(self):
        if self.is_active and self.is_piece_of_user:
            for node in self.nodes_centers:
                if round(node.x) >= TetrisGame.columns - 1:
                    return False  # illegal move
                for piece in TetrisGame.pieces:
                    if piece == self:
                        continue
                    for other_node in piece.nodes_centers:
                        if round(other_node.x) == round(node.x + 1) and round(other_node.y) == round(node.y):
                            return False  # illegal move

            self.center_x += 1
            self.update()

            return True
        return False

    def move_left(self):
        if self.is_active and self.is_piece_of_user:
            for node in self.nodes_centers:
                if round(node.x) < 1:
                    return False    # illegal move
                for piece in TetrisGame.pieces:
                    if piece == self:
                        continue
                    for other_node in piece.nodes_centers:
                        if round(other_node.x) == round(node.x - 1) and round(other_node.y) == round(node.y):
                            return False    # illegal move

            self.center_x -= 1
            self.update()

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

            for node in self.nodes_centers:
                if round(node.y) < 0 or round(node.x) < 0 or round(node.x) >= TetrisGame.columns:
                    self.angle = previous_angle
                    self.update()
                    return False    # illegal move
                for piece in TetrisGame.pieces:
                    if piece == self:
                        continue
                    for other_node in piece.nodes_centers:
                        if round(other_node.x) == round(node.x) and round(other_node.y) == round(node.y):
                            self.angle = previous_angle
                            self.update()
                            return False  # illegal move
            return True
        return False

    def get_nodes_centers(self):
        nodes_centers = []
        for node in self.nodes:
            radius = math.sqrt(node.x ** 2 + node.y ** 2)
            theta = math.atan2(node.y, node.x)

            node_center_x = radius * math.cos(math.radians(self.angle) + theta)
            node_center_y = radius * math.sin(math.radians(self.angle) + theta)
            nodes_centers.append(Point(self.center_x + node_center_x, self.center_y + node_center_y))
        return nodes_centers

    def split_in_popped_row(self, row):
        split_nodes = []
        removed_nodes = []
        for i in range(len(self.nodes_centers)):
            if round(self.nodes_centers[i].y) < row:
                split_nodes.append(i)
            elif round(self.nodes_centers[i].y) == row:
                removed_nodes.append(i)

        if len(split_nodes) == len(self.nodes) or len(split_nodes) + len(removed_nodes) == 0:
            pass

        split_piece = Piece(self.center_x, self.center_y, self.color,
                            [self.nodes[i] for i in split_nodes], self.angle, self.is_active)
        split_piece.is_piece_of_user = False
        for i in sorted(removed_nodes + split_nodes)[::-1]:
            self.nodes.pop(i)
        self.update()
        self.above_ground = False


class LinePiece(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (51, 153, 255)
        nodes = [Point(0.5, 1.5), Point(0.5, 0.5), Point(0.5, -0.5), Point(0.5, -1.5)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class LBlock(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (255, 128, 0)
        nodes = [Point(-1, 1), Point(0, 1), Point(0, 0), Point(0, -1)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class ReverseLBlock(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (0, 0, 204)
        nodes = [Point(1, 1), Point(0, 1), Point(0, 0), Point(0, -1)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class Square(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (238, 238, 7)
        nodes = [Point(0.5, 0.5), Point(0.5, -0.5), Point(-0.5, 0.5), Point(-0.5, -0.5)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class Squiggly(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (255, 0, 0)
        nodes = [Point(-1, 0), Point(0, -1), Point(0, 0), Point(1, -1)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class ReverseSquiggly(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (0, 204, 0)
        nodes = [Point(-1, 0), Point(0, 0), Point(0, 1), Point(1, 1)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)


class TBlock(Piece):
    def __init__(self, center_x, center_y, angle, is_active):
        color = (102, 0, 204)
        nodes = [Point(0, 1), Point(0, 0), Point(1, 0), Point(0, -1)]
        super().__init__(center_x, center_y, color, nodes, angle, is_active)
