#version 150
#extension GL_ARB_geometry_shader4 : enable

inout float radius;
layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;

// a passthrough geometry shader for color and position
void main()
{
  for(int i = 0; i < gl_VerticesIn; ++i)
  {
    // copy color
    gl_FrontColor = gl_FrontColorIn[i];
 
    // copy position
    gl_Position = gl_PositionIn[i];
 
    // done with the vertex
    EmitVertex();
  }
}
