import input_gen
reload(input_gen)
from subprocess import call
import os.path


class febio_part:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number
        self.elems = []
        self.fix_disp = None

class febio_face:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number
        self.elems = []
        self.fix_disp = None
        self.shell = 0

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

### Faces
Symm_tri3 = febio_face('Symm_tri3', 101)
Symm_tri3.shell = 1
Symm_tri3.elem_type = 'tri3'
Symm_tri3.mat = 1
Symm_tri3.thickness = '0,0,0'

Cell_front_tri3 = febio_face('Cell_front_tri3', 4)
Cell_front_tri3.fix_disp = 'z'
Cell_back_tri3 = febio_face('Cell_back_tri3', 5)

Cell_top_tri3 = febio_face('Cell_top_tri3', 2)
Cell_top_tri3.elem_type = 'tri3'

Cell_bottom_tri3 = febio_face('Cell_bottom_tri3',3)

Cell_bottom_tri3.fix_disp = 'y'
Inde_front_tri3 = febio_face('Inde_front_tri3', 204)
Inde_front_tri3.fix_disp = 'z'
Inde_back_tri3 = febio_face('Inde_back_tri3', 205)

Inde_top_tri3 = febio_face('Inde_top_tri3', 202)

Inde_bottom_tri3 = febio_face('Inde_bottom_tri3', 203)
Inde_bottom_tri3.elem_type = 'tri3'
Inde_bottom_tri3.slave = [2]
Inde_bottom_tri3.contact_type = 'facet-to-facet sliding'
inde_cell_contact = { 'two_pass':0, 'auto_penalty':1, 'fric_coeff':0,
                      'fric_penalty':0, 'search_tol':0.01, 'minaug':0,
                      'maxaug':10, 'gaptol':0, 'seg_up':0}
Inde_bottom_tri3.contact_attributes = inde_cell_contact

febio_faces = [Symm_tri3, Cell_front_tri3, Cell_back_tri3, Cell_top_tri3, Cell_bottom_tri3, Inde_front_tri3, Inde_back_tri3, Inde_top_tri3, Inde_bottom_tri3]

print "writing simulation {0:d}".format(id)
print "{0:s}/cell_{0:s}_{1:d}.feb".format(sim_name,id)
input_gen.generate_febio_input(msh_file, id, sim_name, name, \
                               febio_edges, febio_parts, febio_faces,
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
