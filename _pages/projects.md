---
permalink: /projects/
classes: wide
title: "Projects"

entries:
  - title: MiePy
    description: Solve Maxwell's equations for a cluster of particles using the generalized multiparticle Mie theory (GMMT).
    url: /projects/miepy
    image_url: /assets/img/projects/miepy_thumbnail.png
    github_url: https://github.com/johnaparker/miepy
    tags:
      - Python
      - C++

  - title: Stoked
    description: Solves the Stokesian dynamics equations for <i>N</i> interacting particles, a generalization of Brownian dynamics that includes hydrodynamic coupling interactions.
    url: /projects/stoked
    image_url: /assets/img/projects/stoked_thumbnail.svg
    github_url: https://github.com/johnaparker/stoked
    tags:
      - Python

  - title: FPlanck
    description: Numerically solve the Fokker-Planck partial differential equation in <i>N</i> dimensions using a matrix numerical method.
    url: /projects/fplanck
    image_url: /assets/img/projects/fplanck_thumbnail.png
    github_url: https://github.com/johnaparker/fplanck
    tags:
      - Python

  - title: NumPipe
    description: NumPipe is a Python software package that makes long-running tasks easier and faster by executing code in embarrassingly parallel and caching the output to HDF5 files.
    url: /projects/numpipe
    image_url: /assets/img/projects/numpipe_thumbnail.png
    github_url: https://github.com/johnaparker/numpipe
    tags:
      - Python

  - title: QBox
    description: Custom Finite-Difference Time-Domain (FDTD) solver in two-dimensions.
    url: /projects/qbox
    image_url: /assets/img/projects/qbox.png
    github_url: https://github.com/johnaparker/qbox
    tags:
      - C++

  - title: GranSim
    description: Granular simulation.
    url: /projects/gransim
    image_url: /assets/img/projects/gransim_thumbnail.png
    github_url: https://github.com/johnaparker/GranSim
    tags:
      - C++

  - title: GitScan
    description: Git-Scan is a command-line utility to scan local or remote git repositories for history that is divergent from the remote branch.
    url: /projects/gitscan
    image_url: /assets/img/projects/gitscan.svg
    github_url: https://github.com/johnaparker/git-scan
    tags:
      - Python

additional_projects:
  - title: "pybind_examples"
    description: Examples of pybind11 based projects (using cmake)
    github_url: https://github.com/johnaparker/pybind_examples
    
  - title: "h5cpp"
    description: Basic C++ wrapper for HDF5 C library
    github_url: https://github.com/johnaparker/h5cpp

  - title: "h5tree"
    description: HDF5 tree command line utility
    github_url: https://github.com/johnaparker/h5tree

  - title: "meep_ext"
    description: Extensions for Python Meep
    github_url: https://github.com/johnaparker/meep_ext

  - title: "Qpost"
    description: Python library and command-line utility for QBox FDTD software
    github_url: https://github.com/johnaparker/qpost

  - title: "LatBolt"
    description: Solve the Navier-Stokes equations using a Lattice Boltzmann method
    github_url: https://github.com/johnaparker/LatBolt

  - title: "MPI walkers"
    description: Random walkers on a 2D grid using MPI for parallelization
    github_url: https://github.com/johnaparker/walker_mpi

  - title: "my_pytools"
    description: Helper functions to solve common tasks in numpy, matplotlib, h5py, and vpython
    github_url: https://github.com/johnaparker/my_pytools
---

{% include project-entries.html %}
