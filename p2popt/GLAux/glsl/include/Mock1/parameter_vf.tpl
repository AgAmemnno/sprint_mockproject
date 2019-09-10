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
#define SHXTH   {{CONST.SHXTH|default("256", True)}}
#define SHYTH   {{CONST.SHYTH|default("1", True)}}
#define SHZTH   {{CONST.SHZTH|default("1", True)}}

#define SHRTH   {{CONST.SHRTH|default("2048", True)}}
#define TOTAL   {{CONST.TOTAL|default("20000", True)}}

//Global Variable
int  IDX;
int SIDX;
uvec3 WG;

