//PARAMETER
//    int PMFI_ROLL
//    int PMFI_DROLL
//    float PMFI_EMA
//Global
//    int IDX
//Shared Data
//    struct  rates

struct iMFI{

            float   PMF[120];
            float   NMF[120];
            float    Pmf,Nmf;
            float       _Pre;
            float        Mfi;
            int          rid;

            float       sMfi;
            float       _ema;

            int         roll;
            int        state;
            int       signal;

};
void MFI_Set(inout iMFI mfi,int _roll)
{
      mfi.roll = _roll;
      mfi.rid  =  0;
}

float MFI_Ema(inout iMFI mfi)
{
    mfi.sMfi = mfi.sMfi +  mfi._ema*(mfi.Mfi - mfi.sMfi);
    return mfi.sMfi;
}

float MFI_Calc(inout iMFI mfi)
{

       if(IDX == 0){
            mfi._Pre =  rates[IDX].tval;
            mfi.Nmf  =  mfi.Pmf  = 0;
            mfi.Mfi  =  50;mfi.sMfi = mfi.Mfi;

      }else{

            float  _Curr = 0.;

            _Curr   =  rates[SIDX].tval;

           if(mfi.roll<IDX){
                 mfi.Pmf -= mfi.PMF[mfi.rid];mfi.Nmf -=  mfi.NMF[mfi.rid];
           }

            mfi.NMF[mfi.rid] = 0.;mfi.PMF[mfi.rid] = 0.;
            if(_Curr > mfi._Pre){ mfi.PMF[mfi.rid]  = _Curr;}
            if(_Curr < mfi._Pre){ mfi.NMF[mfi.rid]  = _Curr;}
            mfi.Pmf  +=  mfi.PMF[mfi.rid];mfi.Nmf +=  mfi.NMF[mfi.rid];
            mfi._Pre  = _Curr;

            if(mfi.Nmf != 0.0)mfi.Mfi=100.0-100.0/(1 + mfi.Pmf/mfi.Nmf);
            else          mfi.Mfi=100.0;
            mfi.rid =  (mfi.rid + 1)%mfi.roll;
            MFI_Ema(mfi);

      }

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
void SetMFICROS(inout MFI_Cros mfic){


             mfic.mfi[1]._ema = mfic.mfi[0]._ema  = 2./(1.+ float(PMFI_EMA));

             MFI_Set(mfic.mfi[0],PMFI_ROLL);
             MFI_Set(mfic.mfi[1],PMFI_ROLL + PMFI_DROLL);

             MFI_Calc(mfic.mfi[0]);
             MFI_Calc(mfic.mfi[1]);

             mfic._Pre[0] =  mfic.mfi[0].sMfi;
             mfic._Pre[1] =  mfic.mfi[1].sMfi;
             mfic._diff   =  mfic._Pre[1] - mfic._Pre[0];



}

void Calc_MFICROS(inout MFI_Cros mfic){

             float _Curr[2];
             float diff;
             MFI_Calc(mfic.mfi[0]);
             MFI_Calc(mfic.mfi[1]);

             _Curr[0] =  mfic.mfi[0].sMfi;
             _Curr[1] =  mfic.mfi[1].sMfi;


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

