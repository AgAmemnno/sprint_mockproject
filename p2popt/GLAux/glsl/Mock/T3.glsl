#include <sRates.glsl>
#include <ac.glsl>

//Const
#define SHTH 1024
#define RTH  4096

//Global Variable
int IDX;

//Shared Variable
struct sVal
{
   uint    tval;
   float   open;
};

shared sVal rates[RTH];

uniform int   TOTAL = 20000;
uniform int GLOBAL =0;

layout(local_size_x = SHTH, local_size_y = 1, local_size_z = 1) in;


#define round5(a) (floor((a)*100000.)/100000.)



void main() {

    uvec3 id   = gl_GlobalInvocationID;
    uvec3 lid  = gl_LocalInvocationID;

    uint mod31  =  2147483647;
    uint mod15  =  32768;
    uint a = 0;

if(GLOBAL==1){

    for (int idx =1;idx<TOTAL;idx++){
        //float b   = round5((_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.);
        //uint b   =  uint(100000.*round5((round5(_rates[idx].high) + round5(_rates[idx].low) + round5(_rates[idx].close))/3.));
        //uint b   =  uint(100000.*round5((_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.));
        uint b   =  uint(100000.*(_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.);
        a = (a + b)%mod31;
        if(id.x + id.y + id.z  == 0){
            _rates[idx].date =  float(b)/100000;
        }
    }

}else {
    for (uint i =0;i<uint(ceil(float(RTH)/float(SHTH)));i++){
        uint  idx = lid.x + SHTH*i;
        if (idx > RTH)break;
        //rates[idx].tval =   round5((_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.);
        //rates[idx].tval =   uint(100000.*round5((round5(_rates[idx].high) + round5(_rates[idx].low) + round5(_rates[idx].close))/3.));
        //rates[idx].tval =  uint(100000.*round5((_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.));
        rates[idx].tval =   uint(100000.*(_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.);
    }
    barrier();

    for(int idx =1;idx<TOTAL;idx++){
        //float b   = rates[idx].tval;
        //a = (a + uint(b*100000))%mod31;
        uint b = rates[idx].tval;
        a = (a + rates[idx].tval)%mod31;
        if(id.x + id.y + id.z  == 0){
             _rates[idx].open = float(b)/100000;
        }
    }

    //24734720
    //24796160
}

    a = a%mod15;
    atomicAdd(ac[id.z].i[id.y],a);
}