# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

"""
This file contains the classes for CellBlender's Surface Regions.

"""

import cellblender

# blender imports
import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, \
                      FloatProperty, FloatVectorProperty, IntProperty, \
                      IntVectorProperty, PointerProperty, StringProperty

# blender imports
import bpy
from bpy.app.handlers import persistent
from bl_operators.presets import AddPresetBase
import mathutils

# python imports
import array
import glob
import os
import random
import re
import subprocess
import time
import shutil
import datetime

import sys, traceback


#from bpy.app.handlers import persistent
#import math
#import mathutils


# CellBlender imports
import cellblender
from . import parameter_system
from . import cellblender_preferences
from . import cellblender_release
from . import cellblender_objects
from . import cellblender_utils

# import cellblender.data_model
# import cellblender_source_info
from . import cellblender_utils
#from cellblender.cellblender_utils import project_files_path
from cellblender.cellblender_utils import project_files_path
from cellblender.io_mesh_mcell_mdl import export_mcell_mdl

# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)



# Surface Regions callback functions


def check_mod_surf_regions(self, context):
    """Make sure the surface class name is valid and format the list entry"""
    print ( "  Checking the mod_surf_region for " + str(self) )

    mcell = context.scene.mcell
    obj_list = mcell.model_objects.object_list
    surf_class_list = mcell.surface_classes.surf_class_list
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = self
    surf_class_name = active_mod_surf_regions.surf_class_name
    object_name = active_mod_surf_regions.object_name
    region_name = active_mod_surf_regions.region_name

    region_list = []

    # At some point during the building of properties the object name is "" which causes problems. So skip it for now.
    if len(object_name) > 0:
        try:
            region_list = bpy.data.objects[object_name].mcell.regions.region_list
        except KeyError as kerr:
            # The object name in mod_surf_regions isn't a blender object - print a stack trace ...
            print ( "Error: The object name (\"" + object_name + "\") isn't a blender object ... at this time?" )
            fail_error = sys.exc_info()
            print ( "    Error Type: " + str(fail_error[0]) )
            print ( "    Error Value: " + str(fail_error[1]) )
            tb = fail_error[2]
            # tb.print_stack()
            print ( "=== Traceback Start ===" )
            traceback.print_tb(tb)
            traceback.print_stack()
            print ( "=== Traceback End ===" )
            pass


    # Format the entry as it will appear in the Modify Surface Regions
    active_mod_surf_regions.name = ("Surface Class: %s   Object: %s   "
                                    "Region: %s" % (
                                        surf_class_name, object_name,
                                        region_name))

    status = ""

    # Make sure the user entered surf class is in Defined Surface Classes list
    if not surf_class_name in surf_class_list:
        status = "Undefined surface class: %s" % surf_class_name
    # Make sure the user entered object name is in the Model Objects list
    elif not active_mod_surf_regions.object_name in obj_list:
        status = "Undefined object: %s" % active_mod_surf_regions.object_name
    # Make sure the user entered object name is in the object's
    # Surface Region list
    elif not region_name in region_list:
        status = "Undefined region: %s" % region_name

    active_mod_surf_regions.status = status

    return


def check_active_mod_surf_regions(self, context):
    """This calls check_mod_surf_regions on the active mod_surf_regions"""

    mcell = context.scene.mcell
    mod_surf_regions = mcell.mod_surf_regions
    active_mod_surf_regions = mod_surf_regions.mod_surf_regions_list[
        mod_surf_regions.active_mod_surf_regions_index]
    # This is a round-about way to call "check_mod_surf_regions" above
    # Maybe these functions belong in the MCellModSurfRegionsProperty class
    # Leave them here for now to not disturb too much code at once

    ######  commented out temporarily (causes names to not be built):
    active_mod_surf_regions.check_properties_after_building(context)
    # The previous line appears to cause the following problem:
    """
        Done removing all MCell Properties.
        Overwriting properites based on data in the data model dictionary
        Overwriting the parameter_system properties
        Parameter System building Properties from Data Model ...
        Overwriting the initialization properties
        Overwriting the define_molecules properties
        Overwriting the define_reactions properties
        Overwriting the release_sites properties
        Overwriting the define_release_patterns properties
        Overwriting the define_surface_classes properties
        Overwriting the modify_surface_regions properties
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: top")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: top")>
        Error: The object name ("") isn't a blender object
            Error Type: <class 'KeyError'>
            Error Value: 'bpy_prop_collection[key]: key "" not found'
        === Traceback Start ===
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 842, in check_mod_surf_regions
            region_list = bpy.data.objects[active_mod_surf_regions.object_name].mcell.regions.region_list
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 78, in execute
            data_model.upgrade_properties_from_data_model ( context )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/data_model.py", line 298, in upgrade_properties_from_data_model
            mcell.build_properties_from_data_model ( context, dm )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 4986, in build_properties_from_data_model
            self.mod_surf_regions.build_properties_from_data_model ( context, dm["modify_surface_regions"] )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 2755, in build_properties_from_data_model
            sr.build_properties_from_data_model ( context, s )
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 774, in build_properties_from_data_model
            self.surf_class_name = dm["surf_class_name"]
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 892, in check_active_mod_surf_regions
            active_mod_surf_regions.check_properties_after_building(context)
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_properties.py", line 780, in check_properties_after_building
            check_mod_surf_regions(self, context)
          File "/home/user/.config/blender/2.74/scripts/addons/cellblender/cellblender_operators.py", line 853, in check_mod_surf_regions
            traceback.print_stack()
        === Traceback End ===
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object:    Region: ")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object:    Region: ")>
        Implementing check_properties_after_building for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: ")>
          Checking the mod_surf_region for <bpy_struct, MCellModSurfRegionsProperty("Surface Class: Surface_Class   Object: Cube   Region: ")>
        Overwriting the model_objects properties
        Data model contains Cube
        Overwriting the viz_output properties
        Overwriting the mol_viz properties
    """
    return



# Surface Regions Operators:


class MCELL_OT_mod_surf_regions_add(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_add"
    bl_label = "Assign Surface Class"
    bl_description = "Assign a surface class to a surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.add()
        mod_surf_regions.active_mod_surf_regions_index = len(
            mod_surf_regions.mod_surf_regions_list) - 1
        check_active_mod_surf_regions(self, context)

        return {'FINISHED'}


class MCELL_OT_mod_surf_regions_remove(bpy.types.Operator):
    bl_idname = "mcell.mod_surf_regions_remove"
    bl_label = "Remove Surface Class Assignment"
    bl_description = "Remove a surface class assignment from a surface region"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mod_surf_regions = context.scene.mcell.mod_surf_regions
        mod_surf_regions.mod_surf_regions_list.remove(
            mod_surf_regions.active_mod_surf_regions_index)
        mod_surf_regions.active_mod_surf_regions_index -= 1
        if (mod_surf_regions.active_mod_surf_regions_index < 0):
            mod_surf_regions.active_mod_surf_regions_index = 0

        return {'FINISHED'}


# Surface Regions Panels:


class MCELL_PT_object_selector(bpy.types.Panel):
    bl_label = "CellBlender - Object Selector"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "CellBlender"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( self.layout )
        else:
            layout.prop(mcell.object_selector, "filter", text="Object Filter:")
            row = layout.row(align=True)
            row.operator("mcell.select_filtered", text="Select Filtered")
            row.operator("mcell.deselect_filtered", text="Deselect Filtered")
            row=layout.row(align=True)
            row.operator("mcell.toggle_visibility_filtered",text="Visibility Filtered")
            row.operator("mcell.toggle_renderability_filtered",text="Renderability Filtered")




class MCELL_UL_check_mod_surface_regions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if item.status:
            layout.label(item.status, icon='ERROR')
        else:
            layout.label(item.name, icon='FILE_TICK')


class MCELL_PT_mod_surface_regions(bpy.types.Panel):
    bl_label = "CellBlender - Assign Surface Classes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        context.scene.mcell.mod_surf_regions.draw_panel ( context, self )



# Surface Regions Property Groups


class MCellModSurfRegionsProperty(bpy.types.PropertyGroup):
    """ Assign a surface class to a surface region. """

    name = StringProperty(name="Assign Surface Class")
    surf_class_name = StringProperty(
        name="Surface Class Name",
        description="This surface class will be assigned to the surface "
                    "region listed below.",
        update=check_active_mod_surf_regions)
    object_name = StringProperty(
        name="Object Name",
        description="A region on this object will have the above surface "
                    "class assigned to it.",
        update=check_active_mod_surf_regions)
    region_name = StringProperty(
        name="Region Name",
        description="This surface region will have the above surface class "
                    "assigned to it.",
        update=check_active_mod_surf_regions)
    status = StringProperty(name="Status")

    def remove_properties ( self, context ):
        print ( "Removing all Surface Regions Properties... no collections to remove." )

    def build_data_model_from_properties ( self, context ):
        print ( "Surface Region building Data Model" )
        sr_dm = {}
        sr_dm['data_model_version'] = "DM_2014_10_24_1638"
        sr_dm['name'] = self.name
        sr_dm['surf_class_name'] = self.surf_class_name
        sr_dm['object_name'] = self.object_name
        sr_dm['region_name'] = self.region_name
        return sr_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModSurfRegionsProperty Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsProperty data model to current version." )
            return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsProperty data model to current version." )

        self.name = dm["name"]
        self.surf_class_name = dm["surf_class_name"]
        self.object_name = dm["object_name"]
        self.region_name = dm["region_name"]

    def check_properties_after_building ( self, context ):
        print ( "Implementing check_properties_after_building for " + str(self) )
        print ( "Calling check_mod_surf_regions on object named: " + self.object_name )
        check_mod_surf_regions(self, context)


class MCellModSurfRegionsPropertyGroup(bpy.types.PropertyGroup):
    mod_surf_regions_list = CollectionProperty(
        type=MCellModSurfRegionsProperty, name="Assign Surface Class List")
    active_mod_surf_regions_index = IntProperty(
        name="Active Assign Surface Class Index", default=0)

    def build_data_model_from_properties ( self, context ):
        print ( "Assign Surface Class List building Data Model" )
        sr_dm = {}
        sr_dm['data_model_version'] = "DM_2014_10_24_1638"
        sr_list = []
        for sr in self.mod_surf_regions_list:
            sr_list.append ( sr.build_data_model_from_properties(context) )
        sr_dm['modify_surface_regions_list'] = sr_list
        return sr_dm


    @staticmethod
    def upgrade_data_model ( dm ):
        # Upgrade the data model as needed. Return updated data model or None if it can't be upgraded.
        print ( "------------------------->>> Upgrading MCellModSurfRegionsPropertyGroup Data Model" )
        if not ('data_model_version' in dm):
            # Make changes to move from unversioned to DM_2014_10_24_1638
            dm['data_model_version'] = "DM_2014_10_24_1638"

        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.flag_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsPropertyGroup data model to current version." )
            return None

        if "modify_surface_regions_list" in dm:
            for item in dm["modify_surface_regions_list"]:
                if MCellModSurfRegionsProperty.upgrade_data_model ( item ) == None:
                    return None

        return dm


    def build_properties_from_data_model ( self, context, dm ):

        # Check that the data model version matches the version for this property group
        if dm['data_model_version'] != "DM_2014_10_24_1638":
            data_model.handle_incompatible_data_model ( "Error: Unable to upgrade MCellModSurfRegionsPropertyGroup data model to current version." )

        while len(self.mod_surf_regions_list) > 0:
            self.mod_surf_regions_list.remove(0)
        if "modify_surface_regions_list" in dm:
            for s in dm["modify_surface_regions_list"]:
                self.mod_surf_regions_list.add()
                self.active_mod_surf_regions_index = len(self.mod_surf_regions_list)-1
                sr = self.mod_surf_regions_list[self.active_mod_surf_regions_index]
                # sr.init_properties(context.scene.mcell.parameter_system)
                sr.build_properties_from_data_model ( context, s )


    def check_properties_after_building ( self, context ):
        print ( "Implementing check_properties_after_building for " + str(self) )
        for sr in self.mod_surf_regions_list:
            sr.check_properties_after_building(context)

    def remove_properties ( self, context ):
        print ( "Removing all Surface Regions Properties ..." )
        for item in self.mod_surf_regions_list:
            item.remove_properties(context)
        self.mod_surf_regions_list.clear()
        self.active_mod_surf_regions_index = 0
        print ( "Done removing all Surface Regions Properties." )


    def draw_layout(self, context, layout):
        mcell = context.scene.mcell

        if not mcell.initialized:
            mcell.draw_uninitialized ( layout )
        else:

            # mod_surf_regions = context.scene.mcell.mod_surf_regions

            row = layout.row()
            if not mcell.surface_classes.surf_class_list:
                row.label(text="Define at least one surface class", icon='ERROR')
            elif not mcell.model_objects.object_list:
                row.label(text="Add a mesh to the Model Objects list",
                          icon='ERROR')
            else:
                col = row.column()
                col.template_list("MCELL_UL_check_mod_surface_regions",
                                  "mod_surf_regions", self,
                                  "mod_surf_regions_list", self,
                                  "active_mod_surf_regions_index", rows=2)
                col = row.column(align=True)
                col.operator("mcell.mod_surf_regions_add", icon='ZOOMIN', text="")
                col.operator("mcell.mod_surf_regions_remove", icon='ZOOMOUT',
                             text="")
                if self.mod_surf_regions_list:
                    active_mod_surf_regions = \
                        self.mod_surf_regions_list[
                            self.active_mod_surf_regions_index]
                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "surf_class_name",
                                    mcell.surface_classes, "surf_class_list",
                                    icon='FACESEL_HLT')
                    row = layout.row()
                    row.prop_search(active_mod_surf_regions, "object_name",
                                    mcell.model_objects, "object_list",
                                    icon='MESH_ICOSPHERE')
                    if active_mod_surf_regions.object_name:
                        try:
                            regions = bpy.data.objects[
                                active_mod_surf_regions.object_name].mcell.regions
                            layout.prop_search(active_mod_surf_regions,
                                               "region_name", regions,
                                               "region_list", icon='FACESEL_HLT')
                        except KeyError:
                            pass


    def draw_panel ( self, context, panel ):
        """ Create a layout from the panel and draw into it """
        layout = panel.layout
        self.draw_layout ( context, layout )




#Custom Properties


