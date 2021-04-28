# Created by Vincent Zhang
# v.1.0
# 26/04/21

import maya.cmds as cmds

selected = cmds.ls(sl=1)

# Check if have 3 joints selected
if len(selected) != 3:
    cmds.error("Selected 3 Bones")

# Declare the variables
ik = ""
fk = ""
og = ""
bone = ["Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle", "Ball", "Toe"]
selectedBone = ""
side = ""

# Initialise the variables accordingly by FK/IK & OG joint
for x in selected:
    if "IK" in x:
       ik = x
    elif "FK" in x:
        fk = x
    else:
        og = x 
    
# Check if selected bone is blendable for FK and IK
for i in range(len(bone)):
    if bone[i] in og:
        selectedBone = bone[i]
        break
    
    if i == len(bone)-1:
        cmds.error("Select a blendable limb joint (Arm/Legs)")


# Check that the selected bone is in FK and IK bones
if not selectedBone in fk:
    if not selectedBone in ik:
        cmds.error("Select the same bone for all 3 joints")


# Check for limb side (Left or Right)
if "L_" in og:
    side = "L"
if "R_" in og:
    side = "R"


# Create nice name for blend node
blendNN = "Rig_" + side + "_" + selectedBone + "_blend"

# Create the blend node
cmds.createNode("blendColors", n=blendNN)

# Connect the joints to blend node
cmds.connectAttr(fk + ".rotate", blendNN + ".color1") 
cmds.connectAttr(ik + ".rotate", blendNN + ".color2") 
cmds.connectAttr(blendNN + ".output", og + ".rotate") 


print og

print selected

print ik, fk , og