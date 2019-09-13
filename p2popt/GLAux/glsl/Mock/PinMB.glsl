#include <Visual/Depth.glsl>
#include <Mock1/inout.glsl>

vec3 ra[8] = vec3[8](vec3(5,60,1),vec3(5,100,1),vec3(5,50,1.2),vec3(12,120,1),vec3(12,120,1),vec3(21,210,1),vec3(0.005,0.01,0.001),vec3(0.1,0.5,0.05));

shared uint P[2048];

#define SHX  1024
layout(local_size_x = SHX, local_size_y = 1, local_size_z = 1) in;

uniform int  IOTH = 0;
uniform ivec2 AX;

void main(){
    //512*512  block 16*16   32 = 512/16
    #define thd  32

    uvec3  id     =   gl_GlobalInvocationID;
    uvec2  uv     =   id.yz*thd;
    uint  lid     =   gl_LocalInvocationID.x;
          uv      =   uv + uvec2(lid%thd,lid/thd);
    uint gid      =   uv.y*DEPTH_SIZE + uv.x;
    uint _i       =   lid;

    for(int i=0;i<2;i++){
        if(_i >= uint(IOTH))break;
        uint x =  uint(DEPTH_SIZE*(io[_i].x[AX.x] - ra[AX.x][0])/(ra[AX.x][1] -ra[AX.x][0]));
        uint y =  uint(DEPTH_SIZE*(io[_i].x[AX.y] - ra[AX.y][0])/(ra[AX.y][1] -ra[AX.y][0]));
        P[_i]  = y*DEPTH_SIZE + x;
        _i += SHX*(i+1);
    }
    barrier();

    if(dep[gid].c == 1){
           for(int i=0;i<IOTH;i++){
               if(P[i] == gid){
                   io[i].sel = 1;
               }
           }
    }

};
