# Abaqus python script to create an ODB file
# from existing odb file.

# import statements
from abaqus import *
from abaqusConstants import *
import odbAccess

mainodb_name = 'interference_fit.odb'
subodb_name = 'subodb.odb'

# Open main odb
odb = session.openOdb(name=mainodb_name)

# Create sub-odb object
subodb = session.Odb(name='data', path=subodb_name)

# Accessing instances of main odb
isn_names = odb.rootAssembly.instances.keys()

# Iterating through instance names
# ----------------------------------------------------
# Access instance
for isn_name in isn_names:
    isn1 = odb.rootAssembly.instances[isn_name]
    isn_space = isn1.embeddedSpace
    isn_type = isn1.type

    # read the data
    # Extract element information
    el_dict = dict()
    for element in isn1.elements:
        conn = element.connectivity
        label = element.label
        el_type = element.type
        if el_type not in el_dict:
            el_dict[el_type] = [ tuple([label, ] + list(conn)), ]
        else:
            el_dict[el_type].append(tuple([label, ] + list(conn)))
        

    # Extract node information
    nd_label, nd_coords = [], []
    for node in isn1.nodes:
        label = node.label
        coords = node.coordinates
        nd_label.append(label)
        nd_coords.append(tuple(coords))

    # write the data
    # create the part
    # space,  type, name
    mypart = subodb.Part(name=isn_name, embeddedSpace=isn_space,
                        type=isn_type)

    # Add node and elements
    mypart.addNodes(labels=tuple(nd_label), coordinates=tuple(nd_coords))

    for key,val in el_dict.items():
        mypart.addElements(elementData=tuple(val), type=key)

    # Create a instance from the part
    subodb.rootAssembly.Instance(name=isn_name, object=mypart)
# ----------------------------------------------------

# Update and save subodb
subodb.update()
subodb.save()
subodb.close()

# ----------------------------------------------------
# Lec 9 - WRITING THE FIELD DATA TO ODB
import numpy as np

subodb = session.openOdb(name=subodb_name, readOnly=False)

step_name = 'results'
nset_name = 'bush_outer'

# Creating a result step to write the data
step_obj = subodb.Step(name=step_name, description='Result Step',
                       domain=TIME, timePeriod=1.0)

# Create the frame in result step
frame_obj = step_obj.Frame(incrementNumber=1, frameValue=0.0)

# -------------------------------------------------------------------------------
# FIRST CASE
# Create field output
field_obj = frame_obj.FieldOutput(name='U_max', description='Maximum Displacement',
                                  type=VECTOR, componentLabels=('U1', 'U2', 'U3'),
                                  validInvariants=(MAGNITUDE, ))

# Read the data from text file
node_data = np.loadtxt('disp.dat', skiprows=1)
node_labels = np.array(node_data[:, 0], dtype=int)
node_data = node_data[:, 1:]

# Get the instance object
inst_obj = subodb.rootAssembly.instances['BUSH-1']

# Write data at Nodes
field_obj.addData(position=NODAL, instance=inst_obj, labels=tuple(node_labels),
                  data=tuple(node_data))
# INTEGRATION_POINT, ELEMENT_NODAL, CENTROID
# [[0.1, 0.2, 0.25], [0.5, 0.6, 0.1], [...], ...]


# -------------------------------------------------------------------------------
# SECOND CASE
# Create field output
field_obj = frame_obj.FieldOutput(name='U_new', description='Displacement Addition',
                                  type=SCALAR)

# Add two displacement to create New Field Output
u1 = frame_obj.fieldOutputs['U_max'].getScalarField(componentLabel='U1')
u2 = frame_obj.fieldOutputs['U_max'].getScalarField(componentLabel='U2')

# Write field output object
u_new = u1 + u2
field_obj.addData(field=u_new)
# -------------------------------------------------------------------------------

# Update and save subodb
subodb.update()
subodb.save()
subodb.close()

# Open the subodb again
subodb = session.openOdb(name=subodb_name, readOnly=False)

print('Script completed successfully...!!!')







