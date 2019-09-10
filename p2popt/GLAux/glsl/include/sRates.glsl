struct sRates
{
    float  date;
    float  open;
    float  high;
    float   low;
	float close;
/*
	float   mu[PORT_NUM];
	float   mu2[PORT_NUM];
	float   mfi[PORT_NUM];
	float   mfi2[PORT_NUM];
	float   asset[PORT_NUM];
*/
};


layout( std430, binding = 3 ) buffer Rates{
	sRates _rates[];
};