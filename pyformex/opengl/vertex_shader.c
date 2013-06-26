/* $Id$ */
//
//  This file is part of pyFormex
//  pyFormex is a tool for generating, manipulating and transforming 3D
//  geometrical models by sequences of mathematical operations.
//  Home page: http://pyformex.org
//  Project page:  http://savannah.nongnu.org/projects/pyformex/
//  Copyright 2004-2012 (C) Benedict Verhegghe (benedict.verhegghe@ugent.be)
//  Distributed under the GNU General Public License version 3 or later.
//
//  This program is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see http://www.gnu.org/licenses/.
//

/* Vertex shader

If you add a uniform value to the shader, you should also add it
in shader.py, in order to allow setting the uniform value.
 */

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
uniform bool highlight;

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
  if (highlight) {
    // Highlight color, currently hardwirded yellow
    fragmentColor = vec3(1.,1.,0.);
  } else if (colormode == 1) {
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
    fTransformedVertexNormal = mat3(modelview[0].xyz,modelview[1].xyz,modelview[2].xyz) * fvertexNormal;

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
