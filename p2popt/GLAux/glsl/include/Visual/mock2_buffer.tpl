#define  SEPARATE   {{CONST.SEPARATE|default("4", True)}}
struct sVisual
{
	float   mu[SEPARATE];
	float   mu2[SEPARATE];
	float   mfi[SEPARATE];
	float   mfi2[SEPARATE];
	float   asset[SEPARATE];
};

layout( std430, binding = 0 ) buffer Visual{
	sVisual  vis[];
};


#define  DEALTH    {{CONST.DEALTH|default("200", True)}}
#define  ASSETTH    {{CONST.ASSETTH|default("300", True)}}
#define  BATCHTH   {{CONST.BATCHTH|default("10", True)}}

struct sAsset
{
	float   x[ASSETTH];
	float   y[ASSETTH];
};

struct sDrawProp
{
     int    stid;
     float   std;
     float ry[2];
     float rx[2];
     int   entry[200];
     int   exit[200];

};

layout( std430, binding = 2 ) buffer DrawProp{
	sDrawProp dprop[];
};



layout( std430, binding = 4 ) buffer Asset{
	sAsset  asset[];
};
