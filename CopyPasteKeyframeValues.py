##############################################################################
#    Description:                                                            #
#        Copies the keyframe values of the first selected object into        #
#        the subsequent object's keyframe values                             #
#                                                                            #
#	 Main use: copy paste SDK values                                     #       
#                                                                            #
#    Function:                                                               #
#        Select first object which you want to copy its keyframe values      #
#        Select the rest of the object which we want to paste the values     #
#	 Variables to edit according to which attribute                      #
#	 or key you want to copy over                                        #
#									     #
#    Author:                                                                 #
#        Vincent Zhang                                                       #
#                                                                            #
#    Version:                                                                #
#        1.00 - 16/02/2021                                                   #
#                                                                            #
##############################################################################



#Copy first selected object's keyframe values (index/float, value) into the rest of the select objects

import maya.cmds as cmds

objects = cmds.ls(sl=True)

primary = objects[0]

objects.pop(0)

#Variables of keyframe we want to copy
#Must depending on use
##################################
attribute = '.translateY'
fi = 1 #FloatIndex 
##################################

floatToCopy = cmds.keyframe(primary+attribute, index=(fi,fi), fc=True, query=True) #X-axis value
valueToCopy = cmds.keyframe(primary+attribute, index=(fi,fi), absolute=True, vc=True ,query=True) #Y-axis value


print(valueToCopy)
print(floatToCopy)


for object in objects:
    cmds.keyframe(object+attribute, edit=True, index=(fi,fi), absolute=True, fc=floatToCopy[0])
    cmds.keyframe(object+attribute, edit=True, index=(fi,fi), absolute=True, vc=valueToCopy[0])
    

