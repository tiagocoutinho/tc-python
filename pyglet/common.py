from collections import namedtuple

from pyglet import gl


Mesh = namedtuple('Mesh', ('vertex_mode',
                           'position_type', 'positions',
                           'color_type', 'colors',
                           'indexes'))

def get_triangle(window, margin=10):
    w, h, m = window.width, window.height, margin
    if w-m < 10 or h-m < 10:
        raise ValueError('margin too small for window')
    return Mesh(gl.GL_TRIANGLES,
                'v2i', (m, m, w-m, m, w-m, h-m),
                'c3B', (0, 0, 255, 0, 255, 0, 255, 0, 0),
                (0, 1, 2))

def get_triangles(window, margin=10):
    w, h, m = window.width, window.height, margin
    if w-m < 10 or h-m < 10:
        raise ValueError('margin too small for window')
    return Mesh(gl.GL_TRIANGLE_FAN,
                'v2i', (m, m, w-m, m, w-m, h-m, m, h-m),
                'c3B', (0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255, 255),
                (0, 1, 2, 0, 2, 3))

def run(demos):
    import sys
    from pyglet.app import run
    from pyglet.window import Window

    if len(sys.argv) > 1:
        name = sys.argv[1]
        if name not in demos:
            print "Unknown demo"
            sys.exit(1)
        prepare = demos[name]
    else:
        print "Need a demo name"
        sys.exit(2)
    w = Window()
    data = prepare(w)
    run()
