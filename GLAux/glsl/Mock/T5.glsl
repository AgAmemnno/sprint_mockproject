#include <sRates.glsl>
#include <Mock1/uniform.glsl>
#include <Mock1/parameter.glsl>
#include <Mock1/mfi.glsl>
#include <Mock1/ac.glsl>

#define YZid(id) (id.y*WG.z+id.z)
layout(local_size_x = SHXTH, local_size_y = SHYTH, local_size_z = SHZTH) in;


void main() {

    uvec3 id   = gl_GlobalInvocationID;
    uvec3 lid  = gl_LocalInvocationID;
    WG  = gl_NumWorkGroups;

    PMFI_ROLL   = 5 + int(lid.x % 64);
    PMFI_DROLL  = int(5 + id.y);//12~
    PMFI_EMA    = int(5 + id.z);


    for (uint i =0;i<uint(ceil(float(TOTAL)/float(SHXTH)));i++){
        uint  idx = lid.x + SHXTH*i;
        if (idx > TOTAL)break;
        rates[idx].tval =   (_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.;
        rates[idx].open =   _rates[idx].open;
    }

    barrier();

    IDX = 0;

    MFI_Cros mfic;
    SetMFICROS(mfic);


    for (int idx = 1;idx<TOTAL;idx++){
        IDX = idx;
        Calc_MFICROS(mfic);
    }

    atomicAdd(ac[YZid(id)].i[lid.x],uint(1));

}