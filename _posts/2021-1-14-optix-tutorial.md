---
title: "Real-time ray tracing tutorial series using NVIDIA OptiX 7"
excerpt: "A ray tracing turorial series for OptiX 7 starting from the basics and covering advanced topics from materials and real-time animation"
image_url: https://jparker.nyc3.digitaloceanspaces.com/optix-tutorial/teasers/optix_tutorial_triangle.png

toc: false
classes: wide

tags:
  - Graphics
  - Tutorial

github_url: https://github.com/johnaparker/optix7tutorial

entries:
  - title: "Getting started"
    description: Configure OptiX, setup a shader binding table, and write a ray-generation and ray-miss program to render a background gradient
    teaser: https://jparker.nyc3.digitaloceanspaces.com/optix-tutorial/teasers/optix_tutorial_getting_started.png
    url: /optix-tutorial/getting-started

  - title: "Rendering a triangle"
    description: Write vertex data to the GPU, build an acceleration structure, and write a closest-hit program to render a single triangle
    teaser: https://jparker.nyc3.digitaloceanspaces.com/optix-tutorial/teasers/optix_tutorial_triangle.png
    url:

  - title: "Making a custom primitive: ray-sphere intersection"
    description: Write a ray-intersection program, create a custom primitive, and render a sphere using the intersection point and surface normal vector
    teaser: https://jparker.nyc3.digitaloceanspaces.com/optix-tutorial/teasers/optix_tutorial_sphere.png
    url:

  - title: "Light sources and basic shading"
    description: Combine triangle meshes and spheres to create a scene with ambient, diffuse, and specular lighting
    teaser: 
    url:

  - title: "Advanced shading: metals, glass, and shadows"
    description: 
    teaser: 
    url:

  - title: "Animations: rebuilding and refining the acceleration structure"
    description: 
    teaser: 
    url:

  - title: "Rendering a large collection of objects"
    description: 
    teaser: 
    url:

  - title: "Implementing a path tracer"
    description: 
    teaser: 
    url:

  - title: "Textures and models"
    description: 
    teaser: 
    url:

  - title: "Using Bullet to do real-time physics"
    description: 
    teaser: 
    url:
---

### **(This is a work in progress)**
{% include tutorial-entries.html %}

## Extra
1. [Implementing a user-controlled camera]()
1. [Denoising]()
1. [Exporting to image or video]()
1. [A high-level Python interface using pybind11]()

## Resources
* [How to get started with OptiX 7](https://developer.nvidia.com/blog/how-to-get-started-with-optix-7/)
* [NVIDIA OptiX 7 programming guide](https://raytracing-docs.nvidia.com/optix7/guide/index.html#preface#)
* [Ingo Wald's OptiX 7 Course](https://github.com/ingowald/optix7course)
* [Peter Shirley's Ray Tracing in One Weekend Series](https://raytracing.github.io)
