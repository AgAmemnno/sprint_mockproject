from p2popt.GLAux.log import *
from p2popt.GLAux.parser import *

from OpenGL.GL import *
from OpenGL.GL.shaders import *

import ctypes
#logging = logging.getLogger(__name__)
__all__ = (['Pipe','Compute','read_file'])

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


def read_file(filename):
    with open(filename) as fp:
        return fp.readlines()

BIT    = {
    GL_VERTEX_SHADER : GL_VERTEX_SHADER_BIT,
    GL_FRAGMENT_SHADER : GL_FRAGMENT_SHADER_BIT
}

PGNAME = {
    GL_VERTEX_SHADER :  "vp",
    GL_FRAGMENT_SHADER : "fp"
}

class ShaderProgram(int):
    """Integer sub-class with context-manager operation"""
    validated = False
    def __enter__(self):
        """Start use of the program"""
        glUseProgram(self)
    def __exit__(self, typ, val, tb):
        """Stop use of the program"""
        glUseProgram(0)
    def check_validate(self):
        """Check that the program validates

        Validation has to occur *after* linking/loading

        raises RuntimeError on failures
        """
        glValidateProgram(self)
        validation = glGetProgramiv(self, GL_VALIDATE_STATUS)
        if validation == GL_FALSE:
            raise RuntimeError(
                """Validation failure (%r): %s""" % (
                    validation,
                    glGetProgramInfoLog(self).decode(),
                ))
        self.validated = True
        return self
    def check_linked(self):
        """Check link status for this program

        raises RuntimeError on failures
        """
        link_status = glGetProgramiv(self, GL_LINK_STATUS)
        if link_status == GL_FALSE:
            raise RuntimeError(
                """%s""" % (
                    glGetProgramInfoLog(self).decode(),
                ))
        return self
    def retrieve(self):
        """Attempt to retrieve binary for this compiled shader

        Note that binaries for a program are *not* generally portable,
        they should be used solely for caching compiled programs for
        local use; i.e. to reduce compilation overhead.

        returns (format,binaryData) for the shader program
        """
        from OpenGL.raw.GL._types import GLint, GLenum
        from OpenGL.arrays import GLbyteArray
        size = GLint()
        glGetProgramiv(self, get_program_binary.GL_PROGRAM_BINARY_LENGTH, size)
        result = GLbyteArray.zeros((size.value,))
        size2 = GLint()
        format = GLenum()
        get_program_binary.glGetProgramBinary(self, size.value, size2, format, result)
        return format.value, result
    def load(self, format, binary, validate=True):
        """Attempt to load binary-format for a pre-compiled shader

        See notes in retrieve
        """
        get_program_binary.glProgramBinary(self, format, binary, len(binary))
        if validate:
            self.check_validate()
        self.check_linked()
        return self

def _compileShader( source, shaderType ):
    """Compile shader source of given type

    source -- GLSL source-code for the shader
    shaderType -- GLenum GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, etc,

    returns GLuint compiled shader reference
    raises RuntimeError when a compilation failure occurs
    """
    if isinstance( source, (bytes,unicode)):
        source = [ source ]
    source = [ as_8_bit(s) for s in source ]
    shader = glCreateShader(shaderType)
    glShaderSource( shader, source )
    glCompileShader( shader )
    result = glGetShaderiv( shader, GL_COMPILE_STATUS )
    if not(result):
        # TODO: this will be wrong if the user has
        # disabled traditional unpacking array support.
        #print(ParseProgram.ofs)
        msg = "Shader Program Traceback\n"
        for l in glGetShaderInfoLog(shader).decode().split('\n'):
            e =  l.find(')')
            if e != -1:
                print(l)
                No = int(l[2:e])
                for i,ofs in enumerate(ParseProgram.ofs):
                    if ofs[1] > No:
                        msg += "%s(%d) %s  \n"%(ofs[0],No-ParseProgram.ofs[i-1][1],l[e+1:])
                        break
        log.Error(msg)
        raise RuntimeError(
            """Shader compile failure (%s)"""%(
                result
            )
        )
    return shader


class Compute(object):
    def __init__(self,*shaders):
        self.PG = []
        self.compile(*shaders)
        self.curr = -1000
    def bind(self,n):
        if n < len(self.PG):
            glUseProgram(self.PG[n])
            self.curr = n
    def compile(self,*shaders, **named):
        sha  = shaders[0]
        for i,fn in enumerate(sha):
            Name = fn.split('/')[-1].split('.')[0]
            sh = parse(fn,0)
            incth = len(ParseProgram.ofs) - 1
            ParseProgram.ofs[incth][1] -= incth
            ParseProgram.ofs.append([fn, len(sh.split("\n"))])
            #print(ParseProgram.ofs)
            pg   = compileProgram(_compileShader(sh, GL_COMPUTE_SHADER))
            self.PG.append(pg)
        log.Info("ComputeShader Generate %s"%self.PG)
    def delete(self):
        for i in self.PG:
            #print(glIsProgram(i))
            glDeleteProgram(i)
        log.Info("ComputeShader Destroy %s"%self.PG)
class Pipe(object):
    def __init__(self,*shaders):
        self.compilePipeline(*shaders)
    def __del__(self):
        #self.delete()
        pass
    def bind(self):
        glUseProgram(0)
        glBindProgramPipeline(self.pipe)
    def vloc(self,name):
        #glProgramUniform3f(pipe.Pg[DIFF::vp][0], glGetUniformLocation(pipe.Pg[DIFF::vp][0], "iGen"), gen.x, gen.y,gen.z);
        return (self.PG[GL_VERTEX_SHADER],glGetUniformLocation(self.PG[GL_VERTEX_SHADER], name))
    def floc(self,name):
        return (self.PG[GL_FRAGMENT_SHADER],glGetUniformLocation(self.PG[GL_FRAGMENT_SHADER], name))
    def compilePipeline(self,*shaders, **named):
        #pipe = 0
        self.pipe = glGenProgramPipelines(1)
        self.PG = {}
        sha  = shaders[0]
        type = shaders[1]
        for i,fn in enumerate(sha):
            str_ = (ctypes.POINTER(ctypes.c_char) * 1)()
            sh = parse(fn)
            enc = sh.encode('utf-8')
            str_[0] =  ctypes.create_string_buffer(enc)
            Sh      =  glCreateShaderProgramv(type[i], 1, str_)
            #logging.Debug(fn)
            sh = ShaderProgram(Sh)
            sh.check_linked()
            sh.check_validate()
            glUseProgramStages(self.pipe,BIT[type[i]], Sh)
            self.PG[type[i]]  = Sh
    def delete(self):
        for i in self.PG:
            #print(glIsProgram(i))
            glDeleteProgram(self.PG[i])
        glDeleteBuffers(1, [self.pipe])
        log.Info("PipeLine Destroy %s" % self.PG)



if __name__ == "__main__":
    log.Log("compile shaders")
