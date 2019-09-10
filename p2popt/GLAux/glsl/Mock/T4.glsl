#include <sRates.glsl>
#include <ac.glsl>

uniform int   TOTAL = 20000;
uniform int GLOBAL =0;

//Const
#define SHTH 1024
#define RTH  4096

//Global Variable
int IDX;

//Shared Variable
struct sVal
{
   float   tval;
   float   open;
};

shared sVal rates[RTH];

layout(local_size_x = SHTH, local_size_y = 1, local_size_z = 1) in;


#define round5(a) (floor((a)*100000.)/100000.)



void main() {

    uvec3 id   = gl_GlobalInvocationID;
    uvec3 lid  = gl_LocalInvocationID;


    float ema = 2./(1. + 26.);
    float v ;
if(GLOBAL==1){
    int idx = 0;
    v = (_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.;
    if(id.x + id.y + id.z  == 0){
            _rates[idx].open =  v;
    }
    for (idx =1;idx<TOTAL;idx++){
        float v0   =  (_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.;
        v = v + ema*(v0 - v);
        if(id.x + id.y + id.z  == 0){
            _rates[idx].open =  v0;
        }
    }

}else {
    for (uint i =0;i<uint(ceil(float(RTH)/float(SHTH)));i++){
        uint  idx = lid.x + SHTH*i;
        if (idx > RTH)break;
        rates[idx].tval =   (_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.;
    }
    barrier();

    int idx = 0;
    v = rates[idx].tval;

    if(id.x + id.y + id.z  == 0){
           _rates[idx].date =  rates[idx].tval;
    }
    for (idx = 1;idx<TOTAL;idx++){
        float v0  =  rates[idx].tval;
        v = v + ema*(v0 - v);
        if(id.x + id.y + id.z  == 0){
            _rates[idx].date =  v;
        }
    }
}
    atomicAdd(ac[id.z].i[id.y],uint(v*100000));
}