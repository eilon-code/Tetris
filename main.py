import pyglet

from screen import MyWindow
from tetris import TetrisGame

# start the main window and start a timer to hit the update method
if __name__ == '__main__':
    frame_rate = 4.0
    window = MyWindow(700, 700, "Tetris", resizable=False)
    pyglet.clock.schedule_interval(TetrisGame.render, 1 / frame_rate)
    pyglet.app.run()
