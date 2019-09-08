#include <sRates.glsl>
#include <ac.glsl>

layout(local_size_x = 1024, local_size_y = 1, local_size_z = 1) in;


void main() {

    ivec3 id   = ivec3(gl_GlobalInvocationID.xyz);

    atomicAdd(ac[id.z].i[id.y],1);

}