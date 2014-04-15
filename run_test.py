import input_gen
reload(input_gen)
from subprocess import call
import os.path


class febio_part:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number
        self.elems = []

class febio_face:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number

class febio_edge:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number
        self.elems = []
        self.fix_disp = None

class febio_node:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number

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



#### simulation specifications

### Edges
Cell_line = febio_edge('Cell_line', 6)
Cell_line.fix_disp = ('xz')
Inde_line = febio_edge('Inde_line', 206)
febio_edges = [Cell_line, Inde_line]

### Parts
Cell_tet4 = febio_part('Cell_tet4', 1)
Cell_tet4.elem_type = 'tet4'
Cell_tet4.mat = 3

Inde_tet4 = febio_part('Inde_tet4', 202)
Inde_tet4.elem_type = 'tet4'
Inde_tet4.mat = 2
febio_parts = [Cell_tet4, Inde_tet4]

print "writing simulation {0:d}".format(id)
print "{0:s}/cell_{0:s}_{1:d}.feb".format(sim_name,id)
input_gen.generate_febio_input(msh_file, id, sim_name, name, \
                               febio_edges, febio_parts,
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
