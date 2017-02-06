from pyglet.app import run
from pyglet.text import Label
from pyglet.window import Window

def hello_world():

    window = Window()

    label = Label('Hello, world',
                  font_name='Times New Roman',
                  font_size=36,
                  x=window.width//2, y=window.height//2,
                  anchor_x='center', anchor_y='center')

    @window.event
    def on_draw():
        window.clear()
        label.draw()

    run()

if __name__ == '__main__':
    hello_world()
