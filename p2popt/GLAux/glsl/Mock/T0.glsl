struct Particle{
    vec4 pos;
};

layout(std430, binding=7) buffer particles{
    Particle p[];
};

uniform float time;
uniform uint max_num;

layout(local_size_x = 128, local_size_y = 1, local_size_z = 1) in;

#define PI 3.14159265359
#define PI2 ( PI * 2.0 )

vec2 rotate( in vec2 p, in float t )
{
  return p * cos( -t ) + vec2( p.y, -p.x ) * sin( -t );
}


float hash(float n)
{
  return fract(sin(n)*753.5453123);
}

void main(){
  uint id = gl_GlobalInvocationID.x;
  float theta = hash(float(id)*0.3123887) * PI2 + time;
  p[id].pos.x = cos(theta)+1.5;
  p[id].pos.y = sin(theta)*1.8;
  p[id].pos.z = 0.0;
  p[id].pos.w = 1.0;
  p[id].pos.xz = rotate(p[id].pos.xz, hash(float(id)*0.5123)*PI2);
}


