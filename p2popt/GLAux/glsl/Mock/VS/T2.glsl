#include <sRates.glsl>
#include <Mock1/parameter_vf.glsl>
#include <Visual/mock2_buffer.glsl>
#include <util/hsl.glsl>
#include <Mock1/inout.glsl>

uniform int   TYPE;
uniform float Zoom;
uniform vec2   res;
uniform int   SEP;
uniform int   FULL;
uniform int   Eofs;
uniform vec3  Seed;

uniform vec2 ioNorm;
uniform vec4  xNorm;

out gl_PerVertex
{
	vec4  gl_Position;
	float gl_PointSize;
};

out block
{
    vec2 scale;
    int TYPE;
    int No;
	vec2 uv;
	vec4 color;
} O;


#define POSITION		0
layout(location = POSITION) in   vec2 pos;

void main() {

    vec2 scale = vec2(1.2,-0.05);
    vec2 sw_sc = vec2(2.,2.);

    O.scale = scale;
    O.TYPE  = TYPE;
    O.No    = 0;

    if(TYPE == 40){

        int  id  = gl_InstanceID;
        #define NormZ(p)  (p-ioNorm.x)/(ioNorm.y-ioNorm.x)
        #define NormX(p)  (p-xNorm.x)/(xNorm.y-xNorm.x)
        #define NormY(p)  (p-xNorm.z)/(xNorm.w-xNorm.z)

        #define Max  35.
	    gl_PointSize  =  Max*NormZ(io[id].y);

	    int               idx;
        float              x,y;
     //174  float x;
        x    =  NormX(io[id].x[SEP*2]);
        y    =  NormY(io[id].x[SEP*2+1]);

        vec2 pos = vec2(x,y);

        //pos.y = (pos.y - scale.y)/scale.x;
        pos   = 2.*pos - 1.;

        pos   = pos +  gl_PointSize*vec2(-1./res.x,1./res.y)/2.;

        O.color = (io[id].sel ==1)?vec4(0.3,0.3,0.3,1.):vec4(1);

        gl_Position = vec4(pos, 0., 1.0);

    }
    else if(TYPE == 0 || TYPE ==1 || TYPE == 41){
        O.uv        = pos * 0.5f + 0.5f;
        O.color     = vec4(vec3(1.0),0.5);
        gl_Position = vec4(pos, 0., 1.0);

    }else if(TYPE == 10){

	      int  id  = gl_InstanceID;
	      int  vid = gl_VertexID;
	      vec2 pos = vec2(0,0);

	      if(id == 0){
	         pos.x =  2*vid - 1;pos.y = 0.;
	      }else{
	         pos.y =  2*vid - 1;
	         pos.x =  2./sw_sc.x*float(id) - 1.;
	      }

	      gl_Position = vec4(pos, 0., 1.0);

	}else if(TYPE >= 2){


	    int  id  = gl_InstanceID;
	    int  vid = gl_VertexID;
	    #define tg(i) int(mod(i+1,2))

	    gl_PointSize = 10.;

	    int               idx;
	    int               idx2;
        float           x,x2,y;


        if(TYPE == 2){
             idx  = id;gl_PointSize = 9.;
             y    = _rates[dprop[SEP].stid + idx].close;
             O.TYPE = 2;
        }

        if(TYPE == 3){
            idx = id + vid;
            y    = vis[dprop[SEP].stid + idx].mu[SEP];
            O.TYPE  = 10;
        }
        if(TYPE == 4){
            idx = id + vid;
            y    = vis[dprop[SEP].stid + idx].mu2[SEP];
             O.TYPE  = 10;
        }

        if(TYPE == 15){
            idx  = dprop[SEP].entry[Eofs + id];O.color = vec4(hsl2rgb(vec3(Seed.x,0.35,0.4)),0.3);gl_PointSize = 20.;O.TYPE = 15;
            y    = _rates[idx].close;
            idx  = idx - dprop[SEP].stid;
        }
        if(TYPE == 16){
            idx  = dprop[SEP].exit[Eofs + id];O.color = vec4(hsl2rgb( vec3(Seed.y,0.35,0.4)),0.3);O.TYPE = 15;gl_PointSize = 20.;
            y    = _rates[idx].close;
            idx  = idx - dprop[SEP].stid;
        }


        if(TYPE == 20){
            gl_PointSize = 8.;
            #define  batch  SHXTH*BATCHTH
            #define  ASid(i,x) (batch*i + x)
            idx = id + vid;
            y      = asset[ASid(SEP,Eofs)].y[idx+1];
            idx    = int(asset[ASid(SEP,Eofs)].x[idx+1]);
            O.TYPE = 1;
        }

         x  = float(idx)/(dprop[SEP].rx[1] - dprop[SEP].rx[0]);
         y  = (y -  dprop[SEP].ry[0])/(dprop[SEP].ry[1] - dprop[SEP].ry[0]);



            vec2 pos = vec2(x,y);
            float z = 1./(1. - Zoom);
            pos.x  = pos.x*z - (z-1.);
            if(pos.x < 0.)return;
            if(pos.x > 1.)return;


            pos.y = (pos.y - scale.y)/scale.x;
            pos   = 2.*pos - 1.;


         if(FULL == 0){
             vec2 sw_sf = 1./sw_sc;

             pos /= sw_sc;


             float sf_x = mod(SEP, sw_sc.x);
             vec2 sf = vec2(((sf_x == 0)?(mod(SEP/sw_sc.y, sw_sc.x)):(mod((SEP-1)/sw_sc.y, sw_sc.x))), -2*sf_x + 1);
             pos.x +=  2.*sw_sf.x*sf.x + sw_sf.x - 1.;
             pos.y +=  sw_sf.y*sf.y;
         }

         if(O.TYPE == 2 || O.TYPE == 15){
                pos   = pos +  gl_PointSize*vec2(-1./res.x,1./res.y)/2.;
         }
         if(O.TYPE <=2){
             float alpha = 0.6;
             #define H(h)  (Seed.x + h)
             #define L(l) ((l)*0.1 + 0.3)
             if(SEP ==0)O.color = vec4(hsl2rgb(vec3(H(0) ,0.05,L(Seed.y))), alpha);
             if(SEP ==1)O.color = vec4(hsl2rgb(vec3(H(0.1) ,0.05,L(Seed.y))), alpha);
             if(SEP ==2)O.color = vec4(hsl2rgb(vec3(H(0.2) ,0.05,L(Seed.y))), alpha);
             if(SEP ==3)O.color = vec4(hsl2rgb(vec3(H(0.3) ,0.05,L(Seed.y))), alpha);
         }

            gl_Position = vec4(pos, 0., 1.0);

	}

}
