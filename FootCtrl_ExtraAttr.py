# Vincent Zhang
# v1.0
# 27/04/2021

# Creates the foot reverse movements such as bank, twist, tap and roll
# Works for both sides of the leg
# Need to Select the foot control, hosting the reverse foot joints


import maya.cmds as cmds


footCtrl =  cmds.ls(sl=1)

side = footCtrl[0].split("_")[0]

joints = cmds.listRelatives(footCtrl[0], ad=1, typ="joint")


#-------------------------------
# Create Foot ctrl attributes

# Extra Attribute Disp
cmds.addAttr(ln=(side + "_Foot_Controls"), nn=(side + " Foot Controls"), at="enum", en="--------", k=1)
cmds.setAttr((footCtrl[0] + "." + side + "_Foot_Controls"), lock=1)

# Foot Bank
cmds.addAttr(ln=(side + "_Foot_Bank"), nn=("Foot Bank"), at="double", dv=0, k=1)

# Foot Heel Twist
cmds.addAttr(ln=(side + "_Foot_Heel_Twist"), nn=("Foot Heel Twist"), at="double", dv=0, k=1)

# Foot Toe Twist
cmds.addAttr(ln=(side + "_Foot_Toe_Twist"), nn=("Foot Toe Twist"), at="double", dv=0, k=1)

# Foot Toe Tap
cmds.addAttr(ln=(side + "_Foot_Toe_Tap"), nn=("Foot Toe Tap"), at="double", dv=0, k=1)

# Foot Roll
cmds.addAttr(ln=(side + "_Foot_Roll"), nn=("Foot Roll"), at="double", min=-10, max=10, dv=0, k=1)

# Extra Attribute Disp - Foot Multipliers
cmds.addAttr(ln=(side + "_Foot_Multipliers"), nn=(side + " Foot Multipliers"), at="enum", en="--------", k=1)
cmds.setAttr((footCtrl[0] + "." + side + "_Foot_Multipliers"), lock=1)


#---------------------------------
# Foot Bank

CBank = ""
EBank = ""

for i, x in enumerate(joints):
	if "CBank" in x:
		CBank = x
	elif "EBank" in x:
		EBank = x 

	
# Create Condition Node
cmds.createNode("condition", name=(side + "_Foot_Bank_cond"), ss=1)
cmds.setAttr((side + "_Foot_Bank_cond" + ".operation"), 3)
cmds.setAttr((side + "_Foot_Bank_cond" + ".colorIfFalseR"), 0)
cmds.setAttr((side + "_Foot_Bank_cond" + ".colorIfTrueG"), 0)

# Connect condition node
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Bank"), (side + "_Foot_Bank_cond") + ".firstTerm")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Bank"), (side + "_Foot_Bank_cond") + ".colorIfTrueR")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Bank"), (side + "_Foot_Bank_cond") + ".colorIfFalseG")

cmds.connectAttr((side + "_Foot_Bank_cond") + ".outColorR", CBank + ".rotateX")
cmds.connectAttr((side + "_Foot_Bank_cond") + ".outColorG", EBank + ".rotateX")



#----------------------------
# Foot Heel Twist

Heel = ""

for x in joints:
	if "Heel" in x:
		Heel = x

if Heel == "":
	cmds.error("No Heel joint")

# Add Multiplier attribute
cmds.addAttr(ln=(side + "_Foot_Heel_Twist_mult"), nn=("Foot Heel Twist Mult"), at="double", dv=-1, k=1)

# Create Multiply Node to reverse value
cmds.createNode("multiplyDivide", name=(side + "_Foot_Heel_Twist_mult"), ss=1)

# Connect multiply node
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Heel_Twist"), (side + "_Foot_Heel_Twist_mult") + ".input1X")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Heel_Twist_mult"), (side + "_Foot_Heel_Twist_mult") + ".input2X")

cmds.connectAttr((side + "_Foot_Heel_Twist_mult") + ".outputX", Heel + ".rotateZ")



#----------------------------
# Foot Toe Twist

Toe = ""

for x in joints:
	if "Toe" in x:
		Toe = x

if Toe == "":
	cmds.error("No Toe joint")

# Add Multiplier attribute
cmds.addAttr(ln=(side + "_Foot_Toe_Twist_mult"), nn=("Foot Toe Twist Mult"), at="double", dv=-1, k=1)

# Create Multiply Node to reverse value
cmds.createNode("multiplyDivide", name=(side + "_Foot_Toe_Twist_mult"), ss=1)

# Connect multiply node
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Toe_Twist"), (side + "_Foot_Toe_Twist_mult") + ".input1X")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Toe_Twist_mult"), (side + "_Foot_Toe_Twist_mult") + ".input2X")

cmds.connectAttr((side + "_Foot_Toe_Twist_mult") + ".outputX", Toe + ".rotateZ")



#----------------------------
# Foot Toe Tap

Ball = ""

for x in cmds.listRelatives(footCtrl[0], ad=1):
	if "Ball" in x and "offset" in x:
		Ball = x

if Ball == "":
	cmds.error("Could not find the offset group needed for the Toe Tap")

# Add Multiplier attribute
cmds.addAttr(ln=(side + "_Foot_Toe_Tap_mult"), nn=("Foot Toe Tap Mult"), at="double", dv=-1, k=1)

# Create Multiply Node to reverse value
cmds.createNode("multiplyDivide", name=(side + "_Foot_Toe_Tap_mult"), ss=1)

# Connect multiply node
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Toe_Tap"), (side + "_Foot_Toe_Tap_mult") + ".input1X")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Toe_Tap_mult"), (side + "_Foot_Toe_Tap_mult") + ".input2X")

cmds.connectAttr((side + "_Foot_Toe_Tap_mult") + ".outputX", Ball + ".rotateY")



#-----------------------------------
# Foot Roll

# Reset Ball variable to the Ball joint, not the offset group
Ball = ""

for x in cmds.listRelatives(footCtrl[0], ad=1, type="joint"):
	if "Ball" in x:
		Ball = x

if Ball == "":
	cmds.error("No Ball Joint")


# Add Multiplier attribute
cmds.addAttr(ln=(side + "_Foot_Heel_Roll_mult"), nn=("Foot Heel Roll Mult"), at="double", dv=5, k=1)
cmds.addAttr(ln=(side + "_Foot_Ball_Roll_mult"), nn=("Foot Ball Roll Mult"), at="double", dv=5, k=1)
cmds.addAttr(ln=(side + "_Foot_Toe_Roll_mult"), nn=("Foot Toe Roll Mult"), at="double", dv=5, k=1)


# Create 1 multiplier node for all 3 joints
cmds.createNode("multiplyDivide", name=(side + "_Foot_Roll_mult"), ss=1)

# Connect the multiplier attributes to multipler
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Roll"), side + "_Foot_Roll_mult" + ".input1X")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Roll"), side + "_Foot_Roll_mult" + ".input1Y")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Roll"), side + "_Foot_Roll_mult" + ".input1Z")

cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Heel_Roll_mult"), side + "_Foot_Roll_mult" + ".input2X")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Ball_Roll_mult"), side + "_Foot_Roll_mult" + ".input2Y")
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Toe_Roll_mult"), side + "_Foot_Roll_mult" + ".input2Z")


# Heel --------------------------
# Create Condition Node
cmds.createNode("condition", name=(side + "_Foot_Heel_Roll_cond"), ss=1)
cmds.setAttr((side + "_Foot_Heel_Roll_cond.colorIfTrueR"), 0)
cmds.setAttr((side + "_Foot_Heel_Roll_cond.operation"), 3)

# Connect
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Roll"), (side + "_Foot_Heel_Roll_cond") + ".firstTerm")
cmds.connectAttr(side + "_Foot_Roll_mult" + ".outputX", (side + "_Foot_Heel_Roll_cond") + ".colorIfFalseR")

cmds.connectAttr((side + "_Foot_Heel_Roll_cond") + ".outColorR", Heel + ".rotateY")


# Ball -------------------------
# Create Condition Node 1 - Checks when Roll is Negative
cmds.createNode("condition", name=(side + "_Foot_Ball_Roll_cond01"), ss=1)
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Roll"), (side + "_Foot_Ball_Roll_cond01") + ".firstTerm")
cmds.setAttr((side + "_Foot_Ball_Roll_cond01.secondTerm"), 0) #Check for negative values (no movement)
cmds.setAttr((side + "_Foot_Ball_Roll_cond01.operation"), 5) #Less or equal to 0
cmds.setAttr((side + "_Foot_Ball_Roll_cond01.colorIfTrueR"), 0) #If true, keep at 0

cmds.connectAttr(side + "_Foot_Roll_mult" + ".outputY", (side + "_Foot_Ball_Roll_cond01") + ".colorIfFalseR")


# Create Condition Node 2 - Checks when roll is positive, below 5 (Mid point for ball and toe rotation)
cmds.createNode("condition", name=(side + "_Foot_Ball_Roll_cond02"), ss=1)
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Roll"), (side + "_Foot_Ball_Roll_cond02") + ".firstTerm")
cmds.setAttr((side + "_Foot_Ball_Roll_cond02.secondTerm"), 5) #Check for value below 5, ball can rotate
cmds.setAttr((side + "_Foot_Ball_Roll_cond02.operation"), 5) #Less or equal to 5

# Create Multiplier Node - Max value ball can rotate. Equals to 5 (midpoint) x ball roll multiplier
cmds.createNode("multiplyDivide", name=(side + "_Foot_Ball_MaxRoll_mult"), ss=1)
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Ball_Roll_mult"), (side + "_Foot_Ball_MaxRoll_mult" + ".input1X"))
cmds.setAttr((side + "_Foot_Ball_MaxRoll_mult" + ".input2X"), 5) #Set 5 as mid point


# Connect Condition01 and Multipler to Condition02
cmds.connectAttr((side + "_Foot_Ball_Roll_cond01") + ".outColorR", (side + "_Foot_Ball_Roll_cond02") + ".colorIfTrueR")
cmds.connectAttr((side + "_Foot_Ball_MaxRoll_mult") + ".outputX", (side + "_Foot_Ball_Roll_cond02") + ".colorIfFalseR")

# Connect Condition02 to Ball joint
cmds.connectAttr((side + "_Foot_Ball_Roll_cond02") + ".outColorR", Ball + ".rotateY")


# Toe ---------------------
# Create plusMinusAverage node to offset the rotation past the midpoint value of 5
cmds.createNode("plusMinusAverage", name=(side + "_Foot_Toe_Roll_offset_substract"), ss=1)
cmds.setAttr((side + "_Foot_Toe_Roll_offset_substract") + ".operation", 2)

# Calculate the offset value: Midpoint 5 x Toe roll multiplier
cmds.createNode("multiplyDivide", name=(side + "_Foot_Toe_Roll_offset_mult"), ss=1)

cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Toe_Roll_mult"), (side + "_Foot_Toe_Roll_offset_mult") + ".input1X")
cmds.setAttr((side + "_Foot_Toe_Roll_offset_mult") + ".input2X", 5) #Mid point value of 5

# Connect Main Roll Multi to plusMinusAverage
cmds.connectAttr((side + "_Foot_Roll_mult") + ".outputZ", (side + "_Foot_Toe_Roll_offset_substract") + ".input1D[" + str(0) + "]")
cmds.connectAttr((side + "_Foot_Toe_Roll_offset_mult") + ".outputX", (side + "_Foot_Toe_Roll_offset_substract") + ".input1D[" + str(1) + "]")

# Create Conditon Node
cmds.createNode("condition", name=(side + "_Foot_Toe_Roll_cond"), ss=1)
cmds.setAttr((side + "_Foot_Toe_Roll_cond") + ".operation", 3) # Greater than 
cmds.setAttr((side + "_Foot_Toe_Roll_cond") + ".secondTerm", 5) # Greater than 5 (toe rotation)
cmds.setAttr((side + "_Foot_Toe_Roll_cond") + ".colorIfFalseR", 0) # Greater than 5 (toe rotation)

# Connect condition node
cmds.connectAttr(footCtrl[0] + "." + (side + "_Foot_Roll"), (side + "_Foot_Toe_Roll_cond") + ".firstTerm")
cmds.connectAttr((side + "_Foot_Toe_Roll_offset_substract") + ".output1D", (side + "_Foot_Toe_Roll_cond") + ".colorIfTrueR")

# Final output to joint
cmds.connectAttr((side + "_Foot_Toe_Roll_cond") + ".outColorR", Toe + ".rotateY")

print "Successful!"
