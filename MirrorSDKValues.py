#Limitations: 
#Left to Right
#Only connecting, does not create the controllers (yet)
#No mirroring axis?
#Select the driven object/node

import maya.cmds as cmds

selected = cmds.ls(sl=True)


object1 = selected[0] #Copy from
object2 = selected[1] #Paste into

animCurve = cmds.listConnections(object1, scn=True, et=True, t='animCurveUA')
animCurveList = cmds.listConnections(animCurve, scn=True, et=True, t='transform', p=True)
driver = cmds.listConnections(animCurve, scn=True, d=False)
print animCurve 
print animCurveList
print driver

inAttribute = (animCurveList[0].split('.'))[1]
outAttribute = (animCurveList[1].split('.'))[1]

print inAttribute
print outAttribute

if "L_" in inAttribute:
	inAttribute = inAttribute.replace("L_", "R_")

if "L_" in outAttribute:
	outAttribute = outAttribute.replace("L_", "R_")


print inAttribute
print outAttribute

mirrorAnimCurve = cmds.duplicate(animCurve, n=animCurve[0].replace('L', 'R'))
mirrorDriver = cmds.ls(driver[0].replace('L', 'R'))

cmds.connectAttr('%s.' % mirrorDriver[0] + outAttribute, '%s.input' % mirrorAnimCurve[0], f=True)  
cmds.connectAttr('%s.output' % mirrorAnimCurve[0], '%s.' % object2 + inAttribute, f=True)  
  