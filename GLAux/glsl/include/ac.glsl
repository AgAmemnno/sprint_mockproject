struct sACNT
{
	uint   i[1024];
};

layout( std430, binding = 1 ) buffer ACNT{
	sACNT ac[];
};