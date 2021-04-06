##############################################################################
#    Description:                                                            #
#        Create control stack for selection of joints/transforms             #
#        Allow multiple joints/transforms as well as in hierarchies          #        
#                                                                            #
#    Function:                                                               #
#        Select hierarchy from child to parent (ascending order)             #
#        Iterates list of selected objects (joints/transforms)               #
#        in ascending hierarchy order                                        #
#        Creates the control stacks                                          #
#        Checks if object has a child; parent the child's stack to object    #
#                                                                            #
#    Author:                                                                 #
#        Vincent Zhang                                                       #
#                                                                            #
#    Version:                                                                #
#        1.00 - 21/01/2021                                                   #
#                                                                            #
##############################################################################

import maya.cmds as cmds

objects = cmds.ls(sl=True)

obj_child_homenul = None #Homenul of object's child
obj_child = None #Object's child

for object in objects:
    
    #Create the stack
    spacenul = cmds.group(n=object+"_ctrl_grp", em=True)
    

    #Create the controller with X-axis as its normal direction
    object_ctrl = cmds.circle(name=(object+"_ctrl"), nr=(1,0,0), r=10)


    #Rearrange group
    cmds.parent(object_ctrl[0], spacenul)


    #Move the group to joint's location#
    temp = cmds.parentConstraint(object, spacenul, mo=False)
    cmds.delete(temp)
    
    #Check if current_object has a child 
    #Parent the child's stack to the current_object's controller
    obj_child = cmds.listRelatives(object, typ=['joint', 'transform'], c=True)
    

    #Constraint the controller to the object
    pc = cmds.parentConstraint(object_ctrl, object, mo=False)
    
    
    if obj_child is not None:
        cmds.parent(child_stack, object_ctrl[0])

    #Create reference for future parenting#
    child_stack = spacenul 


cmds.select(cl=True)
obj_child = None
child_stack = None
spacenl = None