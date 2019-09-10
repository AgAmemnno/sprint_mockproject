//PARAMETERS

float PMFI_TH     = 100;
int   PMFI_ROLL   = 26;
int   PMFI_DROLL  = 12;
float PMFI_EMA    = 12;


float PAMA_FSSC    = 100;
int   PAMA_AMA     = 12;
int   PAMA_EMA1    = 12;
int   PAMA_EMA2    = 26;



float PAMA_BANDTH  = 0.15;


//Const
#define SHXTH   32
#define SHYTH   1
#define SHZTH   1

#define SHRTH   2048
#define TOTAL   31540

//Global Variable
int  IDX;
int SIDX;
uvec3 WG;
//Shared Variable
struct sVal
{
   float   tval;
   float   open;
};

shared sVal rates[SHRTH];
