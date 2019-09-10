#include <sRates.glsl>
#include <Mock1/uniform.glsl>
#include <Mock1/parameter.glsl>
#include <Mock1/mfi.glsl>
#include <Mock1/ama.glsl>
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

    PAMA_AMA     = 5 + int(lid.x % 64);
    PAMA_EMA1    = int(5 + id.y);//12~
    PAMA_EMA2    = int(5 + id.z);
    PAMA_FSSC    = 0.008;
    PAMA_BANDTH  = 0.3;


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

    AMA  ama;
    AMA_Set(ama);


    for (int idx = 1;idx<TOTAL;idx++){
        IDX = idx;
        Calc_MFICROS(mfic);
        AMA_Calc(ama);
        //if(BBR==0)Signal(D,ama,mfic);
        //else TrendSignal(D,ama,mfic);
    }

    atomicAdd(ac[YZid(id)].i[lid.x],uint(1));

}