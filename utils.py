import pyglet
from pyglet import shapes


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def play_audio(sound, volume=1.0, loop=False):
    # create a player and queue the song
    player = pyglet.media.Player()
    player.queue(sound)
    player.volume = volume
    player.loop = loop
    player.play()
    return player


def draw_rectangle(x, y, width, height, color, opacity=255, batch=None):
    rectangle = shapes.Rectangle(x, y, width, height, color=color, batch=batch)
    rectangle.opacity = opacity
    return rectangle


def draw_triangle(x1, y1, x2, y2, x3, y3, color, opacity=255, batch=None):
    triangle = shapes.Triangle(x1, y1, x2, y2, x3, y3, color=color, batch=batch)
    triangle.opacity = opacity
    return triangle


def draw_line(x1, y1, x2, y2, color, width, opacity=255, batch=None):
    line = shapes.Line(x1, y1, x2, y2, color=color, batch=batch, width=width)
    line.opacity = opacity
    return line


class AnimatedButton:
    states = ['hovered', 'pressed']

    def __init__(self, batch, x, y, width, height, elevation,
                 text,
                 text_color, background_color, background_color_pressed, elevation_color,
                 font_name='Arial', font_size=18, border_radius=4):
        self.batch = batch
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.elevation = elevation
        self.border_radius = border_radius
        self.text_label = pyglet.text.Label(text,
                                            font_name=font_name, font_size=font_size,
                                            x=x, y=y,
                                            anchor_x='center', anchor_y='center', color=text_color)
        self.background_color = background_color
        self.background_color_pressed = background_color_pressed
        self.elevation_color = elevation_color
        self.current_state = AnimatedButton.states[0]

    def update_mouse_movement(self, x, y, dx, dy):
        if not self.hover(x, y):
            self.current_state = AnimatedButton.states[0]
            return False
        return True

    def click(self, x, y):
        if self.hover(x, y):
            self.current_state = AnimatedButton.states[1]
            return True
        return False

    def release(self):
        if self.current_state == AnimatedButton.states[1]:
            self.current_state = AnimatedButton.states[0]
            return True
        self.current_state = AnimatedButton.states[0]
        return False

    def hover(self, x, y):
        height = self.height
        center_y = self.center_y
        if self.current_state == AnimatedButton.states[1]:
            center_y += self.elevation / 2
            height += self.elevation
        dis_from_center_x = abs(self.center_x - x)
        dis_from_center_y = abs(center_y - y)
        if dis_from_center_x <= self.width / 2 and dis_from_center_y <= height / 2:  # inside the rect
            if dis_from_center_x <= self.width / 2 - self.border_radius or \
                    dis_from_center_y <= height / 2 - self.border_radius or \
                    ((dis_from_center_x - self.width / 2 + self.border_radius) ** 2 +
                     (dis_from_center_y - height / 2 + self.border_radius) ** 2) <= self.border_radius:
                return True
        return False

    def draw(self):
        background_color = self.background_color
        if self.current_state == AnimatedButton.states[0]:
            elevation_rectangle = draw_rectangle(round(self.center_x - self.width / 2),
                                                 round(self.center_y - self.height / 2),
                                                 self.width, self.elevation + self.border_radius,
                                                 color=self.elevation_color,
                                                 opacity=255,
                                                 batch=self.batch)
            rectangle = draw_rectangle(round(self.center_x - self.width / 2),
                                       round(self.center_y - self.height / 2 + self.elevation),
                                       self.width, self.height,
                                       color=background_color,
                                       opacity=255,
                                       batch=self.batch)
            self.text_label.y = self.center_y + self.elevation
            return [elevation_rectangle, rectangle], self.text_label
        else:
            background_color = self.background_color_pressed
            rectangle = draw_rectangle(
                round(self.center_x - self.width / 2),
                round(self.center_y - self.height / 2),
                self.width, self.height, color=background_color, opacity=255, batch=self.batch)
            self.text_label.y = self.center_y
            return [rectangle], self.text_label
