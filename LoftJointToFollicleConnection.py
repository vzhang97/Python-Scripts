import maya.cmds as cmds

loft = None
joint = None
follicle = None
prefix = 'C_SpineRail_'

selected = cmds.ls(sl=True)

for object in selected:
    print(cmds.listRelatives(object))

for object in selected:
    if cmds.objectType(object, isType='joint') == True:
        joint = object
    elif cmds.objectType(cmds.listRelatives(object)[0], 
         isType='nurbsSurface') == True:
        loft = object
    else:
        follicle = object
        
follicleNN = follicle.strip(prefix)
print(follicleNN)

cps = cmds.createNode('closestPointOnSurface', n='closestPointOnSurface_' + joint)
dm = cmds.createNode('decomposeMatrix', n='decomposeMatrix_' + follicleNN)

cmds.connectAttr('%s.worldSpace[0]' % loft, '%s.inputSurface' % cps)
cmds.connectAttr('%s.worldMatrix[0]' % joint, '%s.inputMatrix' % dm)
cmds.connectAttr('%s.outputTranslate' % dm, '%s.inPosition' % cps)

cmds.connectAttr('%s.parameterU' % cps, '%s.parameterU' % follicle)
cmds.connectAttr('%s.parameterV' % cps, '%s.parameterV' % follicle)