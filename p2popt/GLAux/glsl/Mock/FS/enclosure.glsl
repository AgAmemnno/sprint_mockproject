#include <Visual/Depth.glsl>
// by nikos papadopoulos, 4rknova / 2013
// Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

precision highp float;
uniform float iTime;
uniform vec3  iMouse;
uniform vec2  iResolution;
uniform vec2  StPos;
uniform float Radius;
uniform float Visc;
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

float dCassinoid(vec2 p, vec2 a, vec2 b){
 return length(p-a)*length(p-b);}

float ssf(float a,float d){return smoothstep(-a,a,d);}

float waveTri(float x,float d){
    d*=2.;
 return min(mod(x,d),mod(-x,d));}

float WavSaw(float x,float w){
 return abs((x)/w);}//waveSaw saw-function

uniform int DUMP = 1;

vec4 enclosure(){
            uint did;
            if(DUMP==1)did = uint(floor(In.uv.y*DEPTH_SIZE) *DEPTH_SIZE + floor(In.uv.x*DEPTH_SIZE));

            vec2 p = 2.*In.uv -1;
            vec2 res=iResolution.xy;
            //vec2 p=uv/min(res.x,res.y);

            float dx=res.x/res.y;

            //vec2 mr= mouse.xy/res.xy;
            vec2 mr= iMouse.xy/res.xy;
            mr = 2.*vec2(mr.x,1-mr.y)-1;
            if(iMouse.z == 1){
                    p-= mr;
                    mr = vec2(0);
            }else{
                    p  -= StPos;
                    mr -= StPos;
            }

            //if(length(In.uv-mouse) < 0.1)color = vec4(1.);
            //else color = vec4(0,0,0,1.);


            vec3 col = vec3(0);
            vec2 a=vec2(.0);
            vec2 b=mr;
            float d=dCassinoid(p,a,b);

            float lq=length(a-b);lq*=lq;
            float dist=lq*(Visc);
            float eps=Radius;
            float e=1.;
            if(d<dist+eps){
                 e=-.125;
                  if(DUMP==1)dep[did].c = 1;
            }else if(DUMP==1)dep[did].c = 0;

            if(d<dist+eps && d>dist-eps)e*=4.;//optional line
            d=waveTri(d*15.,.6);
            //   d=WavSaw(d*15.,.6);
            d=1.-ssf(.25,d*e);

    return vec4(vec3(d) + col,1);

}


const  float radius = 2.0;

float distanceFromEdge(vec3 p)			// Circles are defined as everything a uniform distance from the center
{										// In this case we are looking for how far the current candidate guess
    return length(p) - radius;			//   is from the radius of the circle
}

float trace(vec3 origin, vec3 ray)				// You -could- do this recursively, but itterative is simpler and safer
{
    float t = 0.0;
    for (int i = 0; i < 64; ++i)				// We know what direction the pixel is, and we want to know
    {											//   the amount t must be to get to it
        vec3 p = origin + ray * t;				// Pick a point along the ray r at a distance t from the origin
        float distance = distanceFromEdge(p);   // Let d be the new distance from the circle edge, negative or positive
        t += distance * 0.5;					// Now change the distance factor t by half the distance we currently are from edge
    }
    return t;
}

vec4 circle(vec2 uv)
{

   // uv.x *= iResolution.x / iResolution.y;// Correct for aspect ratio; rescale texcoords horizontally based on it

    vec3 ray    = normalize(vec3(uv, 1.0));// Direction to the pixel (unit vector, no magnitude)
    vec3 origin = vec3(0.0, 0.0, -3);// Camera origin at 0,0,-3

    float t     = trace(origin, ray);

    return vec4(1.0/t);
}

void main(){

     if(In.TYPE == 1){
         color = enclosure();
     }else if(In.TYPE == 40){
         vec2 uv = 2.0 * gl_PointCoord - 1.0;
         color = circle(uv)*In.color;
     }else if(In.TYPE == 41){
         uint did = uint(floor(In.uv.y*DEPTH_SIZE) *DEPTH_SIZE + floor(In.uv.x*DEPTH_SIZE));
         color = vec4(vec3(dep[did]),1);
     }
}


