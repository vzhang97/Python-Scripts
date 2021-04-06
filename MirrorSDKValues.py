#Limitations: 
#Left to Right
#Only connecting, does not create the controllers (yet)
#No mirroring axis?

import maya.cmds as cmds

selected = cmds.ls(sl=True)

object1 = selected[0] #Copy from
object2 = selected[1] #Paste into

animCurve = cmds.listConnections(object1, scn=True, et=True, t='animCurveUL')
animCurveList = cmds.listConnections(animCurve, scn=True, et=True, t='transform', p=True)
driver = cmds.listConnections(animCurve, scn=True, d=False)

inAttribute = (animCurveList[0].split('.'))[1]
outAttribute = (animCurveList[1].split('.'))[1]

mirrorAnimCurve = cmds.duplicate(animCurve, n=animCurve[0].replace('L', 'R'))
mirrorDriver = cmds.ls(driver[0].replace('L', 'R'))

cmds.connectAttr('%s.' % mirrorDriver[0] + outAttribute, '%s.input' % mirrorAnimCurve[0], f=True)  
cmds.connectAttr('%s.output' % mirrorAnimCurve[0], '%s.' % object2 + inAttribute, f=True)  
