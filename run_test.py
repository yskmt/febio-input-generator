from input_gen import generate_febio_input
from subprocess import call
import os.path

id=1;
sim_name = "test" 
name = "test"
indent_1 = -0.8e-6
indent_2 = -2e-6
time_steps = 10000
min_dtmax = 0.1

phi0 = 0.5
density = 1.0

c1 = 100 # E=c1*6
c2 = 0.0
k = c1*100

ksi = 0.01
beta = 2.0

g1 = 2
t1 = 1

perm = 1.0e-17 # -7

sliding_penalty = 10

#### write the simulation files
id = 1
msh_file = "cell.msh"

print "writing simulation {0:d}".format(id)
print "{0:s}/cell_{0:s}_{1:d}.feb".format(sim_name,id)
generate_febio_input(msh_file, id, sim_name, name, \
                     indent_1, indent_2, \
                     time_steps, min_dtmax,\
                     phi0, density, \
                     c1, c2, k, \
                     ksi, beta, \
                     g1, t1, \
                     perm, \
                     sliding_penalty\
)

#### Run the simulation
FEBio = "febio"

print "running simulation {0:d}".format(id)
call([FEBio, "{0:s}/cell_{0:s}_{1:d}.feb".format(sim_name,id)])
