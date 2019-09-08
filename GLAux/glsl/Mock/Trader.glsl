uniform  int   Total;
uniform  int   OFS;
uniform  int   MODE;
uniform  int   XID;
uniform  int   BULL;
uniform  int   STID[21];
uniform  float lot    = 10.;


int TOTAL = Total;
int Ofs = OFS;
int BBR = BULL;


#define PORT_NUM  8
//#define DEBUG
#define VALID


#ifdef VALID
uniform  int  PARATH;
uniform  int  VID;
#define shaX 256
#define scid(x) (PARATH*VID + x)
//#define prid(inst,i) (8*inst + i)
#define PMAX 10
#define prid(inst,i) (PMAX*inst + i)

struct sScore
{
    float  prob[PORT_NUM];
    float  prof[PORT_NUM];

};


layout( std430, binding = 3 ) buffer Score{
	sScore score[];
};


#define ASSETLIMIT 1024
struct sAsset
{
    float  range[(PORT_NUM-1)*ASSETLIMIT];
    float  bull[ (PORT_NUM-1)*ASSETLIMIT];
    float  bear[ (PORT_NUM-1)*ASSETLIMIT];

};


layout( std430, binding = 9 ) buffer Asset{
	sAsset asset[];
};


#define ASSET(i,val) {if(i < ASSETLIMIT)if(BBR==0){asset[id.x].range[id.y*ASSETLIMIT + (i)] = val;}else if(BBR == 1){asset[id.x].bull[id.y*ASSETLIMIT + (i)] = val;}else{asset[id.x].bear[id.y*ASSETLIMIT + (i)] = val;}}

struct sParams
{
    float  p[PMAX*(PORT_NUM-1)];

};


layout( std430, binding = 2 ) buffer ParamsR{
	sParams pa_R[];
};



layout( std430, binding = 8 ) buffer ParamsT{
	sParams pa_T[];
};

#define ENMAX 100
#define EXMAX 101

struct sDrawProp
{
     int    stid;
     float   std;
     float ry[2];
     float rx[2];
     int   entry[100];
     int   exit[101];

};
layout( std430, binding = 7 ) buffer DrawProp{
	sDrawProp dprop[];
};

#else

#define shaX 1000

#endif

layout(local_size_x = shaX,local_size_y = 1,local_size_z = 1) in;
///PARAMETERS

float PMFI_TH     = 100;
int   PMFI_ROLL   = 26;
int   PMFI_DROLL  = 12;
float PMFI_EMA    = 12;


float PBB_FSSC    = 100;
int   PBB_AMA     = 12;
int   PBB_EMA1    = 12;
int   PBB_EMA2    = 26;



float PBB_BANDTH  = 0.15;
int   PBB_LOTMAX  = 26;

ivec3 id;



struct sRates
{
    float  open[PORT_NUM];
    float  high[PORT_NUM];
    float   low[PORT_NUM];
	float close[PORT_NUM];
	float   vol[PORT_NUM];

	float   mu[PORT_NUM];
	float   mu2[PORT_NUM];
	float   mfi[PORT_NUM];
	float   mfi2[PORT_NUM];
	float   asset[PORT_NUM];
};

layout( std430, binding = 5 ) buffer Rates{
	sRates _rates[];
};


struct sVal
{
   float  tval;
   float  open;
   float   vol;
};

shared sVal rates[2000];


struct sACNT
{
	uint   i[PORT_NUM];

};

layout( std430, binding = 4 ) buffer ACNT{
	sACNT ac[];
};

#ifdef DEBUG
struct sDeb
{
    float  v[PORT_NUM];
    float  v2[PORT_NUM];

};


layout( std430, binding = 3 ) buffer Deb{
	sDeb deb[];
};

#endif

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
      d.Balance = 100000;
      d.on      = false;
      d.Lot     = 0;
      d.Margin  = 0;
      if(MODE == 5)ASSET(0,d.Balance);
}



float SQ2 = sqrt(2.);

struct BB{

       int xid;
       int inst;
       int idx;

       float close;
       float S1[125],S2[125];
       float s1,s2;
       int      rid;
       int    ama;
       float ema1,ema2;

       float        mu,mu2,diff;
       float        dir_mu,dir_mu2;
       float         gc_mu;
       float       std;
       float      fssc;
       float  position;
       float       dir;


      /*
       float diff,diff2,dir,dir_mu;
       int signal,mu_signal;

       int status;
       int cstatus;


       float diff_gc;
       int signal_gc;
       */

};

void BB_Calc(inout BB bb){

    if((bb.idx-Ofs)< bb.ama){

           int idx = (bb.idx-Ofs);

           bb.S1[idx] = rates[idx].tval;
           bb.s1 +=  bb.S1[idx];
           if(idx!=0)bb.S2[idx] = bb.S1[idx]- bb.S1[idx-1];
           if(idx!=0)bb.s2   += bb.S2[idx];

           bb.mu  = bb.s1 / float(idx+ 1);
           bb.rid = idx;

    }else{

          float rsi,FSSC;
          int   irsi;
          int idx = (bb.idx-Ofs);

           bb.rid     =  (bb.rid + 1)%int(bb.ama);

           bb.s1         -=  bb.S1[bb.rid];
           bb.S1[bb.rid] =   rates[idx].tval;
           bb.s1         +=  bb.S1[bb.rid];


           bb.s2              -=  bb.S2[bb.rid];
           bb.S2[bb.rid]       =  bb.S1[bb.rid] - bb.S1[(bb.rid-1+bb.ama)%bb.ama];
           bb.s2              +=  bb.S2[bb.rid];


           float _dmu;
           _dmu      =  bb.s2;
           if(_dmu == 0)FSSC = 0.99;
           else{
               irsi   =  (bb.rid + 1)%bb.ama;
               rsi    =  abs(bb.S1[bb.rid] - bb.S1[irsi])/_dmu;
	           FSSC   =  float(pow((rsi * bb.ema1 + bb.ema2), float(2.)));
		       FSSC   = (log(FSSC + 1)*SQ2);
		       if(FSSC > 0.99)FSSC = 0.99;
		   }

		     bb.dir_mu  = FSSC * (bb.S1[bb.rid] - bb.mu);
		     bb.mu      += bb.dir_mu;
             _dmu       = bb.s1/float(bb.ama);
             bb.dir_mu2 =  _dmu - bb.mu2;
		     bb.mu2     =  _dmu;

      }

     bb.idx++;
     int i = bb.idx-1;
     if(MODE == 2){
                _rates[i].mu[bb.inst]  =  bb.mu;
                _rates[i].mu2[bb.inst]  =  bb.mu2;
              }
     if(MODE == 3 && bb.xid == XID){
                _rates[i].mu[bb.inst]  =  bb.mu;
                _rates[i].mu2[bb.inst]  =  bb.mu2;
              }

}

void BB_Set(inout BB bb,int Xid,int inst)
{
      bb.xid  =  Xid;
      bb.ama  =  PBB_AMA;
      bb.ema1 = 2./(1.+ float( PBB_EMA1));
      bb.ema2 = 2./(1.+ float( PBB_EMA2));
      bb.s1 = 0.;bb.s2 = 0.;

      bb.fssc      =   PBB_FSSC;//FSSC/std;
      bb.inst      =   inst;
      bb.idx       =   Ofs; bb.S2[0] = 0.;
      BB_Calc(bb);


             int i = bb.idx-1;
             if(MODE == 2){
               _rates[i].mu[bb.inst]  =  bb.mu;
               _rates[i].mu2[bb.inst]  =  bb.mu2;
             }

             if(MODE == 3 && bb.xid == XID){
               _rates[i].mu[bb.inst]  =  bb.mu;
               _rates[i].mu2[bb.inst]  =  bb.mu2;
             }


}






struct iMFI{

            int   inst;
            int    idx;

            float PMF[120];
            float NMF[120];
            float Pmf,Nmf;
            float _Pre;
            float  Mfi;
            int    rid;

            float sMfi;
            float _ema;

            int      roll;
            int      state;
            int      signal;

};

void MFI_Set(inout iMFI mfi,int _roll,int inst)
{
      mfi.inst = inst;
      mfi.roll = _roll;
      mfi.rid  =  0;
      mfi.idx  =  Ofs;
}

float MFI_Ema(inout iMFI mfi)
{
    mfi.sMfi = mfi.sMfi +  mfi._ema*(mfi.Mfi - mfi.sMfi);
    return mfi.sMfi;
}

float MFI_Calc(inout iMFI mfi)
{

      int inst = mfi.inst;
      int idx = (mfi.idx-Ofs);

       if(mfi.idx == Ofs){
            mfi._Pre = rates[idx].tval;
            mfi.Nmf =  mfi.Pmf  = 0;
            mfi.Mfi  = 50;mfi.sMfi = mfi.Mfi;

      }else{

            float  _Curr = 0.;
            float  vol   = rates[idx].vol;
            if(vol > 0){

                _Curr   =  rates[idx].tval;
                if(mfi.roll<(mfi.idx-Ofs)){ mfi.Pmf -= mfi.PMF[mfi.rid];mfi.Nmf -=  mfi.NMF[mfi.rid];}
                mfi.NMF[mfi.rid] = 0.;mfi.PMF[mfi.rid] = 0.;
                if(_Curr > mfi._Pre){ mfi.PMF[mfi.rid]  = vol*_Curr;}
                if(_Curr < mfi._Pre){ mfi.NMF[mfi.rid]  = vol*_Curr;}
                mfi.Pmf +=  mfi.PMF[mfi.rid];mfi.Nmf +=  mfi.NMF[mfi.rid];
                mfi._Pre = _Curr;

                if(mfi.Nmf != 0.0)mfi.Mfi=100.0-100.0/(1 + mfi.Pmf/mfi.Nmf);
                else          mfi.Mfi=100.0;
                mfi.rid =  (mfi.rid + 1)%mfi.roll;
                MFI_Ema(mfi);
            }
      }
      mfi.idx++;

      return mfi.Mfi;
}


struct MFI_Cros{
         int   Xid;
         iMFI mfi[2];
         float _Pre[2];
         float _diff;
         float signal;
         float status;
};



void SetMFICROS(inout MFI_Cros mfic,int xid,int inst,int R1,int R2,float __ema){

             mfic.Xid = xid;
             mfic.mfi[1]._ema = mfic.mfi[0]._ema  = 2./(1.+ __ema);
             MFI_Set(mfic.mfi[0],R1,inst);MFI_Set(mfic.mfi[1],R2,inst);
             MFI_Calc(mfic.mfi[0]);
             MFI_Calc(mfic.mfi[1]);

             mfic._Pre[0] =  mfic.mfi[0].sMfi;
             mfic._Pre[1] =  mfic.mfi[1].sMfi;
             mfic._diff   =  mfic._Pre[1] - mfic._Pre[0];



             int i = mfic.mfi[0].idx-1;
             if(MODE == 1){
               _rates[i].mfi[inst]  = mfic.mfi[0].sMfi;
               _rates[i].mfi2[inst] = mfic.mfi[1].sMfi;
             }
             if(MODE == 3 && mfic.Xid == XID){
                _rates[i].mfi[inst]  = mfic.mfi[0].sMfi;
                _rates[i].mfi2[inst] = mfic.mfi[1].sMfi;
             }


}

void Calc_MFICROS(inout MFI_Cros mfic){

             float _Curr[2];
             float diff;
             MFI_Calc(mfic.mfi[0]);
             MFI_Calc(mfic.mfi[1]);

             _Curr[0] =  mfic.mfi[0].sMfi;
             _Curr[1] =  mfic.mfi[1].sMfi;


             int i = mfic.mfi[0].idx-1;
             int inst = mfic.mfi[0].inst;


             if(MODE == 1){
               _rates[i].mfi[inst]  = mfic.mfi[0].sMfi;
               _rates[i].mfi2[inst] = mfic.mfi[1].sMfi;
             }

             if(MODE == 3 && mfic.Xid == XID){
                _rates[i].mfi[inst]  = mfic.mfi[0].sMfi;
                _rates[i].mfi2[inst] = mfic.mfi[1].sMfi;
             }



             diff   = _Curr[1] - _Curr[0];
             mfic.signal = 0;
             if(diff*mfic._diff < 0){
                  float dir;
                  dir = ((_Curr[0] - mfic._Pre[0]) >0)?1:-1;
                  mfic.status = (mfic._Pre[0] + mfic._Pre[1])/2.;
                  mfic.signal = dir;
/*
                  if( (PMFI_TH - mfic.status) > 0. && dir > 0){
                        mfic.signal = 1;
                  }else if( (mfic.status-  (100.-PMFI_TH)) > 0. && dir < 0.){
                        mfic.signal = -1;
                  }
*/
             }
             mfic._diff = diff;
             mfic._Pre[0] = _Curr[0];mfic._Pre[1] = _Curr[1];

}



#define REV  100.
#define UNIT 1000.
#define ACUR 0   //USD
#define MAINTAIN 1.   //USD
#define MAINTAIN_OFS 0.01
#define NANPIN  -0.05
shared int MARGINTYPE =0;



void TrendSignal(inout Deal d,inout BB bb,in MFI_Cros mfic){


     int   idx = (bb.idx-Ofs);
     float margin = 0.;
     float eff    = 0.;
     float _diff,signal_gc;
     float status;
     //static int  _mu_gc;
     _diff = bb.mu2 - bb.mu;
     signal_gc =  0;

     if(bb.diff*_diff < 0){
           signal_gc = (_diff > 0)?1:-1;
           //mu_gc  =   ((_diff*dir_mu) > 0)?_mu_gc:0;
     }
     bb.diff    =_diff;
     if(  float(signal_gc)*(bb.dir_mu) <= 0){
          signal_gc =   0;
     }

     if( (rates[idx-1].tval  - bb.mu2)*bb.dir_mu > 0){
         status =  (bb.dir_mu > 0)?1:-1;
     }else status = 0;

     if(MODE == 2){
               int i = bb.idx-1;
               _rates[i].mu[bb.inst]  =  float(PBB_LOTMAX)*mfic.signal*status;
               _rates[i].mu2[bb.inst] =  status*float(BBR);
     }

     //if(bb.position < 0.5)d.Nums++;

            d.Prof = 0.;

            for(int i =0;i<d.Poth;i++){
                float Prof  = (rates[idx+1].open - d.open[i])*d.AB;
                if(MARGINTYPE==1)Prof /= rates[idx+1].open;
                if(d.Poth-1==i){
                    d.npn   = 0;
                    margin = 1.;
                    if(MARGINTYPE==0)margin = margin*d.open[i];
                    if( (REV*Prof/margin) < NANPIN){
                            d.npn = 1;
                    }
                }
                d.Prof     += Prof;
            }

            d.Prof  = d.Prof*lot*REV*UNIT;
            bb.dir  = 0;

            if(  int(mfic.signal*status) == 1){
              if( (int(status)*BBR) == 1 ){
                    bb.dir = BBR;
                    if(MODE == 2)_rates[bb.idx-1].mu2[bb.inst] =  5.*status*float(BBR);
              }
            }

            if( bb.dir != 0 ){

             if(d.Poth < PBB_LOTMAX){

               margin = lot*UNIT;
               if(MARGINTYPE==0)margin = margin*rates[idx+1].open;
               eff     = d.Balance + d.Prof;
               margin  += d.Margin;



               if( eff/margin > (MAINTAIN+MAINTAIN_OFS)){
                  d.Margin  += margin;
                  d.Poth    = 1;
                  d.open[0] = rates[idx+1].open;
                  d.AB      = float(bb.dir);
                  d.Lot     = lot;
                  if(MODE == 3)dprop[bb.inst].entry[int(d.ENums)] = idx-1;
                  d.ENums++;

               }
              }
            }

   //  }else{

        if(d.Poth>0){

            bool exit = false;

            if( (int(signal_gc)*BBR) == 1){
                    exit = true;
            }

            if(exit){
                d.Balance   += d.Prof;
                d.Margin    = 0;
                if(MODE == 3)dprop[bb.inst].exit[int(d.Nums)] = idx-1;
                d.Nums++;
                if(d.Prof > 0)d.VNums++;
                d.Prof  = 0.;
                d.Poth  = 0;
                d.Lot   = 0;
            }else{

                    if(d.npn == 1){
                            int i = d.Poth - 1;
                            margin = lot*UNIT;
                            if(MARGINTYPE==0)margin = margin*rates[idx+1].open;
                            eff  = d.Balance + d.Prof;
                            margin += d.Margin;
                            if( eff/margin > MAINTAIN){
                                    d.Margin  += margin;
                                    d.open[d.Poth] = rates[idx+1].open;
                                    d.Lot     += lot;
                                    if(MODE == 3)dprop[bb.inst].entry[int(d.ENums)] = idx-1;
                                    d.ENums++;
                                    d.Poth++;
                            }
                    }

            }
      }

     if(MODE == 3 && mfic.Xid == XID){
          int _i = bb.idx -1;
          if(d.Prof + d.Balance>0)_rates[_i].asset[bb.inst]  = d.Prof + d.Balance;
          else _rates[_i].asset[bb.inst]  = 0.;
     }

     if(MODE ==5){
          if(d.Prof + d.Balance>0){ASSET(idx-1,d.Prof + d.Balance);}
          else { ASSET(idx-1,0); }
          // ASSET(idx-1,100000. + d.Prof);// float(idx-1));}//d.Prof + d.Balance);}
     }


     if(idx == TOTAL){
                 if(d.Poth!=0){
                    if(MODE == 3)dprop[bb.inst].exit[int(d.Nums)] = TOTAL-1;
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

}



void Signal(inout Deal d,inout BB bb,in MFI_Cros mfic){

     float margin = 0.;
     float eff    = 0.;

     float low,high; int idx = (bb.idx-Ofs);
     high = bb.mu + bb.fssc;
     low  = bb.mu - bb.fssc;

     bb.position = (rates[idx-1].tval - low)/(high - low);
     //if(bb.position < 0.5)d.Nums++;

     d.Prof = 0.;

     if(d.Poth == 0){
         //if(  ((mfic.signal == 1.) && (bb.position < PBB_BANDTH))  ||  ((mfic.signal == -1.) && (bb.position > (1-PBB_BANDTH))) ){
         bb.dir = 0;
         if( mfic.signal == 1.)
            if(bb.position < PBB_BANDTH) bb.dir = 1;

         if( mfic.signal == -1.)
            if(bb.position > (1-PBB_BANDTH)) bb.dir = -1;

         if( bb.dir != 0 ){
               margin = lot*UNIT;
               if(MARGINTYPE==0)margin = margin*rates[idx+1].open;
               eff     = d.Balance;
               margin += d.Margin;
               if( eff/margin > (MAINTAIN+MAINTAIN_OFS)){
                  d.Margin  += margin;
                  d.Poth    = 1;
                  d.open[0] = rates[idx+1].open;
                  d.AB      = float(bb.dir);
                  d.Lot     = lot;
                  if(MODE == 3)dprop[bb.inst].entry[int(d.ENums)] = idx-1;
                  d.ENums++;
               }
         }

     }else{

            d.Prof = 0.;
            for(int i =0;i<d.Poth;i++){
                float Prof  = (rates[idx+1].open - d.open[i])*d.AB;
                if(MARGINTYPE==1)Prof /= rates[idx+1].open;
                if(d.Poth-1==i){
                    margin = 1.;
                    d.npn=0;
                    if(MARGINTYPE==0)margin = margin*d.open[i];
                    if( (REV*Prof/margin) < NANPIN){
                            d.npn=1;
                    }
                }
                d.Prof     += Prof;
            }

            d.Prof  = d.Prof*lot*REV*UNIT;
            bool exit = false;

            if( d.AB == -1){

                if(bb.position < PBB_BANDTH){
                    exit = true;
                }

            }else{
                if(bb.position > (1-PBB_BANDTH)){
                        exit = true;
                }
            }

            if(exit){
                d.Balance   += d.Prof;
                d.Margin    = 0;
                if(MODE == 3)dprop[bb.inst].exit[int(d.Nums)] = idx-1;
                d.Nums++;
                if(d.Prof > 0)d.VNums++;
                d.Prof  = 0.;
                d.Poth  = 0;
                d.Lot   = 0;
            }else{
                    if(d.npn== 1){
                            margin = lot*UNIT;
                            if(MARGINTYPE==0)margin = margin*rates[idx+1].open;
                            eff  = d.Balance + d.Prof;
                            margin += d.Margin;
                            if( eff/margin > MAINTAIN){
                                    d.Margin  += margin;
                                    d.open[d.Poth] = rates[idx+1].open;
                                    d.Lot     += lot;
                                    if(MODE == 3)dprop[bb.inst].entry[int(d.ENums)] = idx-1;
                                    d.ENums++;
                                    d.Poth++;

                            }
                    }

            }
     }

     if(MODE == 3){
                    int _i = bb.idx -1;
                    _rates[_i].asset[bb.inst]  = d.Prof + d.Balance;
                    //if(d.Prof + d.Balance>0)_rates[_i].asset[bb.inst]  = d.Prof + d.Balance;
                    //else _rates[_i].asset[bb.inst]  = 0.;
     }
     if(MODE ==5){
                    if(d.Prof + d.Balance>0){ASSET(idx-1,d.Prof + d.Balance);}
                    else { ASSET(idx-1,0); }
     }


     if(idx == TOTAL){

                 if(d.Poth!=0){
                    if(MODE == 3)dprop[bb.inst].exit[int(d.Nums)] = TOTAL-1;
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

}


float ZOOM = pow(10.,3.);


void main() {

    id   = ivec3(gl_GlobalInvocationID.xyz);
    if(PARATH==1024)id.y = VID;
    if(MODE ==  5|| MODE == 6)BBR = id.z - 1;
    else BBR = BULL;

    if(OFS < 0){
       Ofs    = STID[id.y + (BBR+1)*7];
       TOTAL  = Total - Ofs;
    }else{
       Ofs = OFS;
       TOTAL = Total;
    }

    //"EURUSD","GBPUSD","AUDUSD","NZDUSD","USDCAD","USDCHF","USDJPY","KUUSD"
    if(id.x == 0){
        if(ACUR==0){
            if(id.y == 7)MARGINTYPE = -1;
            else if(id.y<=3)MARGINTYPE =0;
            else MARGINTYPE =1;
        }
    }

    if(id.z == 0)ac[id.x].i[id.y]  = uint(0);
    if(id.x < 100){dprop[id.y].entry[id.x] =0;dprop[id.y].exit[id.x] =0;}

    for(int i=0;i<7;i++){
       int idx = shaX*i + id.x;
       if(TOTAL+1 >= idx){
            rates[idx].open   =  _rates[idx + Ofs].open[id.y];
            rates[idx].vol    =  _rates[idx + Ofs].vol[id.y];
            rates[idx].tval   = (_rates[idx + Ofs].high[id.y] + _rates[idx + Ofs].low[id.y] + _rates[idx + Ofs].close[id.y])/3.;
       }else break;
     }

     barrier();


     if(id.x >=PARATH)return;
     if(MODE <=3)if(id.x != XID)return;


#ifdef VALID

            //KEYLIST  TREND        [ 0 MFIROLL,1 MFIROLL2,2 MFI_EMA,3 BB_AM,4 BB_EM1,5 BB_EM2,6 lotmax,7 bull ]
            //KEYLIST  RANGE        [ 0 MFIROLL,1 MFIROLL2,2 MFI_EMA,3 BB_AM,4 BB_EM1,5 BB_EM2,6 BB_FSSC,7 bandTH]
            if( BBR == 0){
                    PMFI_ROLL   = int(pa_R[id.x].p[prid(id.y,0)]);
                    PMFI_DROLL  = int(pa_R[id.x].p[prid(id.y,1)]);
                    PMFI_EMA    = int(pa_R[id.x].p[prid(id.y,2)]);

                    PBB_AMA     = int(pa_R[id.x].p[prid(id.y,3)]);
                    PBB_EMA1    = int(pa_R[id.x].p[prid(id.y,4)]);
                    PBB_EMA2    = int(pa_R[id.x].p[prid(id.y,5)]);
                    PBB_FSSC    = pa_R[id.x].p[prid(id.y,6)];
                    PBB_BANDTH  = pa_R[id.x].p[prid(id.y,7)];

            }else{

                    PMFI_ROLL   = int(pa_T[id.x].p[prid(id.y,0)]);
                    PMFI_DROLL  = int(pa_T[id.x].p[prid(id.y,1)]);
                    PMFI_EMA    = int(pa_T[id.x].p[prid(id.y,2)]);
                    PBB_AMA     = int(pa_T[id.x].p[prid(id.y,3)]);
                    PBB_EMA1    = int(pa_T[id.x].p[prid(id.y,4)]);
                    PBB_EMA2    = int(pa_T[id.x].p[prid(id.y,5)]);
                    PBB_LOTMAX  = 1;//int(pa_T[id.x].p[prid(id.y,6)]);
            }
#endif


     if(PBB_AMA == 0 && PMFI_ROLL == 0){
          if(MODE == 1){
               _rates[Ofs].mfi[id.y]  = -12345.;
               _rates[Ofs].mfi2[id.y] = -12345.;
          }
          if(MODE <= 4){
                score[scid(id.x)].prof[id.y] = -1.23;
                score[scid(id.x)].prob[id.y] = -1.23;
                if(MODE==3)dprop[id.y].exit[100] = 0;
          }
          atomicAdd(ac[id.x].i[id.y],1);
          return;
     }



     MFI_Cros mfic;
     SetMFICROS(mfic,id.x,id.y,PMFI_ROLL,PMFI_ROLL + PMFI_DROLL,PMFI_EMA);

     BB  bb;
     BB_Set(bb,id.x,id.y);


     Deal D;
     SetDeal(D);
     //D.on = false;D.POD.Nums =0 ;D.VNums = 0;D.Balance = 100000;
     if(MODE<=4)_rates[Ofs].asset[bb.inst]  = D.Balance;


     for(int i =1;i<TOTAL;i++){

         Calc_MFICROS(mfic);
         BB_Calc(bb);
         if(BBR==0)Signal(D,bb,mfic);
         else TrendSignal(D,bb,mfic);
         //if(TOTAL-1 == bb.idx)break;
     }


#ifdef VALID




     if(VID >= 0 && MODE <= 4){

            if(D.Nums == 0){
                score[scid(id.x)].prob[id.y] = 0.;
            }else{
                score[scid(id.x)].prob[id.y] = D.VNums/D.Nums;
            }
            //if(D.Nums >=5)score[scid(id.x)].prob[id.y] = D.Nums;
            //else score[scid(id.x)].prob[id.y] = 0.;
            score[scid(id.x)].prof[id.y] = D.Balance;
            if(MODE == 3){
                dprop[id.y].exit[EXMAX-1] = int(D.Nums);
                dprop[id.y].entry[ENMAX-1] = int(D.ENums);
            }
     }

#endif



    atomicAdd(ac[id.x].i[id.y],1);

}