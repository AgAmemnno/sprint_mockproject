#define FRAG_COLOR		0

precision highp float;
precision highp int;

in block
{
    vec2 scale;
    flat int   TYPE;
    flat int   No;
	vec2 uv;
	vec3 color;

} In;



layout(location = FRAG_COLOR, index = 0) out vec4 Color;

float  Solve(float lam, float x,float lr) {
	return  (lam + lr*sqrt(lam*lam - 4.*x*lam)) / 2. / lam;
}

void main()
{

	float e = 4.0 / 1024.;
	float x = In.uv.x;
	float sc = -0.3;
	float y = (In.uv.y*sc + -(1.+ sc) );
	float lam = -4. / ((y >= -0.001) ? -0.001 : y);


	vec3 col = vec3(0.18);
	float f = 1.0;
    #define G 5
    #define N 128
	float X[2][N];
	X[0][0] = Solve(lam, 1.0,-1.);
	X[0][1] = Solve(lam, 1.0, 1.);
	int  pre  = 0, cur = 1;
	int  p     = 0;
	int  l      = 2;
	int  L     = 2;
	vec2  TRM = vec2(X[0][0], X[0][1]);

	float bg = 0.3;

	for (int i = 0; i < G; i++)
	{
		if (TRM.x <= x && x <= TRM.y)break;
		if (i == G - 1) { col = vec3(bg); break; }
		p = 2*p + ((TRM.x > x) ? 0 : 1);

		int cnt = 0;
		for (int j = 0; j < N; j++)
		{
			if (L == j)break;
			X[cur][cnt++]    = Solve(lam, X[pre][j],-1.);
		}
		int mid = cnt;
		cnt = 2 * cnt - 1;
		for (int j = 0; j < N; j++)
		{
			if (L == j)break;
			X[cur][cnt - j] = Solve(lam, X[pre][j], 1.);
		}

		TRM = vec2(X[cur][2*p], X[cur][2*p + 1]);

		pre = (pre== 0) ? 1 : 0;
		cur = (pre == 0) ? 1 : 0;
		l++; L *= 2;

	}


	Color = vec4(col, 1.0);


}
