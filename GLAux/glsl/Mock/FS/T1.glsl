in block
{
    vec2 scale;
    flat int   TYPE;
    flat int   No;
	vec2 uv;
	vec4 color;

} In;



#define FRAG_COLOR		0
layout(location = FRAG_COLOR, index = 0) out vec4 color;


float ncolor1D(float v,float g){
	 g = length(vec2(g ,1.));
	 float eps = 0.01;
	 return smoothstep(0.,5.*eps,v/g);
}

bool triangle(vec2 p){
     float scale = 0.5;
     if(p.x < 0.5){if((2.*(p.x)*scale - p.y) < 0)return true;}
     else if( p.y - (-2.*(p.x - 1.)*scale) > 0)return true;
     return false;
}



void main()
{


     if(In.TYPE == 10){
         vec3 col = vec3(0.1,0.1,0.1);
         color = vec4(col,0.6);
     }else{

       if(In.TYPE ==2){
         vec2 uv = 2.0 * gl_PointCoord - 1.0;
         float d = length(uv - 0.5);
		 float e = 0.1;
		 if (d > 0.5)discard;
       }else if(In.TYPE == 15){

           vec2 uv = gl_PointCoord;
           if (triangle(uv))discard;
       }
         color = In.color;
	 }

}