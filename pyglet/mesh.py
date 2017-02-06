from collections import namedtuple

import numpy

from pyglet import gl, graphics



_TYPE_MAP = {
    'b': (numpy.int8,),
    'B': (numpy.uint8,),
    's': (numpy.int16,),
    'S': (numpy.uint16,),
    'i': (numpy.int32, numpy.int64),
    'I': (numpy.uint32, numpy.uint64),
    'f': (numpy.float32,),
    'd': (numpy.float64,),
}
_INV_TYPE_MAP = {}
for k, types in _TYPE_MAP.items():
    for t in types:
        _INV_TYPE_MAP[t] = k

def _get_gl_type(data):
    if type(data) == numpy.ndarray:
        return _INV_TYPE_MAP[data.dtype]
    else:
        while type(data) in (list, tuple):
            data = data[0]
        return 'i' if type(data) == int else 'f'


class RawMesh:
    def __init__(self, drawing_mode, ndim, positions, colors=None, textures=None,
                 normals=None, indexes=None, hint=''):

        if drawing_mode not in (gl.GL_TRIANGLES, gl.GL_TRIANGLE_STRIP):
            raise ValueError('Unsupported vertex mode')
        nb_numbers = len(positions)
        nb_vertices = nb_numbers / ndim
        batch_args = [nb_vertices, drawing_mode, None]
        batch_func = graphics.Batch.add
        if indexes is not None:
            indexes = numpy.array(indexes, dtype='int32', copy=False)
            batch_func = graphics.Batch.add_indexed
            batch_args.append(indexes)

        position_type = _get_gl_type(positions)
        positions = numpy.array(positions, copy=False)
        position_type = 'v{0}{1}'.format(ndim, position_type)
        if hint:
            position_type += '/' + hint

        batch_args.append((position_type, positions))

        color_type = ''
        if colors is not None:
            if len(colors) == nb_vertices * 3:
                color_ndim = 3
            elif len(colors) == nb_vertices * 4:
                color_ndim = 4
            color_type = _get_gl_type(colors)
            # assume it is a ub (0-255)
            if color_type in 'bBsSiI':
                color_type = 'B'
            colors = numpy.array(colors, copy=False)
            color_type = 'c{0}{1}'.format(color_ndim, color_type)
            if hint:
                color_type += '/' + hint
            batch_args.append((color_type, colors))

        # TODO: normals
        # TODO: textures

        self.nb_vertices = nb_vertices
        self.drawing_mode = drawing_mode
        self.ndim = ndim
        self.position_type = position_type
        self.positions = positions
        self.color_type = color_type
        self.colors = colors
        self.indexes = indexes
        self.name = None
        self.__batch = None
        self.__batch_data = batch_func, batch_args

    def add_to_batch(self, batch, group=None):
        f, args = self.__batch_data
        args[2] = group
        return f(batch, *args)

    @property
    def batch(self):
        batch = self.__batch
        if batch is None:
            self.__batch = batch = graphics.Batch()
            self.add_to_batch(batch)
        return batch

    def draw(self):
        self.batch.draw()

    _STR_TEMPLATE = 'RMesh({mode} {o.ndim}D, vnb={o.nb_vertices}, ' \
                    'pos={o.position_type}, color={o.color_type}, ' \
                    'I={indexes})'

    def __str__(self):
        mode = 'Triangles' if self.drawing_mode == gl.GL_TRIANGLES else 'Strip'
        indexes = self.indexes is not None
        return self._STR_TEMPLATE.format(mode=mode, indexes=indexes, o=self)


class Mesh:

    def __init__(self, name=None, batch=None):
        self.name = name
        self.batch = batch or graphics.Batch()
        self.__meshes = set()

    def add_mesh(self, raw_mesh, group=None):
        raw_mesh.add_to_batch(self.batch, group=group)
        self.__meshes.add(raw_mesh)

    def add(self, drawing_mode, ndim, positions, colors=None, textures=None,
            normals=None, indexes=None, hint='', group=None):
        mesh = RawMesh(drawing_mode, ndim, positions, colors=colors,
                       textures=textures, normals=normals, indexes=indexes,
                       hint=hint)
        self.add_mesh(mesh, group=group)

    def draw(self):
        self.batch.draw()

    def __str__(self):
        name = self.name or ''
        meshes = ", ".join([str(m) for m in self.__meshes])
        return 'Mesh(name={0!r} meshes={{{1}}})'.format(name, meshes)


def demo1(window):
    mesh = Mesh()
    w, h, m = window.width, window.height, 10
    #positions = w-m, m, m, m, w-m, h-m, m, h-m
    positions = m, h-m, m, m, w-m, h-m, w-m, m
    colors = 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255, 255
    indexes = 0, 1, 2, 3
    mesh.add(gl.GL_TRIANGLE_STRIP, 2, positions, colors=colors, indexes=indexes)
    return mesh

def demo2(window):
    # http://www.learnopengles.com/tag/degenerate-triangles/
    mesh = Mesh()
    w, h, m = 100, 100, 10
    positions = m, m+h, m, m, m+w, m+h, m+w, m
    colors = 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255, 255
    indexes = 0, 1, 2, 3, 3 # 1 degenerate here at the end
    #positions = m, m+h, m, m, m+w, m+h
    #colors = 0, 0, 255, 0, 255, 0, 255, 0, 0
    #indexes = 0, 1, 2, 2
    mesh.add(gl.GL_TRIANGLE_STRIP, 2, positions, colors=colors, indexes=indexes)

    m = 150
    positions = m, m+h, m, m, m+w, m+h
    colors = 0, 0, 255, 0, 255, 0, 255, 0, 0
    indexes = 0, 0, 1, 2 # 1 degenerate here at the beginning
    mesh.add(gl.GL_TRIANGLE_STRIP, 2, positions, colors=colors, indexes=indexes)

    return mesh

def main():
    from pyglet.app import run
    from pyglet.window import Window
    window = Window(caption='Mesh demo')
    mesh = demo2(window)
    print mesh
    @window.event
    def on_draw():
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glLoadIdentity()
        mesh.draw()
    run()

if __name__ == '__main__':
    main()
