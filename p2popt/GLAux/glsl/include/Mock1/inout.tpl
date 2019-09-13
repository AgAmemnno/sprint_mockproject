#define VTH {{CONST.VTH|default("8", True)}}  //variable length
struct sIO
{
	float   x[VTH];
    float   y;
    float   sel;
};

layout( std430, binding = 5 ) buffer IO{
	sIO io[];
};