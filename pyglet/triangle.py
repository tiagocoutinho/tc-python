from common import get_triangle, run


def immediate_mode(window):
    from pyglet import gl

    triangle = get_triangle(window)

    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glBegin(triangle.vertex_mode)
        for i in xrange(3):
            gl.glVertex2i(*triangle.positions[2*i:2*i+2])
        gl.glEnd()

    window.event(on_draw)

def vertex_array(window):
    from pyglet import gl

    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

    triangle = get_triangle(window)
    positions = triangle.positions
    positions_gl = (gl.GLint * len(positions))(*positions)

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glVertexPointer(2, gl.GL_INT, 0, positions_gl)
        gl.glDrawArrays(triangle.vertex_mode, 0, 3)

def vertex_array_numpy(window):
    import numpy
    from pyglet import gl

    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

    triangle = get_triangle(window)
    positions = numpy.array(triangle.positions, dtype=numpy.int32)
    positions_gl = numpy.ctypeslib.as_ctypes(positions)

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glVertexPointer(2, gl.GL_INT, 0, positions_gl)
        gl.glDrawArrays(triangle.vertex_mode, 0, 3)
    return triangle

def graphics(window):
    from pyglet import gl
    from pyglet.graphics import draw

    triangle = get_triangle(window)
    positions = triangle.position_type, triangle.positions

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        draw(3, triangle.vertex_mode, positions)

def graphics_indexed(window):
    from pyglet import gl
    from pyglet.graphics import draw_indexed

    triangle = get_triangle(window)
    vertices = triangle.position_type, triangle.positions

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        draw_indexed(3, triangle.vertex_mode, triangle.indexes, vertices)

def graphics_vertex_list(window):
    from pyglet import gl
    from pyglet.graphics import vertex_list

    triangle = get_triangle(window)
    vertices = triangle.position_type, triangle.positions
    vl = vertex_list(3, vertices)

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        vl.draw(triangle.vertex_mode)

def graphics_vertex_list_indexed(window):
    from pyglet import gl
    from pyglet.graphics import vertex_list_indexed

    triangle = get_triangle(window)
    vertices = triangle.position_type, triangle.positions
    vl = vertex_list_indexed(3, triangle.indexes, vertices)

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        vl.draw(triangle.vertex_mode)


if __name__ == '__main__':
    run(globals())
