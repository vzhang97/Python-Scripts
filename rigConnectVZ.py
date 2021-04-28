# Created by Vincent Zhang
# v1.3
# Date: 27/04/2021

# Select the Bind set, it will parent constraint all the twin rig joints to the bind joints

import maya.cmds as cmds

# Select sets 
selection = cmds.ls(sl=1)

bind = []
rig = []
removeEndJoints = True


# Select members of set
cmds.select(selection[0])


# Check if Bind Root Exists
temp = cmds.ls("Bind_C_Root")
if not temp:
	cmds.error("No Root found in scene")
else:
	cmds.select("Bind_C_Root", add=1)

# Pass the list to a variable
joints = cmds.ls(sl=1)

# Clear selection
cmds.select(cl=1)

# Remove end joints just in case
if removeEndJoints == True:
	for x in joints:
		if "End" in x:
			joints.remove(x)

# Connect each bind joint to the same rig bone
for joint in joints:

	# Clean up the name to search for twin joint on the rig set
	jointName = joint.replace("Bind_", "")

	# Name of joints
	bindJoint = joint 
	rigJoint = "Rig_" + jointName

	# Check if rigJoint exists in scene
	if not cmds.ls(rigJoint):
		cmds.error("Twin rig joint " + rigJoint + "does not exists, please ensure to rename or create appropriate joint")

	# Parent constraint rig joints to bind joints
	cmds.parentConstraint(rigJoint, bindJoint, w=1, mo=0 )


"""
if len(selection) != 2:
	cmds.error("Please select 2 sets that you want to connect")

# Check if Bind and Rig sets are selected. 
# Assign the set to the appropriate variable
for set in selection:
	if not "Bind" in set:
		if not "Rig" in set:
			cmds.error("Please select a Bind and Rig set")

	if "Bind" in set:
		bind = cmds.listRelatives(set, ad=1, typ="joint")
	elif "Rig" in set:
		rig = cmds.listRelatives(set, ad=1, typ="joint")

# Add Root manually
temp = cmds.ls("Bind_C_Root")
if not temp:
	cmds.error("No Root found in scene")
else:
	bind.append("Bind_C_Root")
	rig.append("Rig_C_Root")
	

# Clean up bind list before connecting (Remove End joints)
if removeEndJoints == True:
	for x in bind:
		if "End" in x:
			bind.remove(x)
			

# Connect each bind joint to the same rig bone
for joint in bind:

	# Clean up the name to search for twin joint on the rig set
	jointName = joint.replace("Bind_", "")

	print jointName

	# Name of joints
	bindJoint = joint 
	rigJoint = "Rig_" + jointName

	# Check if rigJoint exists in scene
	if not cmds.ls(rigJoint):
		cmds.error("Twin rig joint " + rigJoint + "does not exists, please ensure to rename or create appropriate joint")

	# Parent constraint rig joints to bind joints
	cmds.parentConstraint(rigJoint, bindJoint, w=1, mo=0 )

"""







"""

temp = cmds.ls(type="joint")

rig_joints = []
bind_joints = []

for i in temp:
	if "Rig_" in i:
		rig_joints.append(i)
	elif "Bind_" in i:
		bind_joints.append(i)


print len(rig_joints)
print len(bind_joints)

if len(rig_joints) != len(bind_joints):
	cmds.error("Please select the same set of bones, use Rig_ and Bind_ prefix")

for i in range(len(rig_joints)):
	cmds.parentConstraint(rig_joints[i], bind_joints[i], w=1, mo=1)


print rig_joints
print bind_joints

"""