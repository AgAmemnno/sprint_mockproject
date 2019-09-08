#define VTH 8  //variable length
struct sIO
{
	float   x[VTH];
    float   y;
};

layout( std430, binding = 5 ) buffer IO{
	sIO io[];
};