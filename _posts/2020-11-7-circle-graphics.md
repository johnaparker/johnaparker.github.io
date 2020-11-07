---
title: "Realtime visualization of a large number of circles using OpenGL"
excerpt: "When using Matplotlib, animations of a large number of circles becomes slow. Using OpenGL, over a million circles can be animated in realtime."
image_url: /assets/img/posts/circle_graphics/teaser.png

tags:
  - Graphics
  - Performance
  - Particles

github_url: https://github.com/johnaparker/blog/tree/master/circle_animation
---

## The need for faster rendering

Matplotlib is my goto software library for creating graphics, including animations.
Combining Matplotlib's patches library with its `FuncAnimation`, you can easily create animations with 2D objects that look good.
However, Matplotlib was not designed with performance in mind, most significantly in that it only utilizes the CPU in a single-threaded environment.
For more demanding animations, Matplotlib becomes unbearably slow.

Suppose we want an animation of 100,000 dynamic circles, and we want it to playback in real-time so that the user can explore by panning and zooming.
Matplotlib is no longer an option.
To get maximum performance, we will use OpenGL to animate the circles, which utilizes the GPU for all of the graphics.
Ultimately, with the correct optimizations, the OpenGL solution can be over 2,000 times faster than Matplotlib, making real-time visualization a reality.

## Visualizing the data

We will need datasets for the positions of _N_ particles.
Three datasets are obtained from a simulation of circular particles with hard collisions (granular materials); they can be downloaded in the [source code]({{ page.github_url }}).
A "small" dataset consists of 1,000 circles, the "medium" dataset consists of 10,000 circles, and the "large" dataset consists of 100,000 circles.
Below are videos of the dynamic animations that can be made using Matplotlib or OpenGL, but only the OpenGL solution is capable of realtime rendering.

**Small dataset ($$N = 1,000$$)**
<video width="100%" controls="controls" loop class="video" preload="metadata" playsinline src="/assets/img/posts/circle_graphics/small.mp4#t=0.01"></video>

**Medium dataset ($$N = 10,000$$)**
<video width="100%" controls="controls" loop class="video" preload="metadata" playsinline src="/assets/img/posts/circle_graphics/medium.mp4#t=0.01"></video>

**Large dataset ($$N = 100,000$$)**
<video width="100%" controls="controls" loop class="video" preload="metadata" playsinline src="/assets/img/posts/circle_graphics/large.mp4#t=0.01"></video>

## Animating circles with Matplotlib

### Simple method
In Matplotlib, animations are created using a list of `circle` patches and an update loop through `FuncAnimation`.
Given an array of the trajectories with shape $$(T, N, 2)$$, we can animate them in Matplotlib like so:
```python
def update(frame):
    for i, circle in enumerate(circles):
        circle.center = traj[frame,i]

    return circles

anim = FuncAnimation(fig, update, len(traj), interval=15)
```

### Using collections
The former method can be improved by using Matplotlib collections, which are designed to be more efficient when drawing a large number of the same objects.
We our required to create a special type of `PatchCollection` that can be animated, so we create an `UpdatablePatchCollection` class:
```python
class UpdatablePatchCollection(PatchCollection):
    def __init__(self, patches, *args, **kwargs):
        self.patches = patches
        PatchCollection.__init__(self, patches, *args, **kwargs)

    def get_paths(self):
        self.set_paths(self.patches)
        return self._paths

collection = UpdatablePatchCollection(circles)
plt.add_collection(collection)
```
The `get_paths` member is needed for the animation to update correctly.
A collection is then created and drawn to the figure.

The `update` function needs to be modified by calling `set_offsets` on the collections, and returning the collections instead of the circles:
```python
def update(frame):
    collection.set_offsets(traj[frame])
    for i, circle in enumerate(circles):
        circle.center = traj[frame,i]

    return collection,
```
Using collections provides a 2-3x performance increase over the simple method; not bad, but not nearly enough for real-time animations.

## Animating circles with OpenGL

Enter OpenGL.
There are a number of ways to write OpenGL from Python, such as using PyOpenGL or VisPy.
My preference is to write OpenGL from C++, and use `pybind11` to bind the C++ code to Python.
That way, any calculations that need to be done on the CPU side are very fast before drawing on the GPU.
Python can then make the user-side code very simple.
The [source code]({{ page.github_url }}) shows how all of this done.

To draw many circles, we have to be able to draw a single circle first.
We will consider two approaches: one that uses vertices to approximate the circle and one that uses fragments in the fragment shader.
Finally, when drawing many circles, we will make use of instanced drawing for additional performance.

### Vertex approach
In the vertex approach, we pass _N_ vertices to the vertex shader.
These vertices are all on a circle of radius $$1$$, as well as a vertex at the center of the circle to form the triangles to be drawn.
The fragment shader is trivial: it simply fills each fragment of the triangles with a solid color.
A schematic of what the vertex and fragment shader are doing:
<figure style="width: 100%" class="align-center">
  <img src="/assets/img/posts/circle_graphics/circle_vertex.svg" alt="">
</figure> 

Additionally, the vertex shader is responsible for scaling and translating the vertices so that the circle has the correct radius and position.
The GLSL code for the vertex shader is
```cpp
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 projection;
uniform mat4 transform;
uniform vec4 color;

out vec4 circleColor;

void main() {
    gl_Position = projection * transform * vec4(aPos, 1.0);
    circleColor = color;
}
```
The vertex positions are given by `aPos`.
The uniform data includes the `projection` matrix transform that depends on the users camera, the `transform` matrix that scales and translates the circle, and the `color` vector that defines its color.
As output, the vertex shader sends the color of the circle to the fragment shader.

The fragment shader simply returns the `circleColor` as the `FragColor`
```cpp
#version 330 core
in vec4 circleColor;
out vec4 FragColor;

void main() {
    FragColor = circleColor;
}
```

To actually draw the circle, we need to create the vertices of the circle and send them to the GPU.
We use Element Buffer Objects (EBO) to represent the triangles around the circle, which requires construction of `Nvertices` and corresponding `indices`
```cpp
float vertices[(Nvertices+1)*3];
unsigned int indices[Nvertices*3];

// crete vertices and indices
vertices[0] = vertices[1] = vertices[2] = 0; // origin
for (unsigned int i=0; i<Nvertices; i++) {
    float theta = 2*M_PI*(float)i/(float)(Nvertices);
    vertices[3*(i+1) + 0] = cos(theta);
    vertices[3*(i+1) + 1] = sin(theta);
    vertices[3*(i+1) + 2] = 0;

    indices[3*i + 0] = 0;
    indices[3*i + 1] = 1+i;
    indices[3*i + 2] = (1+i)%Nvertices + 1;
}

// create VAO, VBO, and EBO
glGenVertexArrays(1, &VAO);
glGenBuffers(1, &VBO);
glGenBuffers(1, &EBO);

// send data to GPU
glBindVertexArray(VAO);
glBindBuffer(GL_ARRAY_BUFFER, VBO);
glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
```
Once this is done, we can use the `VAO` to draw as many circles as we want.
Before we draw each circle, we have to set the `transform` and `circleColor` uniform variables
```cpp
for (int i = 0; i < Nparticles; i++) {
    // create the transform matrix
    glm::mat4 transform = glm::mat4(1.0f);
    transform = glm::translate(transform, glm::vec3(pos_data(current_frame,i,0), pos_data(current_frame,i,1), 0.0f));
    transform = glm::scale(transform, glm::vec3(radii_data(i), radii_data(i), 1.0f));
    glUniformMatrix4fv(glGetUniformLocation(shader.ID, "transform"), 1, GL_FALSE, glm::value_ptr(transform));

    // create the color vector
    int idx = i % Ncolors;
    glUniform4f(glGetUniformLocation(shader.ID, "color"), color_data(idx,0), color_data(idx,1), color_data(idx,2), color_data(idx,3));

    // draw the triangle
    glDrawElements(GL_TRIANGLES, 3*Nvertices, GL_UNSIGNED_INT, 0);
}
```
Here, the transform matrix is constructed for each particle by combing a scale with a translate.
The scale sets the radius of the circle, and the translate sets its position.
The color vector is set from the color input in a cyclic manner.
The circle, composed of `3*Nvertices` vertices, is then drawn using `glDrawElements`.

### Fragment approach

The main issue with the vertex approach is that we really need to take `Nvertices` to infinity for the circle to be "perfect".
By perfect, I mean that the circle is drawn as correctly as it can be for the resolution of the monitor.
If you zoom in on a vertex, you don't want to see a pointed corner, but rather a smooth surface.
This can be achieved by using the fragment shader to draw the circle instead of relying entirely on the vertex shader.
The idea is to use vertices that define a square, and only keep the fragments (pixels) that fall inside the circle that the square circumscribes.
Here's a schematic of the fragment shader approach:
<figure style="width: 100%" class="align-center">
  <img src="/assets/img/posts/circle_graphics/circle_fragment.svg" alt="">
</figure> 

To accomplish this, we use the same vertex shader as before, and we add as output the `pos` that is accepted in the fragment shader.
The fragment shader then checks if the `pos` is inside or outside the circle
```cpp
#version 330 core

in vec2 pos;
in vec4 circleColor;
out vec4 FragColor;

void main() {
    float rsq = dot(pos, pos);
    if (rsq > 1)
        discard;
    FragColor = circleColor;
}
```
If outside, the fragment shader discards the fragment, otherwise it colors it.
Doing it this way, we obtain a circle drawn as accurately as possible for the monitor's pixel density.

The vertices and EBO also have to be created differently.
Here we just need two triangles

```cpp
// a square with side lengths 2
float vertices[] = {
     1.0f,  1.0f, 0.0f,
     1.0f, -1.0f, 0.0f,
    -1.0f, -1.0f, 0.0f,
    -1.0f,  1.0f, 0.0f,
};
unsigned int indices[] = {
    0, 1, 3,
    1, 2, 3
};

// create VAO, VBO, and EBO
glGenVertexArrays(1, &VAO);
glGenBuffers(1, &VBO);
glGenBuffers(1, &EBO);

// send data to GPU
glBindVertexArray(VAO);
glBindBuffer(GL_ARRAY_BUFFER, VBO);
glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
```
Thus, the vertex shader has now less work to do, and the fragment shader has more work to do.

### Instanced drawing
In both of the previous examples, each circle is drawn using `glDrawElements` once per circle.
This is not good, since if want to render a large number of circles the CPU is sending data to the GPU in small batches many times over per frame.
Preferably, we want to send all of the necessary data to the GPU at once and issue a single draw commmand.
This can be accomplished using _instanced drawing_.

The vertex shader has to be modified to accept the `transform` and `color` as vertex data instead of uniform data 
```cpp
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in mat4 transform;
layout (location = 5) in vec4 color;

uniform mat4 projection;
out vec4 circleColor;
out vec2 pos;

void main() {
    gl_Position = projection * transform * vec4(aPos, 1.0);
    circleColor = color;
    pos = aPos.xy;
}
```
Note that each `location` occupies 4 `floats`, so the `4x4` transform matrix occupies locations 1 though 4.
The `projection` matrix remains a uniform since there is only one for the entire scene.

The C++ code now looks like this
```cpp
// set instanced data for all particles
for (int i = 0; i < Nparticles; i++) {
    glm::mat4 transform = glm::mat4(1.0f);
    transform = glm::translate(transform, glm::vec3(pos_data(current_frame,i,0), pos_data(current_frame,i,1), 0.0f));
    transform = glm::scale(transform, glm::vec3(radii_data(i), radii_data(i), 1.0f));

    circleTransforms[i] = transform;
    int idx = i % Ncolors;
    circleColors[i] = glm::vec4(color_data(idx,0), color_data(idx,1), color_data(idx,2), color_data(idx,3));
}

// copy instanced data to GPU
glBindBuffer(GL_ARRAY_BUFFER, transformVBO);
glBufferData(GL_ARRAY_BUFFER, Nparticles * sizeof(glm::mat4), &circleTransforms[0], GL_DYNAMIC_DRAW);
glBindBuffer(GL_ARRAY_BUFFER, colorVBO);
glBufferData(GL_ARRAY_BUFFER, Nparticles * sizeof(glm::vec4), &circleColors[0], GL_DYNAMIC_DRAW);

// draw circles
glBindVertexArray(VAO);
glDrawElementsInstanced(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0, Nparticles);
```
All of the transform matrices and circle colors are generated before any draw commands take place.
These arrays are copied to the GPU in one go.
Then, the circles are drawn with `glDrawElementsInstanced`.

## Performance results
The [source code]({{ page.github_url }}) implements all 6 methods mentioned above: 2 matplotlib approaches, and 4 OpenGL approaches using the vertex or fragment approach and instanced and non-instanced drawing.
Running on my machine, I tabulate the average time interval between frames for each of the 6 methods on the small, medium, and large datasets:
<table>
<caption>Runtime performance of circle animations using Matplotlib and OpenGL. Performance is measured by average time between frames (lower is better). Numbers obtained with AMD Ryzen 2700X and NVIDIA RTX 2070 Super. </caption>
<colgroup>
<col width="auto" />
<col width="auto" />
<col width="auto" />
<col width="auto" />
</colgroup>
<thead>
<tr class="header">
<th style="background-color: rgba(0,0,0,0)"></th>
<th>Small dataset<br>(N = 1,000)</th>
<th>Medium dataset<br>(N = 10,000)</th>
<th>Large dataset<br>(N = 100,000)</th>
</tr>
</thead>
<tbody>
<tr>
<th scope="row">Matplotlib (simple)</th>
<td>118 ms</td>
<td>1,000 ms</td>
<td>10,300 ms</td>
</tr>
<tr>
<th scope="row">Matplotlib (collection)</th>
<td>56 ms</td>
<td>420 ms</td>
<td>4,100 ms</td>
</tr>
<tr>
<th scope="row">OpenGL (vertex)</th>
<td>0.33 ms</td>
<td>2.5 ms</td>
<td>24 ms</td>
</tr>
<tr>
<th scope="row">OpenGL (fragment)</th>
<td>0.35 ms</td>
<td>2.5 ms</td>
<td>24 ms</td>
</tr>
<tr>
<th scope="row">OpenGL (vertex, instanced)</th>
<td>0.14 ms</td>
<td>0.38 ms</td>
<td>2.1 ms</td>
</tr>
<tr>
<th scope="row">OpenGL (fragment, instanced)</th>
<td>0.14 ms</td>
<td>0.23 ms</td>
<td>2.1 ms</td>
</tr>
</tbody>
</table>

Matplotlib is tolerable for the small dataset, achieving between ~10 fps in the simple method and ~20 fps in the collection method.
For the large dataset, you have to wait 4 seconds between each frame!

OpenGL is significantly faster; in the non-instanced drawing, over 30 fps is achieved for all datasets.
The vertex and fragment approaches appear to have roughly the same performance; ultimately, the extra calculation in the fragment shader is cheap, so you may as well use the fragment approach over the vertex approach.
When using instanced drawing, an additional ~10x performance boost is realized.
By extrapolation, we can see that real-time visualization of over a million circles is achievable.
