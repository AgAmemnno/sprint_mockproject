#include <Visual/mock1_buffer.glsl>
#include <Visual/mock2_prop.glsl>
#include <sRates.glsl>

uniform int PROG;
uniform int LTH;
uniform int STID;

layout(local_size_x = 1024,local_size_y = 1,local_size_z = 1) in;


shared uint  MAX= 0,MIN=10000000;


void main() {

    if (PROG == 0){

        int idx    =  int(gl_GlobalInvocationID.x);
        int spid   =  int(gl_GlobalInvocationID.y);

        if (LTH <= idx)return;
        float R = 100000.;

        float mu;
        int _i = idx;
        for (int i =0; i<30;i++){
            //mu = vis[STID + idx].mu[spid];
            mu = _rates[STID + _i].close;
            atomicMin(MIN, uint(R*mu));
            atomicMax(MAX, uint(R*mu));
            _i = idx + 1024*(i+1);
            if (_i >= LTH)break;
        }

        barrier();

        if (idx ==0){

            dprop[spid].stid  = STID;
            dprop[spid].ry[0] = float(MIN)/R;
            dprop[spid].ry[1] = float(MAX)/R;
            dprop[spid].rx[0] = 0;
            dprop[spid].rx[1] = float(LTH);

        }

    }

}