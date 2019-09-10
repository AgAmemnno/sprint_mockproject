#include <sRates.glsl>
#include <Mock1/uniform.glsl>
#include <Mock1/parameter.glsl>
#include <Mock1/mfi.glsl>
#include <Mock1/ama.glsl>
#include <Visual/mock2_buffer.glsl>
#include <Visual/mock2_prop.glsl>
#include <Mock1/ac.glsl>

uniform int PID=0;
uniform int VIS_MODE=0;
bool Calc = false;
bool VIS  = false;

uint   YZID  = 0;
float LOT  = 10.;
float UNIT = 100000.;
float LEVER = 100.;
float MAINTAIN = 0.01;
float NANPIN = 0.15;

struct Deal{

    float      Nums;
    float     ENums;
    float     VNums;

    float         AB;
    int         Poth;
    float    Balance;
    float     Margin;
    float        Lot;
    float       Prof;
    float      close;
    float  open[200];
    int          npn;
    bool          on;

};

void SetDeal(inout Deal d){

      d.Nums =0;
      d.ENums =0;
      d.VNums =0;
      d.Poth  =0;
      d.Balance = 1000000;
      d.on      = false;
      d.Lot     = 0;
      d.Margin  = 0;

     //if(MODE == 5)ASSET(0,d.Balance);
}


void Signal(inout Deal d,inout AMA ama,in MFI_Cros mfic){

     float margin = 0.;
     float mainta = 0.;
     float eff    = 0.;

     float low,high;
     high = ama.mu + ama.fssc;
     low  = ama.mu - ama.fssc;

     ama.position = (rates[SIDX].tval - low)/(high - low);
     //if(ama.position < 0.5)d.Nums++;

     d.Prof = 0.;

     if(d.Poth == 0){
         //if(  ((mfic.signal == 1.) && (ama.position < PBB_BANDTH))  ||  ((mfic.signal == -1.) && (ama.position > (1-PBB_BANDTH))) ){
         ama.dir = 0;
         if( mfic.signal == 1.)
            if(ama.position < PAMA_BANDTH) ama.dir = 1;

         if( mfic.signal == -1.)
            if(ama.position > (1-PAMA_BANDTH)) ama.dir = -1;

         if( ama.dir != 0 ){
               margin  = LOT*UNIT*rates[SIDX+1].open/LEVER;
               eff     = d.Balance;
               mainta  = log((eff-margin)/margin)/5. + 1.;
               if( mainta > (1. + MAINTAIN)){
                  d.Margin  += margin;
                  d.Poth    = 1;
                  d.open[0] = rates[SIDX+1].open;
                  d.AB      = float(ama.dir);
                  d.Lot     = LOT;
                  if(Calc &&  VIS)dprop[YZID].entry[int(d.ENums)+1] = IDX;
                  d.ENums++;
               }
         }

     }else{

            d.Prof = 0.;
            for(int i =0;i<d.Poth;i++){
                float Prof  = (rates[SIDX+1].open - d.open[i])*d.AB;
                d.Prof     += Prof;
            }

            d.Prof  = d.Prof*LOT*UNIT;
            bool exit = false;

            if( d.AB == -1){

                if(ama.position < PAMA_BANDTH){
                    exit = true;
                }

            }else{
                if(ama.position > (1-PAMA_BANDTH)){
                        exit = true;
                }
            }

            if(exit){
                d.Balance   += d.Prof;
                d.Margin    = 0;
                if(Calc &&  VIS)dprop[YZID].exit[int(d.Nums)+1] = IDX;
                d.Nums++;
                if(d.Prof > 0)d.VNums++;
                d.Prof  = 0.;
                d.Poth  = 0;
                d.Lot   = 0;
            }else {
                float plof  = d.AB*(rates[SIDX+1].open - d.open[d.Poth-1])*LEVER;
                eff         = d.open[d.Poth-1];
                mainta      = plof/eff;
                if (mainta < -NANPIN){
                    margin  = LOT*UNIT*rates[SIDX+1].open/LEVER;
                    eff     = d.Balance + d.Prof - margin;
                    margin  += d.Margin;
                    mainta  = log(eff/margin)/5. + 1.;
                    if (mainta > (1.+MAINTAIN)){
                        d.Margin = margin;
                        d.open[d.Poth] = rates[SIDX+1].open;
                        d.Lot     += LOT;
                        if(Calc &&  VIS)dprop[YZID].entry[int(d.ENums)+1] = IDX;
                        d.ENums++;
                        d.Poth++;
                    }
                }
            }
     }

    /*
     if(MODE == 3){
                    int _i = ama.idx -1;
                    _rates[_i].asset[ama.inst]  = d.Prof + d.Balance;
                    //if(d.Prof + d.Balance>0)_rates[_i].asset[ama.inst]  = d.Prof + d.Balance;
                    //else _rates[_i].asset[ama.inst]  = 0.;
     }
     if(MODE ==5){
                    if(d.Prof + d.Balance>0){ASSET(idx-1,d.Prof + d.Balance);}
                    else { ASSET(idx-1,0); }
     }

     if(idx == TOTAL){

                 if(d.Poth!=0){
                    if(MODE == 3)dprop[ama.inst].exit[int(d.Nums)] = TOTAL-1;
                    d.Nums++;
                    if(d.Prof > 0)d.VNums++;
                 }

                if(MODE ==5){
                   ASSET(idx,d.Nums);
                   ASSET(idx+1,d.VNums);
                }

                if(MODE ==6){
                   if(d.Prof + d.Balance>0){ASSET(0,d.Prof + d.Balance);}
                   else { ASSET(0,0); }
                   ASSET(1,d.Nums);
                   ASSET(2,d.VNums);
                }


     }
        */
}


#define YZid(id) (id.y*2+id.z)
layout(local_size_x = SHXTH, local_size_y = SHYTH, local_size_z = SHZTH) in;

void Set_Param(float p1,float p2,float p3,float p4,float p5,float p6,float p7,float p8){

        PMFI_ROLL      = int(p1);//5 + int(lid.x % 64);
        PMFI_DROLL     = int(p2);//int(5 + id.y);//12~
        PMFI_EMA       = p3;//int(5 + id.z);

        PAMA_AMA     = int(p4);
        PAMA_EMA1    = int(p5);//12
        PAMA_EMA2    = int(p6);
        PAMA_FSSC    = p7;
        PAMA_BANDTH  = p8;

}

void main() {

    uvec3 id   = gl_GlobalInvocationID;
    uvec3 lid  = gl_LocalInvocationID;

    YZID = YZid(id);

    Calc = false;
    if(lid.x == PID){
         Calc = true;
    }else if(PID ==-1)Calc = true;

    VIS = false;
    if(VIS_MODE == 1)VIS = true;


    WG  = uvec3(1,2,2);//gl_NumWorkGroups;

    for (uint i =0;i<uint(ceil(float(SHRTH)/float(SHXTH)));i++){
        uint  idx = lid.x + SHXTH*i;
        if (idx >= SHRTH)break;
        rates[idx].tval =   (_rates[idx].high + _rates[idx].low + _rates[idx].close)/3.;
        rates[idx].open =   _rates[idx].open;
        barrier();
    }

    barrier();

    /*
    PMFI_ROLL   = 5;//5 + int(lid.x % 64);
    PMFI_DROLL  = 5;//int(5 + id.y);//12~
    PMFI_EMA    =  7.4;//int(5 + id.z);

    PAMA_AMA     = 57 + int(lid.x % 64);
    PAMA_EMA1    = int(71 + id.y);//12~
    PAMA_EMA2    = int(166 + id.z);
    PAMA_FSSC    = 0.008;
    PAMA_BANDTH  = 0.22;
    */
    Set_Param(47.0, 16.0, 12.2, 80.0, 91.0, 37.0, 0.008, 0.4);

    IDX = SIDX = 0;

    MFI_Cros mfic;
    SetMFICROS(mfic);

    AMA  ama;
    AMA_Set(ama);


    Deal D;
    SetDeal(D);

    uint Ofs = 0;


    for (IDX = 1;IDX<TOTAL;IDX++){

        SIDX++;

        if(Calc){
            Calc_MFICROS(mfic);
            AMA_Calc(ama);

            Signal(D, ama, mfic);

            if(VIS){
                vis[IDX].mu[YZID]   =  ama.mu;//ama.mu2;//0.5*sin(float(SIDX % SHRTH)/float(SHRTH))  + 0.5;//
                vis[IDX].mu2[YZID]  =  ama.mu2;//0.5*cos(float(SIDX % SHRTH)/float(SHRTH))  + 0.5;//
            }
        }
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
    if(D.Balance < 0)D.Balance = 0;

    if(Calc){
        atomicAdd(ac[YZID].i[lid.x],uint(D.Balance));
        if(VIS){
            dprop[YZID].entry[0] = int(D.ENums);
            dprop[YZID].exit[0]  = int(D.Nums);
        }
    }

}

    //atomicAdd(ac[YZid(id)].i[lid.x],uint(1));


