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
