struct sACNT
{
	uint   i[SHXTH];
};

layout( std430, binding = 1 ) buffer ACNT{
	sACNT ac[];
};