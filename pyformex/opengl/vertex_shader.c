#ifdef GL_ES
precision mediump float;
#endif

attribute vec3 vertexPosition;
attribute vec3 vertexNormal;
attribute vec3 vertexColor;
attribute vec2 vertexTexturePos;
attribute float vertexScalar;

uniform mat4 modelview;     // xtk: view
uniform mat4 projection;    // xtk: perspective
uniform int colormode;      // xtk useObjectColor;

uniform mat4 objectTransform;
uniform bool useScalars;
uniform bool scalarsReplaceMode;
uniform float scalarsMin;
uniform float scalarsMax;
uniform vec3 scalarsMinColor;
uniform vec3 scalarsMaxColor;
uniform float scalarsMinThreshold;
uniform float scalarsMaxThreshold;
uniform int scalarsInterpolation;
uniform vec3 objectColor;

uniform float pointsize;

uniform bool builtin;
uniform bool lighting;
uniform float ambient;
uniform float diffuse;
uniform float specular;    // Intensity of reflection
uniform float shininess;   // Surface shininess
uniform vec3 speccolor;    // Color of reflected light
uniform float alpha;
uniform vec3 light; // Currently 1 light: need multiple


varying float fDiscardNow;
varying vec4 fvertexPosition;
varying vec3 fvertexNormal;
varying vec4 fragColor;        // Final fragment color, including opacity
varying vec3 fragmentColor;
varying vec2 fragmentTexturePos;
varying vec3 fTransformedVertexNormal;


void main()
{
  if (colormode == 1) {
    // Single color
    fragmentColor = objectColor;
  } else if (colormode == 3) {
    // Vertex color
    if (builtin) {
      fragmentColor = gl_Color;
    } else {
      fragmentColor = vertexColor;
    }
  } else {
    // Default black
    fragmentColor = vec3(0.,0.,0.);
  }

  // Add in lighting
  if (lighting) {
    if (builtin) {
      fvertexNormal = gl_Normal;
    } else {
      fvertexNormal = vertexNormal;
    }
    fTransformedVertexNormal = mat3(modelview[0].xyz,modelview[1].xyz,modelview[2].xyz) * vertexNormal;

    vec3 nNormal = normalize(fTransformedVertexNormal);
    vec3 nlight = normalize(light);
    //vec3 eyeDirection = normalize(-vertexPosition);
    vec3 eyeDirection = normalize(vec3(0.,0.,1.));
    vec3 reflectionDirection = reflect(-nlight, nNormal);
    float nspecular = specular*pow(max(dot(reflectionDirection,eyeDirection), 0.0), shininess);
    float ndiffuse = diffuse * max(dot(nNormal,nlight),0.0);

    // total color is sum of ambient, diffuse and specular
    vec3 fcolor = fragmentColor;
    fragmentColor = vec3(fcolor * ambient +
			 fcolor * ndiffuse +
			 speccolor * nspecular);
  }

  // Add in opacity
  fragColor = vec4(fragmentColor,alpha);

  // setup vertex Point Size
  gl_PointSize = pointsize;
  // Transforming The Vertex
  if (builtin) {
    fvertexPosition = gl_Vertex;
  } else {
    fvertexPosition = vec4(vertexPosition,1.0);
  }
  gl_Position = projection * modelview * fvertexPosition;
}