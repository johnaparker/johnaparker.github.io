import stoked
from topics.photonic_clusters.create_lattice import hexagonal_lattice_particles
from topics.optical_matter.dynamics import stoked_from_cluster_2d
import matplotlib.pyplot as plt
import numpy as np
import miepy
from numpipe import scheduler, once, pbar
from matplotlib import rc
import tempfile 
import subprocess

job = scheduler()
rc('font', size=14)
nm = ns = 1e-9

### initial state
initial = hexagonal_lattice_particles(7)*600*nm
radius = 75*nm

### dynamic properties
dt = 2500*ns
Nsteps = 15000

# electrodynamic properties
water = miepy.materials.water()
Ag = miepy.materials.Ag()
wavelength = 800*nm
source = miepy.sources.gaussian_beam(polarization=[1,1j], width=1500*nm, power=.2)

@job.cache
def sim():
    cluster = miepy.sphere_cluster(position=initial,
                                   radius=radius,
                                   material=Ag,
                                   source=source,
                                   wavelength=wavelength,
                                   medium=water,
                                   lmax=2)

    bd = stoked_from_cluster_2d(cluster, dt=dt, temperature=300)

    for i in pbar(range(Nsteps)):
        if i % 10 == 0:
            yield dict(pos=bd.position)
        bd.step()

def make_pov_file(pos):
    particle_str = "sphere {{<{x:.2f},{y:.2f},Height>, Radius texture{{Silver}}}}"
    particles = '\n'.join([particle_str.format(x=p[0], y=p[1]) for p in pos])

    pov_str = """
#include "colors.inc"
#include "glass.inc"
#include "golds.inc"
#include "metals.inc"
#include "stones.inc"
#include "woods.inc"
#include "metals.inc"
#include "textures.inc"
#include "shapes.inc"

//Ambient light to "brighten up" darker pictures
global_settings { ambient_light White }

global_settings { 
	photons {
		spacing 0.2
		autostop 1
		media 60
		max_trace_level 6
	}
}
#declare transparent_with_media = material{
	texture {
		pigment { 
			rgbt 1 
		}
		finish {
			ambient 0
			diffuse 0
		}
	}
	interior{
		media {
			scattering {
				1, 
				rgb <0.1, 0.1, 0.1>
				extinction 0.000001
			}
			samples 20,50
		}
	}
}

light_group {
	light_source {
// Position
		<0, 0, 70>
// Color and intensity multiplicator
		color Red*60
		cylinder
// direction of your laser
		point_at <6, -5, 0>
// Size and properties of the gaussian beam profile
		radius 8
		falloff 40
		tightness 20
		photons {
			reflection on
		}
	}
	merge {
        box{<-90,-90,1.5>,<90,90,70>}
        //box{<-90,-90,-100>,<90,90,-.0001>}
        hollow
        material {
            transparent_with_media 
        }
        photons {
            pass_through
        }
    }
    global_lights off
}



//Place the camera
camera {
  sky <0,0,1>           //Don't change this
  direction <-1,0,0>    //Don't change this  
  right <-3/3,0,0>      //Don't change this
  location <190,-160,200.5> //Camera location
  look_at <0,0,2>     //Where camera is pointing
  angle 4.3      //Angle of the view--increase to see more, decrease to see less
}

//Place a light--you can have more than one!
light_source {
  <10,-10,180>   //Change this if you want to put the light at a different point
  color White*.8         //Multiplying by 2 doubles the brightness
  spotlight
  point_at <0, 0, 2>
  tightness 120
  radius 20
  falloff 100
  media_interaction off
}

//light_source {
  //<0,-900,70>   //Change this if you want to put the light at a different point
  //color White*.02         //Multiplying by 2 doubles the brightness
//}

//light_source {
  //<0,0,2000>   //Change this if you want to put the light at a different point
  //color Gray*.02         //Multiplying by 2 doubles the brightness
//}

//Set a background color
background { color White }

//Create a "floor"
//plane {
  //<0,0,1>, 0            //This represents the plane 0x+0y+z=0
  //texture { Dark_Green_Glass }       //The texture comes from the file "metals.inc"
//}
// Ground plane
plane { z, -1
   pigment {White}
   texture {NBglass}
   //texture {Dark_Green_Glass}
   finish {
      ambient 0.01
      diffuse 0.01
      specular 0.01
      roughness 0.01
      reflection .0015
   }
}

//Sphere with specified center point and radius
//The texture comes from the file "stones.inc"

#declare Height = 2;
//#declare Silver = texture{pigment{Silver} 
#declare Silver = texture{pigment{BrightGold} 
     finish {
        ambient .1
        diffuse .1
        specular .75
        roughness .1
        metallic
        reflection {
          .5
          //.35
          metallic
        }
     }
};

#declare Radius = 1.2;

#declare Wx = 35;
box{
    <-Wx, -Wx, 0>, <Wx,Wx,Height-.5>
    texture{Dark_Green_Glass}
    rotate -28*z
    finish{reflection {.3}}
}

"""

    return pov_str + particles

@job.cache(depends=sim)
def make_vid():
    var = job.load(sim)
    traj = var.pos[::10]
    for i in pbar(range(len(traj))):
        pov_content = make_pov_file(traj[i]/(100*nm))
        with open('om.pov', 'w') as f:
            f.write(pov_content)

        command = ['povray', 'Width=600 Height=600 om.pov', f'-Oimg/img_{i+1}']
        proc = subprocess.run(command, capture_output=True)

    return dict()

@job.plots
def vis():
    var = job.load(sim)

    patches = stoked.circle_patches(radius/nm)

    anim = stoked.trajectory_animation(var.pos[::10]/nm, patches=patches, colors='C0', trail=0)

job.execute()
