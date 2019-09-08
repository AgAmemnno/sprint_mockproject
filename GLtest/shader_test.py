import sys

import wx
import wx.glcanvas as glcanvas



from OpenGL.GL import *
from OpenGL.GL.shaders import *
#from OpenGL.GLUT import *
haveOpenGL = True
import numpy
import math
import ctypes


#----------------------------------------------------------------------

cs = """
#version 430

struct Particle{
    vec4 pos;
};

layout(std430, binding=7) buffer particles{
    Particle p[];
};

uniform float time;
uniform uint max_num;

layout(local_size_x = 128, local_size_y = 1, local_size_z = 1) in;

#define PI 3.14159265359
#define PI2 ( PI * 2.0 )

vec2 rotate( in vec2 p, in float t )
{
  return p * cos( -t ) + vec2( p.y, -p.x ) * sin( -t );
}   


float hash(float n)
{
  return fract(sin(n)*753.5453123);
}

void main(){
  uint id = gl_GlobalInvocationID.x;
  float theta = hash(float(id)*0.3123887) * PI2 + time;
  p[id].pos.x = cos(theta)+1.5;
  p[id].pos.y = sin(theta)*1.8;
  p[id].pos.z = 0.0;
  p[id].pos.w = 1.0;
  p[id].pos.xz = rotate(p[id].pos.xz, hash(float(id)*0.5123)*PI2);
}
"""

vs = """
#version 430

layout( location = 0 ) in vec4 pos;

layout(std140) uniform pvMatrix
{
  mat4 pMatrix;
  mat4 vMatrix;
};

void main(void){    
    //gl_Position = pMatrix*vMatrix*pos;
    gl_Position = pos;
}
"""

fs = """
#version 430

out vec4 fragColor;

vec3 hsv(float h, float s, float v)
{
  return mix( vec3( 1.0 ), clamp( ( abs( fract(
    h + vec3( 3.0, 2.0, 1.0 ) / 3.0 ) * 6.0 - 3.0 ) - 1.0 ), 0.0, 1.0 ), s ) * v;
}

void main(){
    fragColor = vec4(hsv(0.6, 1.0, 1.0), 1.0);
}
"""

class MyCanvasBase(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False
        self.context = glcanvas.GLContext(self)
        self.lastx = self.x = 30
        self.lasty = self.y = 30
        self.size = None
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)



    def OnSize(self, event):
        wx.CallAfter(self.DoSetViewport)
        event.Skip()


    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)


    def OnPaint(self, event):
        #dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()


    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()


    def OnMouseUp(self, evt):
        self.ReleaseMouse()


    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            self.Refresh(False)



def perspective(fovy, aspect, near, far):
    top = near * math.tan(math.radians(fovy) / 2)
    right = top * aspect
    u = right * 2
    v = top * 2
    w = far - near
    return numpy.array((
        near * 2 / u, 0, 0, 0, 0,
        near * 2 / v, 0, 0, 0, 0,
        -(far + near) / w, -1, 0, 0,
        -(far * near * 2) / w, 0)
    ).astype(numpy.float32)


def lookAt(eye, center, up):
    eye = numpy.array(eye)
    center = numpy.array(center)
    up = numpy.array(up)
    z = (eye - center)/numpy.linalg.norm(eye - center)
    x = numpy.cross(up,z)
    x = x / numpy.linalg.norm(x)
    y = numpy.cross(z,x)
    x = y / numpy.linalg.norm(y)
    return numpy.array((
        x[0], y[0], z[0], 0,
        x[1], y[1], z[1], 0,
        x[2], y[2], z[2], 0,
        -x.dot(eye), -y.dot(eye), -z.dot(eye), 1)
    ).astype(numpy.float32)


class ShaderTest2(MyCanvasBase):
    def InitGL2(self):
        global computeProg
        computeProg = compileProgram(compileShader(cs, GL_COMPUTE_SHADER))

    def InitGL(self):
        glClearDepth(1)
        glClearColor(0, 0, 0, 0)

        global max_num
        max_num = 50000

        #global renderProg
        #renderProg = compileProgram(
        #    compileShader(vs, GL_VERTEX_SHADER),
        #    compileShader(fs, GL_FRAGMENT_SHADER))

        global pipe, Vs, Fs
        str_vs = (ctypes.POINTER(ctypes.c_char) * 1)()
        enc =  vs.encode('utf-8')
        str_vs[0] = ctypes.create_string_buffer(enc)

        str_fs    = (ctypes.POINTER(ctypes.c_char) * 1)()
        enc2      = fs.encode('utf-8')
        str_fs[0] = ctypes.create_string_buffer(enc2)

        Vs = glCreateShaderProgramv(GL_VERTEX_SHADER, 1,str_vs);
        Fs = glCreateShaderProgramv(GL_FRAGMENT_SHADER, 1,str_fs);
        pipe = 0
        glGenProgramPipelines(1,pipe);
        glUseProgramStages(pipe,GL_VERTEX_SHADER_BIT, Vs);
        glUseProgramStages(pipe,GL_FRAGMENT_SHADER_BIT, Fs);


        global computeProg
        computeProg = compileProgram(compileShader(cs, GL_COMPUTE_SHADER))

        ssbo = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, 4 * 4 * max_num, None, GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 7, ssbo)

        #glUseProgram(renderProg)
        glBindProgramPipeline(pipe);
        global vao
        vao = glGenVertexArrays(1);
        glBindVertexArray(vao);
        glBindBuffer(GL_ARRAY_BUFFER, ssbo)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)


        #glUniformBlockBinding(Vs, glGetUniformBlockIndex(Vs, 'pvMatrix'), 5)
        #buffer = glGenBuffers(1)
        #glBindBuffer(GL_UNIFORM_BUFFER, buffer)
        #data = numpy.hstack((
        #    perspective(45, w / h, 0.1, 100),
        #    lookAt((0, 3, 6), (0, 0, 0), (0, 1, 0))
        #))
        #glBufferData(GL_UNIFORM_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        #glBindBufferBase(GL_UNIFORM_BUFFER, 5, buffer)

        glUseProgram(computeProg)
        glUniform1ui(glGetUniformLocation(computeProg, 'max_num'), max_num)


    def OnDraw2(self):
        pass

    def OnDraw(self):

        glUseProgram(computeProg)
        glUniform1f(glGetUniformLocation(computeProg, 'time'), 1.)
        glDispatchCompute(max_num // 128, 1, 1)
        #glUseProgram(renderProg)
        glUseProgram(0)
        glBindProgramPipeline(pipe);
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_POINTS, 0, max_num)
        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size

        self.SwapBuffers()

class ShaderTest(MyCanvasBase):
    def InitGL(self):
        glClearDepth(1)
        glClearColor(0, 0, 0, 0)

        global max_num
        max_num = 50000

        global renderProg
        renderProg = compileProgram(
            compileShader(vs, GL_VERTEX_SHADER),
            compileShader(fs, GL_FRAGMENT_SHADER))

        global computeProg
        computeProg = compileProgram(compileShader(cs, GL_COMPUTE_SHADER))

        ssbo = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, 4 * 4 * max_num, None, GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 7, ssbo)

        glUseProgram(renderProg)
        glBindBuffer(GL_ARRAY_BUFFER, ssbo)
        pos = glGetAttribLocation(renderProg, "pos")
        glVertexAttribPointer(pos, 4, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(pos)

        glUniformBlockBinding(renderProg, glGetUniformBlockIndex(renderProg, 'pvMatrix'), 5)
        buffer = glGenBuffers(1)
        glBindBuffer(GL_UNIFORM_BUFFER, buffer)
        data = numpy.hstack((
            perspective(45, w / h, 0.1, 100),
            lookAt((0, 3, 6), (0, 0, 0), (0, 1, 0))
        ))
        glBufferData(GL_UNIFORM_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glBindBufferBase(GL_UNIFORM_BUFFER, 5, buffer)

        glUseProgram(computeProg)
        glUniform1ui(glGetUniformLocation(computeProg, 'max_num'), max_num)
    def OnDraw(self):

        glUseProgram(computeProg)
        glUniform1f(glGetUniformLocation(computeProg, 'time'), 1.)
        glDispatchCompute(max_num // 128, 1, 1)
        glUseProgram(renderProg)
        glClear(GL_COLOR_BUFFER_BIT)
        glDrawArrays(GL_POINTS, 0, max_num)
        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size

        self.SwapBuffers()

class CubeCanvas(MyCanvasBase):
    def InitGL(self):
        # set viewing projection
        glMatrixMode(GL_PROJECTION)
        glFrustum(-0.5, 0.5, -0.5, 0.5, 1.0, 3.0)

        # position viewer
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -2.0)

        # position object
        glRotatef(self.y, 1.0, 0.0, 0.0)
        glRotatef(self.x, 0.0, 1.0, 0.0)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)




    def OnDraw(self):
        # clear color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # draw six faces of a cube
        glBegin(GL_QUADS)
        glNormal3f( 0.0, 0.0, 1.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)

        glNormal3f( 0.0, 0.0,-1.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)

        glNormal3f( 0.0, 1.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glVertex3f(-0.5, 0.5, 0.5)

        glNormal3f( 0.0,-1.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f(-0.5,-0.5, 0.5)

        glNormal3f( 1.0, 0.0, 0.0)
        glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5)

        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5,-0.5)
        glEnd()

        if self.size is None:
            self.size = self.GetClientSize()
        w, h = self.size
        w = max(w, 1.0)
        h = max(h, 1.0)
        xScale = 180.0 / w
        yScale = 180.0 / h
        glRotatef((self.y - self.lasty) * yScale, 1.0, 0.0, 0.0);
        glRotatef((self.x - self.lastx) * xScale, 0.0, 1.0, 0.0);

        self.SwapBuffers()


if __name__ == '__main__':
    app = wx.App(False)
    global w, h
    w, h = 350, 250
    if not haveOpenGL:
        wx.MessageBox('This sample requires the PyOpenGL package.', 'Sorry')
    else:
        frm = wx.Frame(None, title='GLCanvas Sample')
        canvas = ShaderTest2(frm)
        frm.Show()
    app.MainLoop()
    glDeleteProgram(Vs)
    glDeleteProgram(Fs)
    glDeleteBuffers(1, [pipe])
    glDeleteVertexArrays(1,[vao])

