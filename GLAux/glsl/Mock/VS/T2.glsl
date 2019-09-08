#include <sRates.glsl>
#include <Mock1/parameter_vf.glsl>
#include <Visual/mock2_buffer.glsl>
uniform int   TYPE;
uniform float Zoom;
uniform vec2   res;
uniform int   SEP;
uniform int   FULL;
uniform int   Eofs;

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
	vec3 color;
} O;


#define POSITION		0
layout(location = POSITION) in   vec2 pos;

void main() {

    vec2 scale = vec2(1.2,-0.05);
    vec2 sw_sc = vec2(2.,2.);


    O.scale = scale;
    O.TYPE  = TYPE;
    O.No    = 0;

    if(TYPE == 0 || TYPE ==1){
        O.uv        = pos * 0.5f + 0.5f;
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
            idx  = dprop[SEP].entry[Eofs + id];O.color = vec3(0.2,0.4,0.9);gl_PointSize = 15.;O.TYPE = 15;
            y    = _rates[idx].close;
            idx  = idx - dprop[SEP].stid;
        }
        if(TYPE == 16){
            idx  = dprop[SEP].exit[Eofs + id];O.color = vec3(0.9,0.4,0.2);O.TYPE = 15;gl_PointSize = 15.;
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

       /*
        }else if(TYPE == 3 || TYPE == 4){

             idx  = id + vid;
             x  = float(idx)/(dprop[SEP].rx[1] - dprop[SEP].rx[0]);
             if(PARATH == -1){
                if(TYPE == 3)y  = rates[dprop[SEP].stid + idx].mu[SEP] - dprop[SEP].std;
                if(TYPE == 4)y  = rates[dprop[SEP].stid + idx].mu[SEP] + dprop[SEP].std;
             }else{
                if(TYPE == 3)y  = rates[dprop[SEP].stid + idx].mu[SEP];
                if(TYPE == 4)y  = rates[dprop[SEP].stid + idx].mu2[SEP];
             }

             if(TYPE == 3)O.color = vec3(0.2, 0.35, 0.8);
             if(TYPE == 4)O.color = vec3(0.8, 0.65, 0.5);

             y  = (y -  dprop[SEP].ry[0])/(dprop[SEP].ry[1] - dprop[SEP].ry[0]);

        }else if(TYPE == 5 || TYPE == 6 || TYPE==17 || TYPE == 18){

             idx  = id + vid;
             if(TYPE == 17){idx = dprop[SEP].entry[id];O.color = vec3(0.2,0.4,0.7);gl_PointSize = 15.;O.TYPE = 15;}
             if(TYPE == 18){idx = dprop[SEP].exit[id];O.color = vec3(0.7,0.4,0.2);O.TYPE = 15;gl_PointSize = 15.;}


             x  = float(idx)/(dprop[SEP].rx[1] - dprop[SEP].rx[0]);
             if(TYPE == 5 || O.TYPE == 15){y  = rates[dprop[SEP].stid + idx].mfi[SEP];if(TYPE==5)O.color = vec3(0.2,0.7,0.5);}
             if(TYPE == 6){y  = rates[dprop[SEP].stid + idx].mfi2[SEP];O.color = vec3(0.64,0.2,0.48);}



             y  = y/100.;

        }else if(TYPE ==  7|| TYPE==19 || TYPE == 20){

             idx  = id + vid;
             if(TYPE == 19){idx = dprop[SEP].entry[id];O.color = vec3(0.2,0.4,0.7);gl_PointSize = 15.;O.TYPE = 15;}
             if(TYPE == 20){idx = dprop[SEP].exit[id];O.color = vec3(0.7,0.4,0.2);O.TYPE = 15;gl_PointSize = 15.;}


             x  = float(idx)/(dprop[SEP].rx[1] - dprop[SEP].rx[0]);
             y  = rates[dprop[SEP].stid + idx].asset[SEP];
             if(TYPE==7)O.color = vec3(0.2,0.7,0.5);
             y  = (y -  dprop[SEP].ry[0])/(dprop[SEP].ry[1] - dprop[SEP].ry[0]);

        }else if(TYPE ==  30){

             idx  = id + vid;

             x  = float(idx)/(dprop[SEP].rx[1] - dprop[SEP].rx[0]);
             int bbr = dprop[SEP].stid;
             if(bbr==0){
                y  = asset[PARATH].range[asid(SEP,idx)];
             }else if(bbr==1){
                y  = asset[PARATH].bull[asid(SEP,idx)];
             }else{
                y  = asset[PARATH].bear[asid(SEP,idx)];
             }
             float PI =  3.14159265358979323846264;
             O.color = vec3(0.2,0.2,0.7*abs(sin(PI*float(PARATH)/192.)));
             y  = (y -  dprop[SEP].ry[0])/(dprop[SEP].ry[1] - dprop[SEP].ry[0]);
        }
        */


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

             if(SEP ==0)O.color = vec3(0.6,0.4,0.2);
             if(SEP ==1)O.color = vec3(0.2,0.4,0.6);
             if(SEP ==2)O.color = vec3(0.2,0.6,0.4);
             if(SEP ==3)O.color = vec3(0.4,0.4,0.4);

         }

            gl_Position = vec4(pos, 0., 1.0);

	}

}
