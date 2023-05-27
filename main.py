import pyglet

from screen import MyWindow

# start the main window and start a timer to hit the update method
if __name__ == '__main__':
    frame_rate = 30
    window = MyWindow(700, 700, "Tetris", resizable=False)
    pyglet.clock.schedule_interval(window.update, 1 / frame_rate)
    pyglet.app.run()
