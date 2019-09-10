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
