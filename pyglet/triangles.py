from common import get_triangles, run


def immediate_mode(window):
    from pyglet import gl
    triangles = get_triangles(window)

    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glBegin(triangles.vertex_mode)
        for i in xrange(4):
            gl.glColor3ub(*triangles.colors[3*i:3*i+3])
            gl.glVertex2i(*triangles.positions[2*i:2*i+2])
        gl.glEnd()

    window.event(on_draw)

def vertex_array(window):
    from pyglet import gl

    gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

    triangles = get_triangles(window)
    positions = triangles.positions
    positions_gl = (gl.GLint * len(positions))(*positions)

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glVertexPointer(2, gl.GL_INT, 0, positions_gl)
        gl.glLoadIdentity()
        gl.glDrawArrays(triangles.vertex_mode, 0, 4)

def graphics(window):
    raise TypeError('draw does not support TRIANGLE_FAN')

def graphics_indexed(window):
    from pyglet import gl
    from pyglet.graphics import draw_indexed

    triangles = get_triangles(window)
    positions = triangles.position_type, triangles.positions
    colors = triangles.color_type, triangles.colors

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        draw_indexed(4, triangles.vertex_mode, triangles.indexes,
                     positions, colors)

def graphics_vertex_list(window):
    from pyglet import gl
    from pyglet.graphics import vertex_list

    triangles = get_triangles(window)
    positions = triangles.position_type, triangles.positions
    colors = triangles.color_type, triangles.colors
    vl = vertex_list(4, positions, colors)

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        vl.draw(triangles.vertex_mode)

def graphics_vertex_list_indexed(window):
    from pyglet import gl
    from pyglet.graphics import vertex_list_indexed

    triangles = get_triangles(window)
    positions = triangles.position_type, triangles.positions
    colors = triangles.color_type, triangles.colors
    vl = vertex_list_indexed(4, triangles.indexes, positions, colors)

    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        vl.draw(triangles.vertex_mode)

if __name__ == '__main__':
    run(globals())
