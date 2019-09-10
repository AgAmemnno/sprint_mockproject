#include <sRates.glsl>
#include <ac.glsl>
uniform int   TOTAL = 20000;
layout(local_size_x = 1024, local_size_y = 1, local_size_z = 1) in;


void main() {

    ivec3 id   = ivec3(gl_GlobalInvocationID.xyz);

    float a = 0.;
    for(int i =1;i<TOTAL;i++){
        a += exp(5.);
        for(int j =0;j<100;j++){
            a += exp(j);
        }
    }

    atomicAdd(ac[id.z].i[id.y],1);

}