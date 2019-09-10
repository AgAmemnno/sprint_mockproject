#define  SEPARATE   4
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


#define  DEALTH    200
#define  ASSETTH    300
#define  BATCHTH   10

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