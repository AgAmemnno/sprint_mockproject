from OpenGL.GL import *
from OpenGL.GL.shaders import *
import numpy as np

class Vao(object):
    def __init__(self):
        pass
    def __del__(self):
        #self.delete()
        pass
    def bind(self):
        glBindVertexArray(self.vao);
    def pos2d(self):
        positions = np.array([
            [-1.0, -1.0],
            [-1.0, 1.0],
            [1.0, -1.0],
            [1.0, 1.0]], dtype="f4")

        position_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, position_vbo)
        glBufferData(GL_ARRAY_BUFFER, positions, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, position_vbo)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.vao  = vao
        self.vbo  = position_vbo
    def delete(self):
        glDeleteVertexArrays(1, [self.vao]);
        glDeleteBuffers(1, [self.vbo]);
