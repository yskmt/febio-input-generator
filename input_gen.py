from subprocess import call
from lxml import etree
import numpy as np
import pdb

##### simulation
def generate_febio_input( msh_file, id, sim_name, name, \
                          febio_edges, febio_parts, febio_faces, \
                          febio_mats, febio_rigids, \
                          indent_1, indent_2, \
                          time_steps, min_dtmax,\
                          phi0, density, \
                          c1, c2, k, \
                          ksi, beta, \
                          g1, t1, \
                          perm, \
                          sliding_penalty\
):
    
    f = open(msh_file)
    content = f.readlines()
    f.close()

    # output
    call(["mkdir", "-p", sim_name])
    f = open('{0:s}/cell_{0:s}_{1:d}.feb'.format(sim_name,id), 'w')

    # scale
    sc = 1e-6

    len_file = len(content)
    node_start = len_file
    node_end = -1
    elem_start = len_file
    elem_end = -1

    Nodes = []


    for i in range(len_file):
        # get number of nodes
        # get the start and end line numbers of node data
        if content[i].find("$Nodes") != -1:
            n_nodes = int(content[i+1])
            node_start = i+2
            node_end = i+2+n_nodes
            
        # collect node information
        if (i>=node_start) & (i<node_end):
            node_list = content[i].split('\n')[0].split(' ')
            node_info = []
            node_info.append(int(node_list[0]))
            node_info.append(float(node_list[1])*sc)
            node_info.append(float(node_list[2])*sc)
            node_info.append(float(node_list[3])*sc)
            Nodes.append(node_info)

        # get number of elements
        # get the start and end line numbers of element data
        if content[i].find("$Elements") != -1:
            n_elem = int(content[i+1])
            elem_start = i+2
            elem_end = i+2+n_elem

        # collect element information
        if (i>=elem_start) & (i<elem_end):
            elem_list = content[i].split('\n')[0].split(' ')
            elem_info = []
            elem_info.append(int(elem_list[0]))
            elem_info.append(int(elem_list[1]))
            elem_info.append(int(elem_list[2]))
            elem_info.append(int(elem_list[3]))        
            elem_info.append(int(elem_list[4]))

            # edges
            if elem_info[1] == 1:
                elem_info.append(int(elem_list[5]))
                elem_info.append(int(elem_list[6]))
                for ed in range(len(febio_edges)):
                    if elem_info[3]==febio_edges[ed].number:
                        febio_edges[ed].elems.append(elem_info)

            # parts
            if (elem_info[1] == 4):
                elem_info.append(int(elem_list[5]))
                elem_info.append(int(elem_list[6]))
                elem_info.append(int(elem_list[7]))
                elem_info.append(int(elem_list[8]))
                for pt in range(len(febio_parts)):
                    if elem_info[3]==febio_parts[pt].number:
                        febio_parts[pt].elems.append(elem_info)

            # faces
            if (elem_info[1] == 2):
                elem_info.append(int(elem_list[5]))
                elem_info.append(int(elem_list[6]))
                elem_info.append(int(elem_list[7]))
                for fc in range(len(febio_faces)):
                    if elem_info[3]==febio_faces[fc].number:
                        febio_faces[fc].elems.append(elem_info)


    # Collect the edge nodes for fixed displacement condition
    for ed in range(len(febio_edges)):
        if febio_edges[ed].fix_disp != None:
            # Add fix_disp_nodes member
            febio_edges[ed].fix_disp_nodes = []

            # collect and order the edge fixed nodes
            for i in range(len(febio_edges[ed].elems)):
                febio_edges[ed].fix_disp_nodes.append(febio_edges[ed].elems[i][5])
                febio_edges[ed].fix_disp_nodes.append(febio_edges[ed].elems[i][6])
            # remove duplicates and sort
            febio_edges[ed].fix_disp_nodes=list(set(febio_edges[ed].fix_disp_nodes))
            febio_edges[ed].fix_disp_nodes.sort()            

    # Collect the face nodes for fixed displacement condition
    for fc in range(len(febio_faces)):
        if febio_faces[fc].fix_disp != None:
            # Add fix_disp_nodes member
            febio_faces[fc].fix_disp_nodes = []
            
            # collect and order the face fixed nodes
            for i in range(len(febio_faces[fc].elems)):
                febio_faces[fc].fix_disp_nodes.append(febio_faces[fc].elems[i][5])
                febio_faces[fc].fix_disp_nodes.append(febio_faces[fc].elems[i][6])
                febio_faces[fc].fix_disp_nodes.append(febio_faces[fc].elems[i][7])
            # remove duplicates and sort
            febio_faces[fc].fix_disp_nodes=list(set(febio_faces[fc].fix_disp_nodes))
            febio_faces[fc].fix_disp_nodes.sort()

    #####################################################################
    ##                Now write the .feb file                          ##
    #####################################################################

    # header
    root = etree.Element("febio_spec", version="1.2")

    # Global
    Globals_xml = etree.SubElement(root, "Globals")

    ## Constants
    Constants_xml = etree.SubElement(Globals_xml, "Constants")
    etree.SubElement(Constants_xml, "T").text = "0"
    etree.SubElement(Constants_xml, "R").text = "0"
    etree.SubElement(Constants_xml, "Fc").text = "0"

    # Material
    Material_xml = etree.SubElement(root, "Material")

    for mt in range(len(febio_mats)):
        material_xml = etree.SubElement(Material_xml, "material",
                                        id = str(febio_mats[mt].mat),
                                        name = febio_mats[mt].name,
                                        type = febio_mats[mt].mat_type)

        for atr in febio_mats[mt].mat_attributes.keys():
            if type(febio_mats[mt].mat_attributes[atr])==dict:
                solid_xml = etree.SubElement(material_xml, atr,\
                                             type=str(febio_mats[mt].mat_attributes[atr]['type']))

                for atr2 in febio_mats[mt].mat_attributes[atr].keys():
                    if type(febio_mats[mt].mat_attributes[atr][atr2])==dict:

                        elastic_xml = etree.SubElement(solid_xml, atr2, \
                                                       type=str(febio_mats[mt].mat_attributes[atr][atr2]['type']))
                    
                        for atr3 in febio_mats[mt].mat_attributes[atr][atr2].keys():
                            if atr3 != 'type':
                                etree.SubElement(elastic_xml, atr3).text = str(febio_mats[mt].mat_attributes[atr][atr2][atr3])

                    elif atr2 != 'type':
                        etree.SubElement(solid_xml, atr2).text \
                            =str(febio_mats[mt].mat_attributes[atr][atr2])
            else:
                etree.SubElement(material_xml, atr).text \
                    = str(febio_mats[mt].mat_attributes[atr])

    # Geometry
    Geometry_xml = etree.SubElement(root, "Geometry")
    
    ## Nodes
    Nodes_xml = etree.SubElement(Geometry_xml, "Nodes")
    for i in range(len(Nodes)):
        etree.SubElement(Nodes_xml, "node", id="{0:d}".format(Nodes[i][0])).text = "{0:9.7e}, {1:9.7e}, {2:9.7e}".format(Nodes[i][1], Nodes[i][2], Nodes[i][3])

    ## Elements
    Elements_xml = etree.SubElement(Geometry_xml, "Elements")
    elem_id = 0

    ### Parts
    for pt in range(len(febio_parts)):
        for i in range(len(febio_parts[pt].elems)):
            elem_id+=1;
            febio_parts[pt].elems[i][0] = elem_id
            etree.SubElement(Elements_xml, febio_parts[pt].elem_type,
                             id="{0:d}".format(elem_id),
                             mat="{0:d}".format(febio_parts[pt].mat)).text \
                = "{0:5d}, {1:5d}, {2:5d}, {3:5d}"\
                    .format( febio_parts[pt].elems[i][5],
                             febio_parts[pt].elems[i][6],
                             febio_parts[pt].elems[i][7],
                             febio_parts[pt].elems[i][8] )

    ### Faces
    for fc in range(len(febio_faces)):
        # check if shell element
        if febio_faces[fc].shell == 1:            
            for i in range(len(febio_faces[fc].elems)):
                elem_id+=1;
                febio_faces[fc].elems[i][0] = elem_id
                etree.SubElement(Elements_xml, febio_faces[fc].elem_type,
                                 id="{0:d}".format(elem_id),
                                 mat="{0:d}".format(febio_faces[fc].mat)).text \
                = "{0:5d}, {1:5d}, {2:5d}" \
                .format(febio_faces[fc].elems[i][5],
                        febio_faces[fc].elems[i][6],
                        febio_faces[fc].elems[i][7])
    
    ## ElementData
    ElementData_xml = etree.SubElement(Geometry_xml, "ElementData")
    
    ### Shell element thickness
    for fc in range(len(febio_faces)):
        # check if shell element
        if febio_faces[fc].shell == 1:    
            for i in range(len(febio_faces[fc].elems)):
                ElData_element_xml \
                    = etree.SubElement(ElementData_xml,
                                       "element",
                                       id="{0:d}"\
                                       .format(febio_faces[fc].elems[i][0]))
                etree.SubElement(ElData_element_xml, "thickness").text \
                    = febio_faces[fc].thickness

    # Boundary
    Boundary_xml = etree.SubElement(root, "Boundary")
    
    ## fixed displacement for face element
    for fc in range(len(febio_faces)):
        if febio_faces[fc].fix_disp != None:
            fix_xml = etree.SubElement(Boundary_xml, "fix")
            for i in range(len(febio_faces[fc].fix_disp_nodes)):
                etree.SubElement(fix_xml, "node",
                                 id="{0:d}".format(febio_faces[fc].fix_disp_nodes[i]),
                                 bc=febio_faces[fc].fix_disp)

    ## fixed displacement for edge element
    for ed in range(len(febio_edges)):
        if febio_edges[ed].fix_disp != None:
            fix_xml = etree.SubElement(Boundary_xml, "fix")
            for i in range(len(febio_edges[ed].fix_disp_nodes)):
                etree.SubElement(fix_xml, "node", \
                                 id="{0:d}".format(febio_edges[ed].fix_disp_nodes[i]), \
                                 bc=febio_edges[ed].fix_disp)

    ## Contact Boundary 
    for fc in range(len(febio_faces)):
        if hasattr(febio_faces[fc], 'slave'):

            ## contact boundary attributes
            contact_xml = etree.SubElement(Boundary_xml, "contact", type=febio_faces[fc].contact_type)
            for atr in febio_faces[fc].contact_attributes.keys():
                etree.SubElement(contact_xml, atr).text \
                    = str(febio_faces[fc].contact_attributes[atr])

            # get slave faces
            slave = febio_faces[fc].slave
            
            ### contact master surface
            surface_xml = etree.SubElement(contact_xml, "surface", type="master")
            for i in range(len(febio_faces[fc].elems)):
                etree.SubElement(surface_xml,
                                 febio_faces[fc].elem_type,
                                 id="{0:d}".format(i+1)).text \
                    = "{0:d}, {1:d}, {2:d}"\
                        .format(febio_faces[fc].elems[i][5],
                                febio_faces[fc].elems[i][6],
                                febio_faces[fc].elems[i][7])

            ### contact slave surface
            surface_xml = etree.SubElement(contact_xml, "surface", type="slave")
            for sn in range(len(slave)):
                # get the index of the slave face
                for i in range(len(febio_faces)):
                    if febio_faces[i].number==slave[sn]:
                        fc_sl = i
                
                for i in range(len(febio_faces[fc_sl].elems)):
                    etree.SubElement(surface_xml,
                                     febio_faces[fc_sl].elem_type,
                                     id="{0:d}".format(i+1)).text \
                        = "{0:d}, {1:d}, {2:d}"\
                            .format(febio_faces[fc_sl].elems[i][5],
                                    febio_faces[fc_sl].elems[i][6],
                                    febio_faces[fc_sl].elems[i][7])
    
    # Constraints
    Constraints_xml = etree.SubElement(root, "Constraints")

    for rg in range(len(febio_rigids)):
        rigid_body_xml = etree.SubElement(Constraints_xml, "rigid_body", mat=str(febio_rigids[rg].mat))

        for cst in febio_rigids[rg].rigid_constraints.keys():
            
            # prescribed
            if type(febio_rigids[rg].rigid_constraints[cst])==list:
                etree.SubElement(rigid_body_xml, cst,
                                 type=str(febio_rigids[rg].rigid_constraints[cst][0]),
                                 lc=str(febio_rigids[rg].rigid_constraints[cst][1])).text = str(febio_rigids[rg].rigid_constraints[cst][2])

            # fixed
            else:
                etree.SubElement(rigid_body_xml, cst,
                                 type=str(febio_rigids[rg].rigid_constraints[cst]))

    # Load Data
    LoadData_xml = etree.SubElement(root, "LoadData")
    
    ### saving step
    loadcurve_xml = etree.SubElement(LoadData_xml, "loadcurve", id="1", type="linear", extend="constant") 
    savetime = np.linspace(0.0,110.0,111)
    for i in range(len(savetime)):
        etree.SubElement(loadcurve_xml, "loadpoint").text = "{0:e}, {1:e}".format(savetime[i], min_dtmax*10)

    ### indenter y-direction movement
    loadcurve_xml = etree.SubElement(LoadData_xml, "loadcurve", id="2", type="smooth")
    etree.SubElement(loadcurve_xml, "loadpoint").text = "0, 0"
    etree.SubElement(loadcurve_xml, "loadpoint").text = "1.0, {0:9.7e}".format(indent_1)
    etree.SubElement(loadcurve_xml, "loadpoint").text = "3.5, {0:9.7e}".format(indent_2)

    # Output
    Output_xml = etree.SubElement(root, "Output")
    plotfile_xml = etree.SubElement(Output_xml, "plotfile", type="febio")
    etree.SubElement(plotfile_xml, "var", type="displacement")
    etree.SubElement(plotfile_xml, "var", type="velocity")
    etree.SubElement(plotfile_xml, "var", type="effective fluid pressure")
    etree.SubElement(plotfile_xml, "var", type="fluid flux")
    etree.SubElement(plotfile_xml, "var", type="stress")
    etree.SubElement(plotfile_xml, "var", type="relative volume")
    # etree.SubElement(plotfile_xml, "var", type="fiber vector")

    ## Log
    logfile_xml = etree.SubElement(Output_xml, "logfile", file="{0:s}/cell_{0:s}_{1:d}.log".format(sim_name,id))
    nodefile = "{0:s}/disp_{0:s}_{1:d}.txt".format(sim_name,id)
    etree.SubElement(logfile_xml, "node_data", file=nodefile, name="front tip displacement", data="uy").text = "2"
    fzfile = "{0:s}/fz_{0:s}_{1:d}.txt".format(sim_name,id)
    etree.SubElement(logfile_xml, "rigid_body_data", file=fzfile, data="Fy").text = "2"

    # Step01
    Step_xml = etree.SubElement(root, "Step", name="Step01")
    etree.SubElement(Step_xml, "Module", type="biphasic")
    Control_xml = etree.SubElement(Step_xml, "Control")

    etree.SubElement(Control_xml, "time_steps").text = "{0:d}".format(time_steps)
    etree.SubElement(Control_xml, "step_size").text = "0.001"
    etree.SubElement(Control_xml, "max_refs").text = "15"
    etree.SubElement(Control_xml, "max_ups").text = "10"
    etree.SubElement(Control_xml, "dtol").text = "0.001"
    etree.SubElement(Control_xml, "etol").text = "0.01"
    etree.SubElement(Control_xml, "rtol").text = "0"
    etree.SubElement(Control_xml, "ptol").text = "0.01"
    etree.SubElement(Control_xml, "lstol").text = "0.9"
    time_stepper_xml = etree.SubElement(Control_xml, "time_stepper")
    etree.SubElement(time_stepper_xml, "dtmin").text = "0.01"
    etree.SubElement(time_stepper_xml, "dtmax", lc="1")
    etree.SubElement(time_stepper_xml, "max_retries").text = "10"
    etree.SubElement(time_stepper_xml, "opt_iter").text = "10"
    etree.SubElement(Control_xml, "plot_level").text = "PLOT_MUST_POINTS"
    etree.SubElement(Control_xml, "print_level").text = "PRINT_MAJOR_ITRS"

    ## Loads
    # Loads_xml = etree.SubElement(Step_xml, "Loads")

    ### pressure
    # pressure_xml = etree.SubElement(Loads_xml, "normal_traction", type="nonlinear", traction="mixture")
    # for i in range(len(Elem_pressure)):
    #     etree.SubElement(pressure_xml, "tri3", id="{0:d}".format(i+1), lc="2", scale="-1").text = "{0:d}, {1:d}, {2:d}".format(Elem_pressure[i][5], Elem_pressure[i][6], Elem_pressure[i][7])

    # get the string and write to file
    xml_str = etree.tostring(root, encoding='ISO-8859-1', pretty_print="true")
    f.write(xml_str)
    
    # close the file
    f.close()

