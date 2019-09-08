#include <sRates.glsl>
#include <Mock1/uniform.glsl>
#include <Mock1/parameter.glsl>
#include <Mock1/mfi.glsl>
#include <Mock1/ama.glsl>
#include <Visual/mock1_buffer.glsl>
#include <Mock1/ac.glsl>

#define YZid(id) (id.y*WG.z+id.z)
layout(local_size_x = SHXTH, local_size_y = SHYTH, local_size_z = SHZTH) in;

uniform int PID = 0;

void main() {

    uvec3 id   = gl_GlobalInvocationID;
    uvec3 lid  = gl_LocalInvocationID;

    WG  = gl_NumWorkGroups;

    for (uint i =0;i<uint(ceil(float(SHRTH)/float(SHXTH)));i++){
        uint  idx = lid.x + SHXTH*i;
        if (idx >= SHRTH)break;
        rates[idx].tval =   (_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.;
        rates[idx].open =   _rates[idx].open;
        barrier();
    }

    barrier();

    //if(lid.x != PID)return;

    PMFI_ROLL   = 5 + int(lid.x % 64);
    PMFI_DROLL  = int(5 + id.y);//12~
    PMFI_EMA    =  7.4;//int(5 + id.z);

    PAMA_AMA     = 57;//30 + int(lid.x % 64);
    PAMA_EMA1    = int(85 + id.y);//12~
    PAMA_EMA2    = int(103 + id.z);
    PAMA_FSSC    = 0.008;
    PAMA_BANDTH  = 0.22;


    IDX = SIDX = 0;

    MFI_Cros mfic;
    SetMFICROS(mfic);

    AMA  ama;
    AMA_Set(ama);

    uint Ofs = 0;

    for (IDX = 1;IDX<TOTAL;IDX++){

        SIDX++;
        Calc_MFICROS(mfic);
        AMA_Calc(ama);

        vis[IDX].mu[YZid(id)]   =  ama.mu;//ama.mu2;//0.5*sin(float(SIDX % SHRTH)/float(SHRTH))  + 0.5;//
        vis[IDX].mu2[YZid(id)]  =  ama.mu2;//0.5*cos(float(SIDX % SHRTH)/float(SHRTH))  + 0.5;//

        if(SIDX == SHRTH-1){
            Ofs +=  SHRTH;
            for(uint i =0;i<uint(ceil(float(SHRTH)/float(SHXTH)));i++){
                uint  idx = lid.x + SHXTH*i;
                if (idx >= SHRTH)break;
                uint   _idx = Ofs + idx;
                if(_idx >= TOTAL)break;
                rates[idx].tval =   (_rates[_idx].high + _rates[_idx].low + _rates[_idx].close)/3.;
                rates[idx].open =   _rates[_idx].close;
                barrier();
            }
            barrier();
            SIDX = -1;
        }
    }

    barrier();
    atomicAdd(ac[YZid(id)].i[lid.x],uint(1));
}

    //atomicAdd(ac[YZid(id)].i[lid.x],uint(1));

