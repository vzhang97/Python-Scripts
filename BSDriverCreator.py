import maya.cmds as cmds

BS_Attribute = 'L_LipsLowerCorner'
driverAttr = 'y'
dv = -1.0

controller = cmds.ls(sl=True)
controllerClean = controller[0].replace("_ctrl", "")

cmds.addAttr(sn='Multi', nn='Multi', ln='%s_BS_multi' % controller[0], defaultValue=dv, 
             k=True)

multiNode = cmds.createNode( 'multiplyDivide', n='%s_multi' % controller[0].replace("_ctrl", ""))

cmds.connectAttr('%s.t' % controller[0] + driverAttr, '%s.input 1X' % multiNode)
cmds.connectAttr('%s.Multi' % controller[0], '%s.input 2X' % multiNode)
cmds.connectAttr('%s.outputX' % multiNode, 'BS_Head.' + BS_Attribute)