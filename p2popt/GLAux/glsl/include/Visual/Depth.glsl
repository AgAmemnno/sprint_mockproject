#define DEPTH_SIZE 512
struct sDepth
{
	float c;
};

layout( std430, binding = 6 ) buffer Depth{
	sDepth  dep[];
};

