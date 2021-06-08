import maya.cmds as cmds

# Select all props + ctrl
selected = cmds.ls(sl=1)

# List of props
props = []

# Append selected items into list
for x in selected:
	props.append(x)
	print x

# Ctrl name
ctrl = ""

# Prefix
prefix = ""

# Get curve
for x in selected:
	children = cmds.listRelatives(x)

	if cmds.objectType(children, isType="nurbsCurve"):
		ctrl = x


# Remove curve from prop list
props.remove(ctrl)


# Obtain prefix of props
for i in range(len(props[0])):
    if False in [props[0][:i] == j[:i] for j in props]:
        #print(props[0][:i-1])
        prefix += props[0][:i-1]
        break


# Create enum list 
enumList = ""

# Added none prop to list
props.append("None")

# Create new list of props with simplified names
cleanProps = []

#Simplify prop name 
for prop in props:
	prop = prop.replace(prefix, "") #Removes prefix
	prop = prop.split("_", 1)[0]	#Removes suffix based on the underscore

	enumList += prop + ":" #Add into enumList
	cleanProps.append(prop) #Append into clean list


# Create attr on ctrl with the enumList
cmds.addAttr(ctrl, sn="prop_name", ln="prop_name", nn="Prop Name", at="enum", en=enumList, k=1)


# Iterate over the props and connect the appropriate attributes
for i in range(len(cleanProps) - 1):
	cmds.createNode("condition", n=(ctrl + "_" + cleanProps[i] + "_cond"))
	cmds.setAttr((ctrl + "_" + cleanProps[i] + "_cond.colorIfTrueR"), 1) #True is 1
	cmds.setAttr((ctrl + "_" + cleanProps[i] + "_cond.colorIfFalseR"), 0) #False is 0
	cmds.setAttr((ctrl + "_" + cleanProps[i] + "_cond.secondTerm"), i) #Second term is based on idex on prop in list
	cmds.connectAttr((ctrl + ".prop_name"), (ctrl + "_" + cleanProps[i] + "_cond.firstTerm"))
	cmds.connectAttr((ctrl + "_" + cleanProps[i] + "_cond.outColor.outColorR"), (props[i] + ".visibility"))

