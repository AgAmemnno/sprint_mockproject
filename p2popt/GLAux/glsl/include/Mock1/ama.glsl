//Global
//    int IDX
//Shared Data
//    struct  rates


float SQ2 = sqrt(2.);
struct AMA{


       float close;
       float S1[155],S2[155];
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



};

void AMA_Calc(inout AMA ama){

    if(IDX< ama.ama){

           ama.S1[IDX] = rates[IDX].tval;
           ama.s1 +=  ama.S1[IDX];
           if(IDX!=0)ama.S2[IDX] = ama.S1[IDX]- ama.S1[IDX-1];
           if(IDX!=0)ama.s2   += ama.S2[IDX];

           ama.mu2 = ama.mu  = ama.s1 / float(IDX+ 1);
           ama.rid = IDX;

    }else{

          float rsi,FSSC;
          int   irsi;

           ama.rid     =  (ama.rid + 1)%int(ama.ama);

           ama.s1         -=  ama.S1[ama.rid];
           ama.S1[ama.rid] =   rates[SIDX].tval;
           ama.s1         +=  ama.S1[ama.rid];


           ama.s2              -=  ama.S2[ama.rid];
           ama.S2[ama.rid]      =  ama.S1[ama.rid] - ama.S1[(ama.rid-1+ama.ama)%ama.ama];
           ama.s2              +=  ama.S2[ama.rid];


           float _dmu;
           _dmu      =  ama.s2;
           if(_dmu == 0)FSSC = 0.99;
           else{
               irsi   =  (ama.rid + 1)%ama.ama;
               rsi    =  abs(ama.S1[ama.rid] - ama.S1[irsi])/_dmu;
	           FSSC   =  float(pow((rsi * ama.ema1 + ama.ema2), float(2.)));
		       FSSC   = (log(FSSC + 1)*SQ2);
		       if(FSSC > 0.99)FSSC = 0.99;
		   }

		     ama.dir_mu  = FSSC * (ama.S1[ama.rid] - ama.mu);
		     ama.mu      += ama.dir_mu;
             _dmu       = ama.s1/float(ama.ama);
             ama.dir_mu2 =  _dmu - ama.mu2;
		     ama.mu2     =  _dmu;
             //ama.mu     = ama.mu  + FSSC*(rates[SIDX].tval - ama.mu);
             //ama.mu     = ama.mu  + 2./(1. + 24.)*(rates[SIDX].open - ama.mu);
             //ama.mu2    = ama.mu2 + 2./(1. + 12.)*(rates[SIDX].open - ama.mu2);

      }


}

void AMA_Set(inout AMA ama)
{

      ama.ama  =  PAMA_AMA;
      ama.ema1 = 2./(1.+ float( PAMA_EMA1));
      ama.ema2 = 2./(1.+ float( PAMA_EMA2));
      ama.s1 = 0.;ama.s2 = 0.;

      ama.fssc      =   PAMA_FSSC;//FSSC/std;
      ama.S2[0] = 0.;
      AMA_Calc(ama);

}

