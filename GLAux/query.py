from GLAux.log import *
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import subprocess

class Smi:
    def __init__(self):
        pass
    def utilization(self):
        cmd = 'nvidia-smi --query-gpu=utilization.gpu --format=csv'
        output = subprocess.check_output(cmd, shell=True)
        return float(output.decode().split('\n')[1].strip()[:-1])


COMPUTE_SHADER_SPEC ={
"GL_MAX_COMPUTE_SHARED_MEMORY_SIZE":GL_MAX_COMPUTE_SHARED_MEMORY_SIZE,
"GL_MAX_COMPUTE_SHADER_STORAGE_BLOCKS":GL_MAX_COMPUTE_SHADER_STORAGE_BLOCKS,
#data returns one value, the maximum number of active shader storage blocks that may be accessed by a compute shader.
"GL_MAX_COMBINED_SHADER_STORAGE_BLOCKS":GL_MAX_COMBINED_SHADER_STORAGE_BLOCKS,
#data returns one value, the maximum total number of active shader storage blocks that may be accessed by all active shaders.
"GL_MAX_COMPUTE_UNIFORM_BLOCKS":GL_MAX_COMPUTE_UNIFORM_BLOCKS,
#data returns one value, the maximum number of uniform blocks per compute shader. The value must be at least 14. See glUniformBlockBinding.
"GL_MAX_COMPUTE_TEXTURE_IMAGE_UNITS":GL_MAX_COMPUTE_TEXTURE_IMAGE_UNITS,
#data returns one value, the maximum supported texture image units that can be used to access texture maps from the compute shader. The value may be at least 16. See glActiveTexture.
"GL_MAX_COMPUTE_UNIFORM_COMPONENTS":GL_MAX_COMPUTE_UNIFORM_COMPONENTS,
#data returns one value, the maximum number of individual floating-point, integer, or boolean values that can be held in uniform variable storage for a compute shader. The value must be at least 1024. See glUniform.
"GL_MAX_COMPUTE_ATOMIC_COUNTERS":GL_MAX_COMPUTE_ATOMIC_COUNTERS,
#data returns a single value, the maximum number of atomic counters available to compute shaders.
"GL_MAX_COMPUTE_ATOMIC_COUNTER_BUFFERS":GL_MAX_COMPUTE_ATOMIC_COUNTER_BUFFERS,
#data returns a single value, the maximum number of atomic counter buffers that may be accessed by a compute shader.
"GL_MAX_COMBINED_COMPUTE_UNIFORM_COMPONENTS":GL_MAX_COMBINED_COMPUTE_UNIFORM_COMPONENTS,
#data returns one value, the number of words for compute shader uniform variables in all uniform blocks (including default). The value must be at least 1. See glUniform.
#"GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS":GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS,
#data returns one value, the number of invocations in a single local work group (i.e., the product of the three dimensions) that may be dispatched to a compute shader.
#"GL_MAX_COMPUTE_WORK_GROUP_COUNT":GL_MAX_COMPUTE_WORK_GROUP_COUNT,
#Accepted by the indexed versions of glGet. data the maximum number of work groups that may be dispatched to a compute shader. Indices 0, 1, and 2 correspond to the X, Y and Z dimensions, respectively.
#"GL_MAX_COMPUTE_WORK_GROUP_SIZE":GL_MAX_COMPUTE_WORK_GROUP_SIZE,
}

class Spec:
    def __init__(self):
        self.comp = COMPUTE_SHADER_SPEC.copy()
    def ComputeShader(self):
        if not bool(glGenBuffers):
            log.Error("Error Disable OpenGL")
            return False
        for k in COMPUTE_SHADER_SPEC:
            v = glGetIntegerv(COMPUTE_SHADER_SPEC[k])
            #print(k,"  ",v)
            self.comp[k] = v
        self.comp["GL_MAX_COMPUTE_WORK_GROUP_COUNT"] = []
        self.comp["GL_MAX_COMPUTE_WORK_GROUP_SIZE"]  = []
        for i in range(3):
             v = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT,i)
             self.comp["GL_MAX_COMPUTE_WORK_GROUP_COUNT"].append(v[0])
             v = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_SIZE, i)
             self.comp["GL_MAX_COMPUTE_WORK_GROUP_SIZE"].append(v[0])

        #print(glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS,0))
        log.Info("ComputeShaderSpec \n%s"%dictString(self.comp))


