import input_gen
reload(input_gen)
from subprocess import call
import os.path
from febio_data_structures import *

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





#### write the simulation files
sim_id = 1
msh_file = "cell.msh"

#### simulation specifications

### Edges
Cell_line = febio_edge('Cell_line', 6)
Cell_line.fix_disp = ('xz')
Inde_line = febio_edge('Inde_line', 206)

### Parts
Cell_tet4 = febio_part('cell', 1)
Cell_tet4.elem_type = 'tet4'
Cell_tet4.mat = 3
Cell_tet4.mat_type = 'biphasic'
Cell_tet4.mat_attributes = {'phi0':phi0,
                            'solid':{'type':'uncoupled viscoelastic',
                                     'g1':g1, 't1':t1,
                                     'elastic':{'type':'Mooney-Rivlin',
                                                'c1':c1, 'c2':c2, 'k':k}
                                 },
                            'permeability':{'type':'perm-const-iso',
                                            'perm':perm}}

Inde_tet4 = febio_part('indenter', 202)
Inde_tet4.elem_type = 'tet4'
Inde_tet4.mat = 2
Inde_tet4.mat_type = 'rigid body'
Inde_tet4.mat_attributes = {'density':1, 'center_of_mass':"1,1.8,0"}
Inde_tet4.rigid_constraints = {'trans_x':'fixed',
                               'trans_y':['prescribed', 2, 1],
                               'trans_z':'fixed',
                               'rot_x':'fixed',
                               'rot_y':'fixed',
                               'rot_z':'fixed',}

### Faces
Symm_tri3 = febio_face('symmetry plane', 101)
Symm_tri3.shell = 1
Symm_tri3.elem_type = 'tri3'
Symm_tri3.mat = 1
Symm_tri3.mat_type = 'rigid body'
Symm_tri3.mat_attributes = {'density':1, 'center_of_mass':'0,0,0'}
Symm_tri3.thickness = '0,0,0'
Symm_tri3.slave = [5]
Symm_tri3.contact_type = 'sliding-tension-compression'
Symm_tri3.contact_attributes = {"laugon":"0", "tolerance":"0.2", "gaptol":"0",
                                "penalty":"1000", "auto_penalty":"1", "two_pass":"0",
                                "search_tol":"0.01", "symmetric_stiffness":"0",
                                "search_radius":"1", "seg_up":"0", "tension":"1",
                                "minaug":"0", "maxaug":"10"}
Symm_tri3.rigid_constraints = {'trans_x':'fixed',
                               'trans_y':'fixed',
                               'trans_z':'fixed',
                               'rot_x':'fixed',
                               'rot_y':'fixed',
                               'rot_z':'fixed',}

Cell_front_tri3 = febio_face('Cell_front_tri3', 4)
Cell_front_tri3.fix_disp = 'z'

Cell_back_tri3 = febio_face('Cell_back_tri3', 5)
Cell_back_tri3.elem_type = 'tri3'

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
Inde_bottom_tri3.contact_attributes = {'two_pass':0, 'auto_penalty':1, 'fric_coeff':0,
                                       'fric_penalty':0, 'search_tol':0.01, 'minaug':0,
                                       'maxaug':10, 'gaptol':0, 'seg_up':0}

## define FEM system
febio_edges = [Cell_line, Inde_line]
febio_parts = [Cell_tet4, Inde_tet4]
febio_faces = [Symm_tri3, Cell_front_tri3, Cell_back_tri3, Cell_top_tri3, Cell_bottom_tri3, Inde_front_tri3, Inde_back_tri3, Inde_top_tri3, Inde_bottom_tri3]
febio_mats = [Symm_tri3, Inde_tet4, Cell_tet4]
febio_rigids = [Symm_tri3, Inde_tet4]

## outputs

output_types = ['displacement', 'velocity', 'effective fluid pressure', 'fluid flux', 'stress', 'relative volume']
nodefile = '"node_data", file="nodefilename", name="y-displacement", data="uy"'
fzfile = '"rigid_body_data", file="fzfilename", name="y-reaction force", data="Fy"'
outputs = {'"plotfile", type="febio"':[output_types],
           '"logfile", file="logfilename"':{nodefile:2, fzfile:2}}

plot_outputs = Tree('plotfile')
plot_outputs.attributes = {'type':'febio'}
plot_outputs.output_types = ['displacement', 'velocity', 'effective fluid pressure', 'fluid flux', 'stress', 'relative volume']

log_outputs = Tree('logfile')
log_outputs.attributes = {'file':'{0:s}/logfile.txt'.format(sim_name)}

node_outputs = Tree('node_data')
node_outputs.attributes = {'file':'{0:s}/ndfile.txt'.format(sim_name),
                           'data':'uy', 'text':'2'}

rigid_outputs = Tree('rigid_body_data')
rigid_outputs.attributes = {'file':'{0:s}/fzfile.txt'.format(sim_name),
                            'data':'Fy', 'text':'2'}

log_outputs.children = [node_outputs, rigid_outputs]

febio_outputs = Tree
febio_outputs.children = [plot_outputs, log_outputs]


step01 = febio_step('Step01')
step01.module = 'biphasic'
step01.control = {"time_steps":"{0:d}".format(time_steps),
                  "step_size":"0.001", "max_refs":"15", "max_ups":"10",
                  "dtol":"0.001", "etol":"0.01", "rtol":"0", "ptol":"0.01",
                  "lstol":"0.9", "plot_level":"PLOT_MUST_POINTS",
                  "print_level":"PRINT_MAJOR_ITRS"}
step01.time_stepper = {'dtmin':0.01, 'dtmax':'lc=1', 'max_retries':10, 'opt_iter':10}

febio_steps = [step01]

## loadcurves
lc1 = febio_loadcurve(1, 'linear', 'constant')
lc2 = febio_loadcurve(2, 'linear', 'constant')
lc1.loadpoints = [(t, min_dtmax*10) for t in np.linspace(0.0,110.0,111)]
lc2.loadpoints = [(0,0), (1.0, indent_1), (3.5, indent_2)]

febio_lcs = [lc1, lc2]

print "writing simulation {0:d}".format(id)
print "{0:s}/cell_{0:s}_{1:d}.feb".format(sim_name,id)
input_gen.generate_febio_input(msh_file, sim_id, sim_name, \
                               febio_edges, febio_parts, febio_faces, \
                               febio_mats, febio_rigids, \
                               febio_outputs, febio_steps, \
                               febio_lcs )

#### Run the simulation
FEBio = "febio"

print "running simulation {0:d}".format(id)
call([FEBio, "{0:s}/cell_{0:s}_{1:d}.feb".format(sim_name,id)])
