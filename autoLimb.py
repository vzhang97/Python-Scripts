#--------------------------------------------------
#
# Created by Vincent Zhang
# Quadped Auto limb rig v1.0
#
#--------------------------------------------------

import maya.cmds as cmds

def autoLimbTool(*args):
	# Setup the variables which could come from the UI

	# Is this the front or rear leg from menu
	whichLeg = cmds.optionMenu("legMenu", q=1, v=1)

	if whichLeg == "Front":
		isRearleg = 0
	else:
		isRearleg = 1

	# Check the checkboxes
	rollCheck = cmds.checkBox("rollCheck", q=1, v=1)
	stretchCheck = cmds.checkBox("stretchCheck", q=1, v=1)


	#How many joints are we working with?
	limbJoints = 4

	# Use this information to start to generate the names we need
	if isRearleg:
		limbType = "Rear"
		print "Working on the Rear Leg"
	else:
		limbType = "Front"
		print "Working on the Front Leg"

	# Check the selection is valid
	selectionCheck  = cmds.ls(sl=1, typ="joint")

	# Error check to make sure a joint is selected
	if not selectionCheck:
		cmds.error("Please select the root joint.")
	else:
		jointRoot = cmds.ls(sl=1, typ="joint")[0]

	# Check prefix of joint root to determine the side
	whichSide = jointRoot[0:2]

	# Make sure the prefix is usable
	if not "L_" in whichSide:
		if not "R_" in whichSide:
			cmds.error("Please use a joint with a usable prefix of either L_ or R_")

	#Build the names
	limbName = whichSide + limbType + "Leg"

	mainControl = limbName + "_ctrl"
	pawControlName = limbName + "_IK_ctrl"
	kneeControlName = limbName + "_PV_ctrl"
	hockControlName = limbName + "_hock_ctrl"
	rootControl = limbName + "_root_ctrl"

	#----------------------------------------------------------------
	# Build the list of joints we are working with, using the root as a start point

	# Find its children
	jointHierarchy = cmds.listRelatives(jointRoot, ad=1, type="joint")

	# Add the selected joint into the front of the list
	jointHierarchy.append(jointRoot)
	jointHierarchy.reverse()

	# Clear the selection
	cmds.select(cl=1)

	#----------------------------------------------------------------
	# Duplicate the main joint chain and rename each joint

	# First define what joint chains we need
	newJointList = ["_IK", "_FK", "_stretch"]

	# Add the extra driver joints if this is the rear leg
	if isRearleg:
		newJointList.append("_driver")

	# Buld the joints
	for newJoint in newJointList:
		for i in range (limbJoints):
			newJointName = (jointHierarchy[i] + newJoint).replace("|","")

			cmds.joint(n=newJointName)
			cmds.matchTransform(newJointName, jointHierarchy[i])
			cmds.makeIdentity(newJointName, a=1, t=0, r=1, s=0)

		cmds.select(cl=1)

	#---------------------------------------------------------
	# Constraint the main joints to the IK and FK joints so we can blend between them
	for i in range (limbJoints):
		cmds.parentConstraint( (jointHierarchy[i] + "_IK"), (jointHierarchy[i] + "_FK"), (jointHierarchy[i]), w=1, mo=0 )

	#------------------------------------------------------
	# Set up FK

	# Connect the FK Controls to the new joints
	for i in range(limbJoints):
		cmds.parentConstraint( (jointHierarchy[i] + "_FK_ctrl"), (jointHierarchy[i] + "_FK"), w=1, mo=0 )

	#------------------------------------------------------
	# Set up IK

	IKSolver = {
		"SC": "ikSCsolver",
		"RP": "ikRPsolver",
		"SP": "ikSpringSolver"
	}

	whichSolver = cmds.optionMenu("ikSolverMenu", q=1, v=1)

	if whichSolver == "Rotate-Plane Solver":
		solver = "RP"
	else:
		solver = "SP"

	#If its the rear/back leg, create the IK Handle from the femur to the metacarpus
	if isRearleg:
		cmds.ikHandle( n=(limbName + "_driver_IKH"), sol=IKSolver[solver], sj=(jointHierarchy[0] + "_driver"), ee=(jointHierarchy[3] + "_driver") )

	#Next, create the main IK handle from the femur to the metatarsus
	cmds.ikHandle( n=(limbName + "_knee_IKH"), sol="ikRPsolver", sj=(jointHierarchy[0] + "_IK"), ee=(jointHierarchy[2] + "_IK") )

	#Finally create the hock IK handle, from the metatarsus to the metacarpus
	cmds.ikHandle( n=(limbName + "_hock_IKH"), sol="ikSCsolver", sj=(jointHierarchy[2] + "_IK"), ee=(jointHierarchy[3] + "_IK") )

	#Create the hock control offset group
	cmds.group( (limbName + "_knee_IKH"), n=(limbName + "_knee_ctrl"))
	cmds.group( (limbName + "_knee_ctrl"), n=(limbName + "_knee_ctrl_offset"))

	# Find the ankle pivot
	anklePivot = cmds.xform( jointHierarchy[3], q=1, ws=1, piv=1 )

	# Set the groups pivot to match the ankle position
	cmds.xform( ((limbName + "_knee_ctrl"), (limbName + "_knee_ctrl_offset")), ws=1, piv=(anklePivot[0], anklePivot[1], anklePivot[2]))

	# Parent the hock ik handle, the group offset to the paw control
	cmds.parent((limbName + "_hock_IKH"), pawControlName)

	# If its the rear leg, adjust the hierarchy so the driver leg controls the IK handles
	if isRearleg:
		cmds.parent( (limbName + "_knee_ctrl_offset"), (jointHierarchy[2] + "_driver") )
		cmds.parent( (limbName + "_hock_IKH"), (jointHierarchy[3] + "_driver") )

		cmds.parent( (limbName + "_driver_IKH"), pawControlName )
	else:
		cmds.parent((limbName + "_knee_ctrl_offset"), "Master_ctrl")
		cmds.pointConstraint(pawControlName, (limbName + "_knee_ctrl_offset"), w=1, mo=1)

	# Constraint the paw
	cmds.orientConstraint(pawControlName, (jointHierarchy[3] + "_IK"), w=1, mo=1)

	# Add the pole vector to the driver IK handle if its the rear leg, if its the front add it to the knee IK Handle
	if isRearleg:
		cmds.poleVectorConstraint(kneeControlName, (limbName + "_driver_IKH"), w=1)
	else:
		cmds.poleVectorConstraint(kneeControlName, (limbName + "_knee_IKH"), w=1)

	#-------------------------------------------------------
	# Add hock control

	# Check if its the front or rear leg
	if isRearleg:
		multiValue = 15
	else:
		multiValue = 15

	cmds.shadingNode("multiplyDivide", au=1, n=(limbName + "hock_multi") )

	cmds.connectAttr((hockControlName + ".translate"), (limbName + "hock_multi.input1"), f=1)
	cmds.connectAttr((limbName + "hock_multi.outputX"), (limbName + "_knee_ctrl.rotateX"), f=1)
	cmds.connectAttr((limbName + "hock_multi.outputY"), (limbName + "_knee_ctrl.rotateZ"), f=1)

	cmds.setAttr((limbName + "hock_multi.input2X"), multiValue)
	cmds.setAttr((limbName + "hock_multi.input2Y"), multiValue*-1)

	# Point constraint the hock offset group to follow the metatarsus
	#cmds.pointConstraint((limbName + "_knee_ctrl"), hockControlName + "_grp", w=1, mo=1)
	cmds.parentConstraint(jointHierarchy[2], (hockControlName + "_grp"), w=1, mo=1)

	#-------------------------------------------------------------
	# Add the IK and FK blending

	# Create blending attribute
	selected = cmds.select(mainControl)
	cmds.addAttr(sn = "IKFK_Switch", ln = "L_RearLeg_IKFK_Switch", nn="IK/FK Switch", at="float", min=0.0, max=1.0, k=1)
	cmds.select(cl=1)


	# Connect blending attribute to controls' visibility - FK (Default 0)
	cmds.connectAttr((mainControl + ".IKFK_Switch"), (jointHierarchy[0] + "_FK_ctrl_grp.visibility"))

	# Connect FK label visibility
	cmds.connectAttr((mainControl + ".IKFK_Switch"), (limbName + "_FK_Label_ctrl.visibility"))
	
	# FK (Default 1) - Reverse the value
	cmds.createNode("reverse", n=(limbName + "_IKFK_rev"))
	cmds.connectAttr((mainControl + ".IKFK_Switch"), (limbName + "_IKFK_rev.inputX"))
	cmds.connectAttr((limbName + "_IKFK_rev.outputX"), (limbName + "_IK_ctrl_grp.visibility"))

	# Connect IK label visibility
	cmds.connectAttr((limbName + "_IKFK_rev.outputX"), (limbName + "_IK_Label_ctrl.visibility"))


	for i in range(limbJoints):
		getConstraint = cmds.listConnections(jointHierarchy[i], type="parentConstraint", d=0)[0]
		getWeights = cmds.parentConstraint(getConstraint, q=1, wal=1)
		print getConstraint
		print getWeights



		cmds.connectAttr((mainControl + ".IKFK_Switch"), (getConstraint + "." + getWeights[1]), f=1)
		cmds.connectAttr((limbName + "_IKFK_rev.outputX"), (getConstraint + "." + getWeights[0]), f=1)


	#-----------------------------------------------------------
	# Update the hierarchy

	# Add a group for the limb
	cmds.group(em=1, n=(limbName + "_grp"))

	# Move it to the root position and freeze the transforms
	cmds.matchTransform((limbName + "_grp"), jointRoot)
	cmds.makeIdentity((limbName + "_grp"), a=1, t=1, r=1, s=0)

	# Parent the joints to the new group
	cmds.parent( (jointRoot + "_FK"), (jointRoot + "_IK"), (jointRoot + "_stretch"), (limbName + "_grp") )

	if isRearleg:
		cmds.parent( (jointRoot + "_driver"), (limbName + "_grp") )

	# Make the new group follow the root control
	cmds.parentConstraint( rootControl, (limbName + "_grp"), w=1, mo=1 )

	# Check if Rig_systems group exists
	rigSys = cmds.ls("Rig_systems")

	if rigSys is None:
		cmds.group(em=1, n=("Rig_systems"), w=1)

	cmds.select(cl=1)

	# Move the group to the rig systems folder
	cmds.parent((limbName + "_grp"), "Rig_systems")

	# Hide group contain the joint hierarchies
	cmds.setAttr((limbName + "_grp.visibility"), 0)

	#Clear selection
	cmds.select(cl=1)

	#------------------------------------------------------------
	# Make Stretchy limbs & squash


	if stretchCheck:
		#----------------------------------
		#Make stretchy limbs 

		# Create the locator with dictates the end position
		cmds.spaceLocator( n=(limbName + "_stretchEndPos_Loc") )
		cmds.matchTransform((limbName + "_stretchEndPos_Loc"), jointHierarchy[3])
		cmds.parent((limbName + "_stretchEndPos_Loc"), pawControlName)

		# Start to build the distance
		# First, we will need to add all the distance nodes together, so we need a plusMinusAverage node
		cmds.shadingNode("plusMinusAverage", au=1, n=(limbName + "_len"))

		# Buld the distance nodes for each section
		for i in range(limbJoints):

			# Ignore the last joint or it will try to use the toes
			if i is not limbJoints -1:
				cmds.shadingNode("distanceBetween", au=1, n=(jointHierarchy[i] + "_distNode"))

				cmds.connectAttr((jointHierarchy[i] + "_stretch.worldMatrix"), (jointHierarchy[i] + "_distNode.inMatrix1"), f=1) 
				cmds.connectAttr((jointHierarchy[i+1] + "_stretch.worldMatrix"), (jointHierarchy[i] + "_distNode.inMatrix2"), f=1)

				cmds.connectAttr((jointHierarchy[i] + "_stretch.rotatePivotTranslate"), (jointHierarchy[i] + "_distNode.point1"), f=1) 
				cmds.connectAttr((jointHierarchy[i+1] + "_stretch.rotatePivotTranslate"), (jointHierarchy[i] + "_distNode.point2"), f=1)

				cmds.connectAttr((jointHierarchy[i] + "_distNode.distance"), (limbName + "_len.input1D[" + str(i) + "]"), f=1)

		# Now get the distance from the root to the stretch end locator - we use this to check the leg is stretching
		cmds.shadingNode("distanceBetween", au=1, n=(limbName + "_stretch_distNode"))

		cmds.connectAttr((jointHierarchy[0] + "_stretch.worldMatrix"), (limbName + "_stretch_distNode.inMatrix1"), f=1) 
		cmds.connectAttr((limbName + "_stretchEndPos_Loc.worldMatrix"), (limbName + "_stretch_distNode.inMatrix2"), f=1)

		cmds.connectAttr((jointHierarchy[0] + "_stretch.rotatePivotTranslate"), (limbName + "_stretch_distNode.point1"), f=1) 
		cmds.connectAttr((limbName + "_stretchEndPos_Loc.rotatePivotTranslate"), (limbName + "_stretch_distNode.point2"), f=1)

		# Create nodes to check for stretching, and to control how the stretch works

		# Scale factor compares the length of the leg with the stretch locator, so we can see when the leg is actuall stretching
		cmds.shadingNode("multiplyDivide", au=1, n=(limbName + "_scaleFactor"))

		# We use the condition node to pass this onto the joints, so the leg only stretches the way we want it to
		cmds.shadingNode("condition", au=1, n=(limbName + "_stretch_cond"))

		# Adjust the node settings
		cmds.setAttr((limbName + "_scaleFactor.operation"), 2)

		cmds.setAttr((limbName + "_stretch_cond.operation"), 2)
		cmds.setAttr((limbName + "_stretch_cond.secondTerm"), 1)

		# Connect the stretch distance to the scale factor multiply divide node
		cmds.connectAttr((limbName + "_stretch_distNode.distance"), (limbName + "_scaleFactor.input1X"), f=1)

		# Connect the full length distance to the scale factor multiply divide node
		cmds.connectAttr((limbName + "_len.output1D"), (limbName + "_scaleFactor.input2X"), f=1)

		# Next, connect the stretch factor node to the first term in the condition node
		cmds.connectAttr((limbName + "_scaleFactor.outputX"), (limbName + "_stretch_cond.firstTerm"), f=1)

		# Also connect it to the color if true attribute, so we can use this as the stretch value
		cmds.connectAttr((limbName + "_scaleFactor.outputX"), (limbName + "_stretch_cond.colorIfTrueR"), f=1)

		# Now connect the stretch value to the ik and driver joints, so they stretch
		for i in range(limbJoints):
			cmds.connectAttr((limbName + "_stretch_cond.outColorR"), (jointHierarchy[i] + "_IK.scaleX"), f=1)
			
			if isRearleg:
				cmds.connectAttr((jointHierarchy[i] + "_IK.scaleX"), (jointHierarchy[i] + "_driver.scaleX"), f=1)


		# Add the ability to turn the stretchiness off
		cmds.shadingNode( "blendColors", au=1, n=(limbName + "_blendColors"))

		# Set the node correctly
		cmds.setAttr((limbName + "_blendColors.color2"), 1, 0, 0, type="double3")

		cmds.connectAttr( (limbName + "_scaleFactor.outputX"), (limbName + "_blendColors.color1R"), f=1)
		cmds.connectAttr( (limbName + "_blendColors.outputR"), (limbName + "_stretch_cond.colorIfTrueR"), f=1)

		# Create stretchiness float on the paw IK control
		cmds.addAttr(pawControlName, sn="stretchiness", ln=(limbName + "_stretchiness"), nn="Stretchiness", at="float", min=0.0, max=1.0, k=1)

		# Connect to the paw control attribute
		cmds.connectAttr( (pawControlName + ".stretchiness"), (limbName + "_blendColors.blender"), f=1)

		# Create stretchiness type (full, stretch only, squash only)
		cmds.addAttr(pawControlName, sn="stretchType", ln=(limbName + "_StretchType"), nn="Stretch Type", at="enum", en="Full:Stretch Only:Squash Only:", k=1)

		# Set up the type of stretch --- Full
		cmds.setAttr((pawControlName + ".stretchType"), 0)
		cmds.setAttr((limbName + "_stretch_cond.operation"), 1) # Not equal

		cmds.setDrivenKeyframe( (limbName + "_stretch_cond.operation"), cd=(pawControlName + ".stretchType"))

		#----- Stretch only
		cmds.setAttr((pawControlName + ".stretchType"), 1)
		cmds.setAttr((limbName + "_stretch_cond.operation"), 3) # Greater than

		cmds.setDrivenKeyframe( (limbName + "_stretch_cond.operation"), cd=(pawControlName + ".stretchType"))

		#----- Squash only
		cmds.setAttr((pawControlName + ".stretchType"), 2)
		cmds.setAttr((limbName + "_stretch_cond.operation"), 5) # Less or equal

		cmds.setDrivenKeyframe( (limbName + "_stretch_cond.operation"), cd=(pawControlName + ".stretchType"))

		# Reset stretch type
		cmds.setAttr((pawControlName + ".stretchType"), 1)

		#Clear selection
		cmds.select(cl=1)


		#------------------------------------------------------------
		# Make Squash limbs/Volume Preservation

		# Create multipleDivide node
		cmds.shadingNode("multiplyDivide", au=1, n=(limbName + "_volume_mult"))
		cmds.setAttr((limbName + "_volume_mult.operation"), 3) # Power operation

		# Connect the main stretch value to the volume node
		cmds.connectAttr( (limbName + "_blendColors.outputR"), (limbName + "_volume_mult.input1X"), f=1)

		# Connect the condition node so we can control scaling
		cmds.connectAttr( (limbName + "_volume_mult.outputX"), (limbName + "_stretch_cond.colorIfTrueG"), f=1)

		# Connect to the fibula joint
		cmds.connectAttr( (limbName + "_stretch_cond.outColorG"), (jointHierarchy[1] + ".scaleY"), f=1)
		cmds.connectAttr( (limbName + "_stretch_cond.outColorG"), (jointHierarchy[1] + ".scaleZ"), f=1)

		# Connect to the metatarsus joint
		cmds.connectAttr( (limbName + "_stretch_cond.outColorG"), (jointHierarchy[2] + ".scaleY"), f=1)
		cmds.connectAttr( (limbName + "_stretch_cond.outColorG"), (jointHierarchy[2] + ".scaleZ"), f=1)

		# Create volume attribute on main control
		cmds.addAttr(mainControl, sn = "volumeOffset", ln = (limbName + "VolumeOffset"), nn="Volume Offset", at="float", k=1, dv=0.5)

		# Connect to the main volume attribute
		cmds.connectAttr( (mainControl + ".volumeOffset"), (limbName + "_volume_mult.input2X"), f=1)


	#------------------------------------------------------------
	# Add Roll joints & Systems

	"""
	#Self made (made other tutorial)
	# Create roll joints for femur
	for i in range(3):

		if i == 0:
			rollJointName = jointHierarchy[0] + "_roll"
		elif i > 1: 
			rollJointName = jointHierarchy[0] + "_rollEnd"
		else:
			rollJointName = jointHierarchy[0] + "_roll01"


		if i > 0:
			cmds.select((jointHierarchy[0] + "_roll"))

		cmds.joint(n=rollJointName, rad=1.5)
		cmds.matchTransform(rollJointName, jointHierarchy[0])
		cmds.makeIdentity(rollJointName, a=1, t=0, r=1, s=0)

	cmds.select(cl=1)

	# Adjust rollEnd joint position
	cmds.matchTransform((jointHierarchy[0] + "_rollEnd"), jointHierarchy[1], pos=1)

	# Position middle roll joint
	tempConstraint = cmds.pointConstraint((jointHierarchy[0] + "_roll"), (jointHierarchy[0] + "_rollEnd"), (jointHierarchy[0] + "_roll01"), w=1, mo=0)
	cmds.delete(tempConstraint)

	# Create IK handle for roll joints
	cmds.ikHandle( n=(jointHierarchy[0] + "_roll_IKH"), sol="ikSCsolver", sj=(jointHierarchy[0] + "_roll"), ee=(jointHierarchy[0] + "_rollEnd") )

	# Point constraint IKH to Fibula
	cmds.pointConstraint( (jointHierarchy[1]), (jointHierarchy[0] + "_roll_IKH"), w=1, mo=0)

	# Add orient constraint for the middle roll joint
	cmds.orientConstraint( (jointHierarchy[0] + "_roll"), (jointHierarchy[0] + "_rollEnd"), (jointHierarchy[0] + "_roll01"), w=1, mo=1)

	# Add orient constraint for the end roll joint
	cmds.orientConstraint( jointHierarchy[0], jointHierarchy[0] + "_rollEnd")

	# Move to rig systems
	cmds.parent((jointHierarchy[0] + "_roll"), (jointHierarchy[0] + "_roll_IKH"), (limbName + "_grp"))

	cmds.select(cl=1)

	# Create roll joints for fibula
	for i in range(3):

		if i == 0:
			rollJointName = jointHierarchy[1] + "_roll"
		elif i > 1: 
			rollJointName = jointHierarchy[1] + "_rollEnd"
		else:
			rollJointName = jointHierarchy[1] + "_roll01"

		cmds.joint(n=rollJointName, rad=1.25)
		cmds.matchTransform(rollJointName, jointHierarchy[1])
		cmds.makeIdentity(rollJointName, a=1, t=0, r=1, s=0)
		cmds.select(cl=1)
		
	# Adjust start roll joint position
	cmds.matchTransform(jointHierarchy[1] + "_roll", jointHierarchy[2], pos=1)

	# Parent the rolls into hierarchy
	cmds.parent((jointHierarchy[1] + "_roll01"), (jointHierarchy[1] + "_rollEnd"), (jointHierarchy[1] + "_roll"))

	# Position middle roll joint
	tempConstraint = cmds.pointConstraint((jointHierarchy[1] + "_roll"), (jointHierarchy[1] + "_rollEnd"), (jointHierarchy[1] + "_roll01"), w=1, mo=0)
	cmds.delete(tempConstraint)

	# Create IK handle for roll joints
	cmds.ikHandle( n=(jointHierarchy[1] + "_roll_IKH"), sol="ikSCsolver", sj=(jointHierarchy[1] + "_roll"), ee=(jointHierarchy[1] + "_rollEnd") )

	# Point constraint IKH to Fibula
	cmds.pointConstraint( (jointHierarchy[1]), (jointHierarchy[1] + "_roll_IKH"), w=1, mo=0)

	# Add orient constraint for the middle roll joint
	cmds.orientConstraint( (jointHierarchy[1] + "_roll"), (jointHierarchy[1] + "_rollEnd"), (jointHierarchy[1] + "_roll01"), w=1, mo=1)

	# Add orient constraint for the end roll joint
	cmds.orientConstraint( jointHierarchy[1], jointHierarchy[1] + "_rollEnd")

	# 

	cmds.select(cl=1)
	"""




	#----------------------------------------------------------------
	#Video Tutorial Roll joints

	if rollCheck:
		# Check which side we are working on so we can move things to the correct side
		if whichSide == "L_":
			flipSide = 1
		else: 
			flipSide = -1
		
		# Create the main roll and follow joints
		rollJointList = [jointHierarchy[0], jointHierarchy[3], jointHierarchy[0], jointHierarchy[0]]

		for i in range(len(rollJointList)):

			# Setup the roll joints
			if i > 2:
				rollJointName = rollJointList[i] + "_followTip"
			elif i > 1:
				rollJointName = rollJointList[i] + "_follow"
			else:
				rollJointName = rollJointList[i] + "_roll"

			cmds.joint(n=rollJointName, rad=1.5)
			cmds.matchTransform(rollJointName, rollJointList[i])
			cmds.makeIdentity(rollJointName, a=1, t=0, r=1, s=0)

			if i < 2:
				cmds.parent(rollJointName, rollJointList[i])
			elif i > 2:
				cmds.parent(rollJointName, rollJointList[2] + "_follow") 

			cmds.select(cl=1)

			# Show the rotaional axes to help us visualise the rotation
			#cmds.toggle(rollJointName, la=1)

		#-----------------------------------
		# Upper leg system

		# Lets work on the femur first and adjust the follow joints
		cmds.pointConstraint(jointHierarchy[0], jointHierarchy[1], rollJointList[2] + "_followTip", w=1, mo=0, n="tempPC")
		cmds.delete("tempPC")

		# Now move them out
		cmds.move(0, 3*flipSide, 0, rollJointList[2] + "_follow", r=1, os=1, wd=1)

		# Create the aim locator which the femur roll joint will always follow
		cmds.spaceLocator(n=(rollJointList[0] + "_roll_aim"))

		# Move it to the root joint and parent it to the follow joint so it moves with it
		cmds.matchTransform((rollJointList[0] + "_roll_aim"), (rollJointList[2] + "_follow"))
		cmds.parent((rollJointList[0] + "_roll_aim"), (rollJointList[2] + "_follow"))

		# Move the locator out too
		cmds.move(0, 3*flipSide, 0, (rollJointList[0] + "_roll_aim"), r=1, os=1, wd=1)

		# Make the root joint aim at the fibula joint, but also keep looking at the aim locator for reference
		cmds.aimConstraint(jointHierarchy[1], (rollJointList[0] + "_roll"), w=1, aim=(1,0,0), u=(0,1,0), wut="object", wuo=(rollJointList[0] + "_roll_aim"), mo=1)

		# Add an IK handle so the follow joints follow the leg
		cmds.ikHandle( n=(jointHierarchy[0] + "_follow_IKH"), sol="ikRPsolver", sj=(jointHierarchy[0] + "_follow"), ee=(jointHierarchy[0] + "_followTip") )
		cmds.setAttr((jointHierarchy[0] + "_follow_IKH.visibility"), 0)


		# Now move it to the fibula and parent it
		cmds.parent((jointHierarchy[0] + "_follow_IKH"), jointHierarchy[1])
		cmds.matchTransform((jointHierarchy[0] + "_follow_IKH"), jointHierarchy[1])

		# Also reset the pole vector to stop the limb twisting
		cmds.setAttr((jointHierarchy[0] + "_follow_IKH.poleVectorX"),0)
		cmds.setAttr((jointHierarchy[0] + "_follow_IKH.poleVectorY"),0)
		cmds.setAttr((jointHierarchy[0] + "_follow_IKH.poleVectorZ"),0)
		
		#----------------------------------

		# Lower leg system

		# Create the aim locator which the metacarpus roll joint will always follow
		cmds.spaceLocator(n=(rollJointList[1] + "_roll_aim"))
		cmds.setAttr((rollJointList[1] + "_roll_aim.visibility"), 0)

		# Move it to the ankle joint and parent it to the ankle joint
		cmds.matchTransform((rollJointList[1] + "_roll_aim"), (rollJointList[1] + "_roll"))
		cmds.parent((rollJointList[1] + "_roll_aim"), jointHierarchy[3])
		
		# Also move it out to the side
		cmds.move(0, 3*flipSide, 0, (rollJointList[1] + "_roll_aim"), r=1, os=1, wd=1)
		
		# Make the ankle joint aim at the metatarsus joint, but also keep looking at the aim locator for reference
		cmds.aimConstraint(jointHierarchy[2], (rollJointList[1] + "_roll"), w=1, aim=(1,0,0), u=(0,1,0), wut="object", wuo=(rollJointList[1] + "_roll_aim"), mo=1)

		# Update the hierarchy, parenting the follow joints to the main group
		cmds.parent( (rollJointList[0] + "_follow"), (limbName + "_grp"))

		cmds.select(cl=1)


	

def autoLimbToolUI():

	# First we check if the window exists and if it does, delete it
	if cmds.window("autoLimbToolUI", ex=1): cmds.deleteUI("autoLimbToolUI")

	# Create the window
	window = cmds.window("autoLimbToolUI", t="Auto Limb Tool v1.0", w=200, h=200, mnb=0, mxb=0)

	# Create the main layout
	mainLayout = cmds.formLayout(nd=100)

	# Leg menu
	legMenu = cmds.optionMenu("legMenu", l="Which Leg?", h=20, ann="Which side are we working on?")

	cmds.menuItem(l="Front")
	cmds.menuItem(l="Rear")

	ikSolverMenu = cmds.optionMenu("ikSolverMenu", l="IK Solver", h=20, ann="Select IK Solver for the main joints")

	cmds.menuItem(l="Rotate-Plane Solver", ann="Rotate-Plane Solver, ideal if need stretchy limbs as it is more stable")
	cmds.menuItem(l="Spring Solver", ann="Spring Solver, better leg movement but does not work well with stretchy limbs")

	# Checkboxes
	rollCheck = cmds.checkBox("rollCheck", l="Roll joints", h=20, ann="Add Roll Joints?", v=0)
	stretchCheck = cmds.checkBox("stretchCheck", l="Stretchy", h=20, ann="Stretchy Limbs?", v=0)

	# Separators
	separator01 = cmds.separator(h=5)
	separator02 = cmds.separator(h=5)
	separator03 = cmds.separator(h=5)

	# Buttons
	button = cmds.button(l="[GO]", c=autoLimbTool)

	# Adjust layout
	cmds.formLayout(mainLayout, e=1,
					attachForm = [(legMenu, 'top', 5), (legMenu, 'left', 5), (legMenu, 'right', 5),

								  (ikSolverMenu, 'left', 5), (ikSolverMenu, 'right', 5),

								  (separator01, 'left', 5), (separator01, 'right', 5),
								  (separator02, 'left', 5), (separator02, 'right', 5),
								  (separator03, 'left', 5), (separator03, 'right', 5),

								  (button, 'bottom', 5), (button, 'left', 5), (button, 'right', 5)


					],

					attachControl = [(separator01, 'top', 5, legMenu),
									 (ikSolverMenu, 'top', 5, separator01),
									 (separator02, 'top', 5, ikSolverMenu),
								     (rollCheck, 'top', 5, separator02),
								     (stretchCheck, 'top', 5, separator02),

								     (separator03, 'top', 5, rollCheck),
								     (button, 'top', 5, separator03)



					],

					# last input, based on number of divisions of the form (100 or 100%)
					attachPosition = [(rollCheck, 'left', 0, 15),
									  (stretchCheck, 'right', 0, 85),



					]



	)


	# Show the window
	cmds.showWindow(window)

