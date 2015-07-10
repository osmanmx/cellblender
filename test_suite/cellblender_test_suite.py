relative_path_to_mcell = "/../mcell_git/src/linux/mcell"

"""
# This section of code was used (from the command line) to copy this addon to the Blender addons area. Now the makefile performs that task.
install_to = "2.75"


# From within Blender: import cellblender.test_suite.cellblender_test_suite
if __name__ == "__main__":
  # Simple method to "install" a new version with "python test_suite/cellblender_test_suite.py" assuming "test_suite" directory exists in target location.
  import os
  print ( "MAIN with __file__ = " + __file__ )
  print ( " Installing into Blender " + install_to )
  os.system ( "cp ./" + __file__ + " ~/.config/blender/" + install_to + "/scripts/addons/" + __file__ )
  print ( "Copied files" )
  exit(0)
"""


bl_info = {
  "version": "0.1",
  "name": "CellBlender Test Suite",
  'author': 'Bob',
  "location": "Properties > Scene",
  "category": "Cell Modeling"
  }


##################
#  Support Code  #
##################

import sys
import os
import hashlib
import bpy
from bpy.props import *

class CellBlenderTestPropertyGroup(bpy.types.PropertyGroup):
    path_to_mcell = bpy.props.StringProperty(name="PathToMCell", default="")
    path_to_blend = bpy.props.StringProperty(name="PathToBlend", default="")
    run_mcell = bpy.props.BoolProperty(name="RunMCell", default=False)
    test_status = bpy.props.StringProperty(name="TestStatus", default="?")
    
    show_sim_runner = bpy.props.BoolProperty(name="ShowSimRunner", default=False)
    show_non_geom = bpy.props.BoolProperty(name="ShowNonGeom", default=False)
    show_simple_geom = bpy.props.BoolProperty(name="ShowSimpleGeom", default=False)
    show_complete_model = bpy.props.BoolProperty(name="ShowCompleteModel", default=False)

class CellBlenderTestSuitePanel(bpy.types.Panel):
    bl_label = "CellBlender Test Suite"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    def draw(self, context):
        app = context.scene.cellblender_test_suite


        row = self.layout.row()
        row.prop(app, "path_to_mcell")
        row = self.layout.row()
        row.prop(app, "path_to_blend")

        row = self.layout.row()
        row.operator ( "cellblender_test.load_home_file" )
        row.operator ( "cellblender_test.save_home_file" )

        row = self.layout.row()
        if app.test_status == "?":
          row.label( icon='QUESTION',  text="?" )
        elif app.test_status == "P":
          row.label( icon='FILE_TICK', text="Pass" )
        elif app.test_status == "F":
          row.label( icon='ERROR',     text="Fail" )
        row.prop(app, "run_mcell")

        box = self.layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'


        if not app.show_sim_runner:
            row.prop(app, "show_sim_runner", icon='TRIA_RIGHT', text="Sim Runner Tests", emboss=False)
        else:
            row.prop(app, "show_sim_runner", icon='TRIA_DOWN', text="Sim Runner Tests", emboss=False)

            row = box.row()
            row.operator ( "cellblender_test.sim_runner_command" )
            row = box.row()
            row.operator ( "cellblender_test.sim_runner_queue" )
            row = box.row()
            row.operator ( "cellblender_test.sim_runner_java" )
            row = box.row()
            row.operator ( "cellblender_test.sim_runner_opengl" )


        box = self.layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        if not app.show_non_geom:
            row.prop(app, "show_non_geom", icon='TRIA_RIGHT', text="Non-Geometry Tests", emboss=False)
        else:
            row.prop(app, "show_non_geom", icon='TRIA_DOWN', text="Non-Geometry Tests", emboss=False)
            row = box.row()
            row.operator ( "cellblender_test.single_mol" )
            row = box.row()
            row.operator ( "cellblender_test.double_sphere" )
            row = box.row()
            row.operator ( "cellblender_test.vol_diffusion_const" )
            row = box.row()
            row.operator ( "cellblender_test.reaction" )
            row = box.row()
            row.operator ( "cellblender_test.release_shape" )
            row = box.row()
            row.operator ( "cellblender_test.rel_time_patterns_test" )

        box = self.layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        if not app.show_simple_geom:
            row.prop(app, "show_simple_geom", icon='TRIA_RIGHT', text="Simple Geometry Tests", emboss=False)
        else:
            row.prop(app, "show_simple_geom", icon='TRIA_DOWN', text="Simple Geometry Tests", emboss=False)
            row = box.row()
            row.operator ( "cellblender_test.cube_test" )
            row = box.row()
            row.operator ( "cellblender_test.cube_surf_test" )
            row = box.row()
            row.operator ( "cellblender_test.sphere_surf_test" )
            row = box.row()
            row.operator ( "cellblender_test.overlapping_surf_test" )


        box = self.layout.box()
        row = box.row(align=True)
        row.alignment = 'LEFT'

        if not app.show_complete_model:
            row.prop(app, "show_complete_model", icon='TRIA_RIGHT', text="Complete Model Tests", emboss=False)
        else:
            row.prop(app, "show_complete_model", icon='TRIA_DOWN', text="Complete Model Tests", emboss=False)
            row = box.row()
            row.operator ( "cellblender_test.organelle_test" )
            row = box.row()
            row.operator ( "cellblender_test.lotka_volterra_torus_test_diff_lim" )
            row = box.row()
            row.operator ( "cellblender_test.lotka_volterra_torus_test_phys" )



class LoadHomeOp(bpy.types.Operator):
    bl_idname = "cellblender_test.load_home_file"
    bl_label = "Load Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        context.scene.cellblender_test_suite.test_status == "?"
        bpy.ops.wm.read_homefile()
        return { 'FINISHED' }


class SaveHomeOp(bpy.types.Operator):
    bl_idname = "cellblender_test.save_home_file"
    bl_label = "Save Startup"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        context.scene.cellblender_test_suite.test_status == "?"
        bpy.ops.wm.save_homefile()
        return { 'FINISHED' }




class CellBlender_Model:

    old_type = None
    context = None
    scn = None
    mcell = None
    path_to_blend = None
    
    def __init__(self, cb_context):
        # bpy.ops.wm.read_homefile()
        self.old_type = None
        self.context = cb_context
        self.setup_cb_defaults ( self.context )
        self.context.scene.cellblender_test_suite.test_status == "?"
        
    def get_scene(self):
        return self.scn
        
    def get_mcell(self):
        return self.mcell


    """
    def get_3d_view_areas(self):
        areas_3d = []
        for area in self.context.screen.areas:
            if area.type == 'VIEW_3D':
                areas_3d = areas_3d + [area]
                # area.spaces.active.show_manipulator = False
        return areas_3d
    """

    def get_3d_view_spaces(self):
        spaces_3d = []
        for area in self.context.screen.areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    spaces_3d = spaces_3d + [space]
                    # area.spaces.active.show_manipulator = False
        return spaces_3d


    def set_view_3d(self):
        area = bpy.context.area
        if area == None:
            self.old_type = 'VIEW_3D'
        else:
            self.old_type = area.type
        area.type = 'VIEW_3D'
      
    def set_view_back(self):
        area = bpy.context.area
        area.type = self.old_type

    def save_blend_file( self, context ):
        app = context.scene.cellblender_test_suite
        wm = context.window_manager

        if len(app.path_to_blend) > 0:
            self.path_to_blend = app.path_to_blend
        else:
            self.path_to_blend = os.getcwd() + "/Test.blend"

        bpy.ops.wm.save_as_mainfile(filepath=self.path_to_blend, check_existing=False)


    def get_scene(self):
        return bpy.data.scenes['Scene']

    def delete_all_objects(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=True)

    def reload_cellblender(self, scn):
        print ( "Disabling CellBlender Application" )
        bpy.ops.wm.addon_disable(module='cellblender')

        print ( "Delete MCell RNA properties if needed" )
        # del bpy.types.Scene.mcell
        if scn.get ( 'mcell' ):
            print ( "Deleting MCell RNA properties" )
            del scn['mcell']

        print ( "Enabling CellBlender Application" )
        bpy.ops.wm.addon_enable(module='cellblender')


    def setup_mcell(self, scn):
        mcell = scn.mcell
        app = bpy.context.scene.cellblender_test_suite

        print ( "Initializing CellBlender Application" )
        bpy.ops.mcell.init_cellblender()

        print ( "Setting Preferences" )
        if len(app.path_to_mcell) > 0:
            mcell.cellblender_preferences.mcell_binary = app.path_to_mcell
        else:
            mcell.cellblender_preferences.mcell_binary = os.getcwd() + relative_path_to_mcell

        mcell.cellblender_preferences.mcell_binary_valid = True
        mcell.cellblender_preferences.show_sim_runner_options = True
        mcell.run_simulation.simulation_run_control = 'COMMAND'
        
        return mcell

    def setup_cb_defaults ( self, context ):

        self.save_blend_file( context )
        scn = self.get_scene()
        self.set_view_3d()
        self.delete_all_objects()
        self.reload_cellblender(scn)
        mcell = self.setup_mcell(scn)

        print ( "Snapping Cursor to Center" )
        bpy.ops.view3d.snap_cursor_to_center()
        print ( "Done Snapping Cursor to Center" )
        
        self.scn = scn
        self.mcell = mcell

    def add_cube_to_model ( self, name="Cell", draw_type="WIRE" ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.ops.mesh.primitive_cube_add()
        self.scn.objects.active.name = name
        bpy.data.objects[name].draw_type = draw_type

        # Add the newly added object to the model objects list

        self.mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        print ( "Done Adding " + name )


    def add_icosphere_to_model ( self, name="Cell", draw_type="WIRE", x=0, y=0, z=0, size=1, subdiv=2 ):
        """ draw_type is one of: WIRE, TEXTURED, SOLID, BOUNDS """
        print ( "Adding " + name )
        bpy.ops.mesh.primitive_ico_sphere_add ( subdivisions=subdiv, size=size, location=(x, y, z) )
        self.scn.objects.active.name = name
        bpy.data.objects[name].draw_type = draw_type

        # Add the newly added object to the model objects list

        self.mcell.cellblender_main_panel.objects_select = True
        bpy.ops.mcell.model_objects_add()
        print ( "Done Adding " + name )


    def add_molecule_species_to_model ( self, name="A", mol_type="3D", diff_const_expr="0.0" ):
        """ Add a molecule species """
        print ( "Adding Molecule Species " + name )
        self.mcell.cellblender_main_panel.molecule_select = True
        bpy.ops.mcell.molecule_add()
        mol_index = self.mcell.molecules.active_mol_index
        self.mcell.molecules.molecule_list[mol_index].name = name
        self.mcell.molecules.molecule_list[mol_index].type = mol_type
        self.mcell.molecules.molecule_list[mol_index].diffusion_constant.set_expr(diff_const_expr)
        print ( "Done Adding Molecule " + name )
        return self.mcell.molecules.molecule_list[mol_index]


    def add_molecule_release_site_to_model ( self, name=None, mol="a", shape="SPHERICAL", obj_expr="", orient="'", q_expr="100", q_type='NUMBER_TO_RELEASE', d="0", x="0", y="0", z="0", pattern=None ):
        """ Add a molecule release site """
        """ shape is one of: 'CUBIC', 'SPHERICAL', 'SPHERICAL_SHELL', 'OBJECT' """
        """ q_type is one of: 'NUMBER_TO_RELEASE', 'GAUSSIAN_RELEASE_NUMBER', 'DENSITY' """
        if name == None:
            name = "rel_" + mol

        print ( "Releasing Molecules at " + name )
        self.mcell.cellblender_main_panel.placement_select = True
        bpy.ops.mcell.release_site_add()
        rel_index = self.mcell.release_sites.active_release_index
        self.mcell.release_sites.mol_release_list[rel_index].name = name
        self.mcell.release_sites.mol_release_list[rel_index].molecule = mol
        self.mcell.release_sites.mol_release_list[rel_index].shape = shape
        self.mcell.release_sites.mol_release_list[rel_index].object_expr = obj_expr
        self.mcell.release_sites.mol_release_list[rel_index].orient = orient
        self.mcell.release_sites.mol_release_list[rel_index].quantity_type = q_type
        self.mcell.release_sites.mol_release_list[rel_index].quantity.set_expr(q_expr)
        self.mcell.release_sites.mol_release_list[rel_index].diameter.set_expr(d)
        self.mcell.release_sites.mol_release_list[rel_index].location_x.set_expr(x)
        self.mcell.release_sites.mol_release_list[rel_index].location_y.set_expr(y)
        self.mcell.release_sites.mol_release_list[rel_index].location_z.set_expr(z)
        if pattern != None:
            self.mcell.release_sites.mol_release_list[rel_index].pattern = pattern
        print ( "Done Releasing Molecule " + name )
        return self.mcell.release_sites.mol_release_list[rel_index]



    def add_release_pattern_to_model ( self, name="time_pattern", delay="0", release_interval="", train_duration="", train_interval="", num_trains="1" ):
        """ Add a release time pattern """
        print ( "Adding a Release Time Pattern " + name + " " + delay + " " + release_interval )
        bpy.ops.mcell.release_pattern_add()
        pat_index = self.mcell.release_patterns.active_release_pattern_index
        self.mcell.release_patterns.release_pattern_list[pat_index].name = name
        self.mcell.release_patterns.release_pattern_list[pat_index].delay.set_expr ( delay )
        self.mcell.release_patterns.release_pattern_list[pat_index].release_interval.set_expr ( release_interval )
        self.mcell.release_patterns.release_pattern_list[pat_index].train_duration.set_expr ( train_duration )
        self.mcell.release_patterns.release_pattern_list[pat_index].train_interval.set_expr ( train_interval )
        self.mcell.release_patterns.release_pattern_list[pat_index].number_of_trains.set_expr ( num_trains )
        print ( "Done Adding Release Time Pattern " + name + " " + delay + " " + release_interval )
        return self.mcell.release_patterns.release_pattern_list[pat_index]



    def add_reaction_to_model ( self, name="", rin="", rtype="irreversible", rout="", fwd_rate="0", bkwd_rate="" ):
        """ Add a reaction """
        print ( "Adding Reaction " + rin + " " + rtype + " " + rout )
        self.mcell.cellblender_main_panel.reaction_select = True
        bpy.ops.mcell.reaction_add()
        rxn_index = self.mcell.reactions.active_rxn_index
        self.mcell.reactions.reaction_list[rxn_index].reactants = rin
        self.mcell.reactions.reaction_list[rxn_index].products = rout
        self.mcell.reactions.reaction_list[rxn_index].type = rtype
        self.mcell.reactions.reaction_list[rxn_index].fwd_rate.set_expr(fwd_rate)
        self.mcell.reactions.reaction_list[rxn_index].bkwd_rate.set_expr(bkwd_rate)
        print ( "Done Adding Reaction " + rin + " " + rtype + " " + rout )
        return self.mcell.reactions.reaction_list[rxn_index]


    def add_reaction_output_to_model ( self, mol_name ):
        """ Add a reaction output """
        print ( "Adding Reaction Output for Molecule " + mol_name )
        self.mcell.cellblender_main_panel.graph_select = True
        bpy.ops.mcell.rxn_output_add()
        rxn_index = self.mcell.rxn_output.active_rxn_output_index
        self.mcell.rxn_output.rxn_output_list[rxn_index].molecule_name = mol_name
        print ( "Done Adding Reaction Output for Molecule " + mol_name )
        return self.mcell.rxn_output.rxn_output_list[rxn_index]


    def add_surface_region_to_model_by_normal ( self, obj_name, surf_name, nx, ny, nz, min_dot_prod ):

        print ("Selected Object = " + str(self.context.object) )
        # bpy.ops.object.mode_set ( mode="EDIT" )

        # Start in Object mode for selecting
        bpy.ops.object.mode_set ( mode="OBJECT" )

        # Face Select Mode:
        msm = self.context.scene.tool_settings.mesh_select_mode[0:3]
        self.context.scene.tool_settings.mesh_select_mode = (False, False, True)

        # Deselect everything
        bpy.ops.object.select_all ( action='DESELECT')
        c = bpy.data.objects[obj_name]
        c.select = False

        # Select just the top faces (normals up)
        mesh = c.data

        bpy.ops.object.mode_set(mode='OBJECT')

        for p in mesh.polygons:
          n = p.normal
          dp = (n.x * nx) + (n.y * ny) + (n.z * nz)
          if dp > min_dot_prod:
            # This appears to be a triangle in the top face
            #print ( "Normal " + str (n) + " matches with " + str(dp) )
            p.select = True
          else:
            #print ( "Normal " + str (n) + " differs with " + str(dp) )
            p.select = False

        bpy.ops.object.mode_set(mode='EDIT')

        # Add a new region

        bpy.ops.mcell.region_add()
        bpy.data.objects[obj_name].mcell.regions.region_list[0].name = surf_name

        # Assign the currently selected faces to this region
        bpy.ops.mcell.region_faces_assign()

        # Restore the selection settings
        self.context.scene.tool_settings.mesh_select_mode = msm
        bpy.ops.object.mode_set(mode='OBJECT')


    def wait ( self, wait_time ):
        import time
        time.sleep ( wait_time )


    def run_model ( self, iterations="100", time_step="1e-6", export_format="mcell_mdl_unified", wait_time=10.0 ):
        """ export_format is one of: mcell_mdl_unified, mcell_mdl_modular """
        print ( "Running Simulation" )
        self.mcell.cellblender_main_panel.init_select = True
        self.mcell.initialization.iterations.set_expr(iterations)
        self.mcell.initialization.time_step.set_expr(time_step)
        self.mcell.export_project.export_format = export_format

        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            bpy.ops.mcell.run_simulation()
            self.wait ( wait_time )
        else:
            bpy.ops.mcell.export_project()


    def refresh_molecules ( self ):
        """ Refresh the display """
        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            bpy.ops.cbm.refresh_operator()


    def change_molecule_display ( self, mol, glyph="Cube", scale=1.0, red=-1, green=-1, blue=-1 ):
        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            if mol.name == "Molecule":
                print ("Name isn't correct")
                return
            print ( "Changing Display for Molecule \"" + mol.name + "\" to R="+str(red)+",G="+str(green)+",B="+str(blue) )
            self.mcell.cellblender_main_panel.molecule_select = True
            self.mcell.molecules.show_display = True
            mol.glyph = glyph
            mol.scale = scale
            if red >= 0: mol.color.r = red
            if green >= 0: mol.color.g = green
            if blue >= 0: mol.color.b = blue

            print ( "Done Changing Display for Molecule \"" + mol.name + "\"" )


    def compare_mdl_with_sha1 ( self, good_hash ):
        """ Compute the sha1 for file_name and compare with sha1 """
        app = bpy.context.scene.cellblender_test_suite
        file_name = self.path_to_blend[:self.path_to_blend.rfind('.')] + "_files/mcell/Scene.main.mdl"

        hashobject = hashlib.sha1()
        if os.path.isfile(file_name):
            hashobject.update(open(file_name, 'rb').read())  # .encode("utf-8"))
            file_hash = str(hashobject.hexdigest())
            print("  SHA1 = " + file_hash + " for " + file_name )
            if file_hash == good_hash:
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                print ( "%%  O K :  Test Expected " + good_hash + ", and got " + file_hash )
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                app.test_status = "P"

            else:
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                print ( "%%  E R R O R :  Test Expected " + good_hash + ", but got " + file_hash )
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
                app.test_status = "F"
                bpy.ops.wm.quit_blender() 
        else:
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "%%  E R R O R :  File '%s' does not exist" % file_name )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            print ( "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" )
            app.test_status = "F"
            bpy.ops.wm.quit_blender()


    def scale_view_distance ( self, scale ):
        """ Change the view distance for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_distance *= scale
        #bpy.ops.view3d.zoom(delta=3)
        #set_view_3d()

    def switch_to_perspective ( self ):
        """ Change to perspective for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_perspective = 'PERSP'

    def switch_to_orthographic ( self ):
        """ Change to orthographic for all 3D_VIEW windows """
        spaces = self.get_3d_view_spaces()
        for space in spaces:
            space.region_3d.view_perspective = 'ORTHO'

    def play_animation ( self ):
        """ Play the animation """
        app = bpy.context.scene.cellblender_test_suite
        if app.run_mcell:
            bpy.ops.screen.animation_play()






######################
#  Individual Tests  #
######################

def SimRunnerExample ( context, method="COMMAND" ):

    cb_model = CellBlender_Model ( context )

    scn = cb_model.get_scene()
    mcell = cb_model.get_mcell()
    mcell.run_simulation.simulation_run_control = method

    mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

    cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="200" )

    cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

    cb_model.compare_mdl_with_sha1 ( "a3409b4891f9d5a9be8010afb3923f0a14d5ec4a" )

    cb_model.refresh_molecules()

    cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )

    cb_model.set_view_back()

    cb_model.scale_view_distance ( 0.1 )

    cb_model.play_animation()


class SimRunnerCommandTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.sim_runner_command"
    bl_label = "Simulation Runner Command Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="COMMAND" )
        return { 'FINISHED' }


class SimRunnerQueueTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.sim_runner_queue"
    bl_label = "Simulation Runner Queue Test"


    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="QUEUE" )
        return { 'FINISHED' }


class SimRunnerJavaTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.sim_runner_java"
    bl_label = "Simulation Runner Java Test"


    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="JAVA" )
        return { 'FINISHED' }


class SimRunnerOpenGLTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.sim_runner_opengl"
    bl_label = "Simulation Runner Open GL Test"


    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):
        SimRunnerExample ( context, method="OPENGL" )
        return { 'FINISHED' }




class SingleMoleculeTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.single_mol"
    bl_label = "Single Molecule Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="1" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )
        
        cb_model.compare_mdl_with_sha1 ( "19fd01beddf82da6026810b52d6955638674f556" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol, glyph='Torus', scale=4.0, red=1.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.02 )

        cb_model.play_animation()

        return { 'FINISHED' }



class DoubleSphereTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.double_sphere"
    bl_label = "Double Sphere Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="400", d="0.5", y="-0.25" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="400", d="0.5", y="0.25" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

        cb_model.compare_mdl_with_sha1 ( "4410b18c1530f79c07cc2aebec52a7eabc4aded4" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=2.0, red=0.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.1 )

        cb_model.play_animation()

        return { 'FINISHED' }



class VolDiffusionConstTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.vol_diffusion_const"
    bl_label = "Volume Diffusion Constant Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-7" )
        mol_c = cb_model.add_molecule_species_to_model ( name="c", diff_const_expr="1e-8" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="100", d="0.01", y="-0.25" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="100", d="0.01", y= "0.0" )
        cb_model.add_molecule_release_site_to_model ( mol="c", q_expr="100", d="0.01", y= "0.25" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

        cb_model.compare_mdl_with_sha1 ( "59b7e9f0f672791101d6a0061af362688e8caa42" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=2.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_c, glyph='Cube', scale=2.0, red=0.1, green=0.1, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.1 )
        cb_model.switch_to_orthographic()

        cb_model.play_animation()

        return { 'FINISHED' }



class ReactionTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.reaction"
    bl_label = "Simple Reaction Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )
        mol_c = cb_model.add_molecule_species_to_model ( name="bg", diff_const_expr="1e-5" )

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr="400", d="0.5", y="-0.05" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="400", d="0.5", y="0.05" )

        # Create a single c molecule at the origin so its properties will be changed
        cb_model.add_molecule_release_site_to_model ( mol="bg", q_expr="1", d="0", y="0" )

        cb_model.add_reaction_to_model ( rin="a + b", rtype="irreversible", rout="bg", fwd_rate="1e8", bkwd_rate="" )

        cb_model.run_model ( iterations='2000', time_step='1e-6', wait_time=5.0 )

        cb_model.compare_mdl_with_sha1 ( "e302a61ecda563a02e8d65ef17c648ff088745d2" )

        cb_model.refresh_molecules()

        # Try to advance frame so molecules exist before changing them
        # scn.frame_current = 1999

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=2.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_c, glyph='Torus', scale=10.0, red=1.0, green=1.0, blue=0.5 )

        #cb_model.refresh_molecules()

        # Set time back to 0
        #scn.frame_current = 0

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.1 )

        cb_model.play_animation()

        return { 'FINISHED' }


class ReleaseShapeTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.release_shape"
    bl_label = "Release Shape Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_cube_to_model ( name="Cell", draw_type="WIRE" )

        diff_const = "1e-6"

        mol_a = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr=diff_const )
        mol_b = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr=diff_const )
        mol_c = cb_model.add_molecule_species_to_model ( name="bg", diff_const_expr=diff_const )
        mol_d = cb_model.add_molecule_species_to_model ( name="d", diff_const_expr=diff_const )

        num_rel = "1000"

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr=num_rel, shape="OBJECT", obj_expr="Cell",  )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr=num_rel, shape="SPHERICAL",       d="1.5", y="1" )
        cb_model.add_molecule_release_site_to_model ( mol="bg", q_expr=num_rel, shape="CUBIC",           d="1.5", y="-1" )
        cb_model.add_molecule_release_site_to_model ( mol="d", q_expr=num_rel, shape="SPHERICAL_SHELL", d="1.5", z="1" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=1.0 )

        cb_model.compare_mdl_with_sha1 ( "c622d3e5c9eaf20911b95ae006eb197401d0e982" )

        cb_model.refresh_molecules()

        mol_scale = 2.5

        cb_model.change_molecule_display ( mol_a, glyph='Cube', scale=mol_scale, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b, glyph='Cube', scale=mol_scale, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_c, glyph='Cube', scale=mol_scale, red=0.0, green=0.0, blue=1.0 )
        cb_model.change_molecule_display ( mol_d, glyph='Cube', scale=mol_scale, red=1.0, green=1.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



class CubeTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.cube_test"
    bl_label = "Simple Cube Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_cube_to_model ( name="Cell", draw_type="WIRE" )

        mol = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="1000" )

        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=2.0 )

        cb_model.compare_mdl_with_sha1 ( "c32241a2f97ace100f1af7a711a6a970c6b9a135" )

        cb_model.refresh_molecules()

        cb_model.change_molecule_display ( mol, glyph='Cube', scale=4.0, red=1.0, green=0.0, blue=0.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



class CubeSurfaceTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.cube_surf_test"
    bl_label = "Cube Surface Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_cube_to_model ( name="Cell", draw_type="WIRE" )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "top", 0, 0, 1, 0.8 )

        mola = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mols = cb_model.add_molecule_species_to_model ( name="s", mol_type="2D", diff_const_expr="1e-6" )
        molb = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( mol="s", shape="OBJECT", obj_expr="Cell[top]", orient="'", q_expr="1000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="1", shape="SPHERICAL", d="0", z="1.001" )


        cb_model.add_reaction_to_model ( rin="a' + s,", rtype="irreversible", rout="b, + s,", fwd_rate="1e8", bkwd_rate="" )


        cb_model.run_model ( iterations='500', time_step='1e-6', wait_time=5.0 )

        cb_model.compare_mdl_with_sha1 ( "32312790f206beaa798ce0a7218f1f712840b0d5" )

        cb_model.refresh_molecules()
        
        scn.frame_current = 1

        cb_model.change_molecule_display ( mola, glyph='Cube', scale=3.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mols, glyph='Cone', scale=3.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molb, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



class SphereSurfaceTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.sphere_surf_test"
    bl_label = "Sphere Surface Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_icosphere_to_model ( name="Cell", draw_type="WIRE" )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "top", 0, 0, 1, 0.8 )

        mola = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-6" )
        mols = cb_model.add_molecule_species_to_model ( name="s", mol_type="2D", diff_const_expr="1e-6" )
        molb = cb_model.add_molecule_species_to_model ( name="b", diff_const_expr="1e-6" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( mol="s", shape="OBJECT", obj_expr="Cell[top]", orient="'", q_expr="1000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr="1", shape="SPHERICAL", d="0", z="1.001" )


        cb_model.add_reaction_to_model ( rin="a' + s,", rtype="irreversible", rout="b, + s,", fwd_rate="1e8", bkwd_rate="" )


        cb_model.run_model ( iterations='500', time_step='1e-6', wait_time=5.0 )

        cb_model.compare_mdl_with_sha1 ( "90ef79fc7405aff0bbf9a6f6864f11b148c622a4" )

        cb_model.refresh_molecules()
        
        scn.frame_current = 1

        cb_model.change_molecule_display ( mola, glyph='Cube', scale=3.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mols, glyph='Cone', scale=3.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( molb, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }




class OverlappingSurfaceTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.overlapping_surf_test"
    bl_label = "Overlapping Surface Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        cb_model.add_icosphere_to_model ( name="Cell", draw_type="WIRE", subdiv=4 )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "top", 0, 0, 1, 0.0 )
        cb_model.add_surface_region_to_model_by_normal ( "Cell", "y",   0, 1, 0, 0.0 )

        mola  = cb_model.add_molecule_species_to_model ( name="a", diff_const_expr="1e-5" )
        mols1 = cb_model.add_molecule_species_to_model ( name="s1", mol_type="2D", diff_const_expr="0" )
        mols2 = cb_model.add_molecule_species_to_model ( name="s2", mol_type="2D", diff_const_expr="0" )
        molb1 = cb_model.add_molecule_species_to_model ( name="b1", diff_const_expr="1e-7" )
        molb2 = cb_model.add_molecule_species_to_model ( name="b2", diff_const_expr="1e-7" )

        cb_model.add_molecule_release_site_to_model ( mol="a", shape="OBJECT", obj_expr="Cell", q_expr="2000" )
        cb_model.add_molecule_release_site_to_model ( mol="s1", shape="OBJECT", obj_expr="Cell[top]", orient="'", q_expr="2000" )
        cb_model.add_molecule_release_site_to_model ( mol="s2", shape="OBJECT", obj_expr="Cell[y]", orient="'", q_expr="2000" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b1", q_expr="1", shape="SPHERICAL", d="0", z="0" )
        cb_model.add_molecule_release_site_to_model ( mol="b2", q_expr="1", shape="SPHERICAL", d="0", z="0" )


        cb_model.add_reaction_to_model ( rin="a' + s1,", rtype="irreversible", rout="a' + b1, + s1,", fwd_rate="1e10", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="a' + s2,", rtype="irreversible", rout="a' + b2, + s2,", fwd_rate="1e10", bkwd_rate="" )


        cb_model.run_model ( iterations='200', time_step='1e-6', wait_time=3.0 )

        cb_model.compare_mdl_with_sha1 ( "3f0d87d4f5e1ab1ecedde6c0d48fa3d2dc89ab93" )

        cb_model.refresh_molecules()

        scn.frame_current = 1

        """
        cb_model.change_molecule_display ( mola, glyph='Cube',  scale=3.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mols1, glyph='Cone', scale=3.0, red=0.0, green=1.0, blue=0.0 )
        cb_model.change_molecule_display ( mols2, glyph='Cone', scale=3.0, red=1.0, green=0.0, blue=1.0 )
        cb_model.change_molecule_display ( molb1, glyph='Cube', scale=4.0, red=1.0, green=1.0, blue=1.0 )
        """

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.25 )

        cb_model.play_animation()

        return { 'FINISHED' }



class ReleaseTimePatternsTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.rel_time_patterns_test"
    bl_label = "Release Time Patterns Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()

        diff_const = "0"

        mol_a =  cb_model.add_molecule_species_to_model ( name="a",  diff_const_expr=diff_const )
        mol_b =  cb_model.add_molecule_species_to_model ( name="b",  diff_const_expr=diff_const )
        mol_bg = cb_model.add_molecule_species_to_model ( name="bg", diff_const_expr="0" )


        decay_rate = "8e6"
        cb_model.add_reaction_to_model ( rin="a",  rtype="irreversible", rout="NULL", fwd_rate=decay_rate, bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="b",  rtype="irreversible", rout="NULL", fwd_rate=decay_rate+"/5", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="bg", rtype="irreversible", rout="NULL", fwd_rate=decay_rate+"/500", bkwd_rate="" )


        dt = "1e-6"
        cb_model.add_release_pattern_to_model ( name="spike_pattern", delay="300 * " + dt, release_interval="10 * " + dt, train_duration="100 * " + dt, train_interval="200 * " + dt, num_trains="5" )
        cb_model.add_release_pattern_to_model ( name="background", delay="0", release_interval="100 * " + dt, train_duration="1e20", train_interval="2e20", num_trains="1" )


        num_rel = "10"

        cb_model.add_molecule_release_site_to_model ( mol="a", q_expr=num_rel, shape="SPHERICAL", d="0.1", z="0.2", pattern="spike_pattern" )
        cb_model.add_molecule_release_site_to_model ( mol="b", q_expr=num_rel, shape="SPHERICAL", d="0.1", z="0.4", pattern="spike_pattern" )
        cb_model.add_molecule_release_site_to_model ( mol="bg", q_expr="1",    shape="SPHERICAL", d="1.0", z="0.0", pattern="background" )

        #### Add a single a molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="a",  name="a_dummy",  q_expr="1", shape="SPHERICAL" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="b",  name="b_dummy",  q_expr="1", shape="SPHERICAL" )
        #### Add a single b molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="bg", name="bg_dummy", q_expr="1", shape="SPHERICAL" )


        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[0].molecule_name = 'a'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[1].molecule_name = 'b'

        bpy.ops.mcell.rxn_output_add()
        mcell.rxn_output.rxn_output_list[2].molecule_name = 'bg'


        cb_model.run_model ( iterations='1500', time_step=dt, wait_time=5.0 )

        cb_model.compare_mdl_with_sha1 ( "ec68e0720b43755c4f193d65ebaaa55eb2c2cfae" )

        cb_model.refresh_molecules()

        mol_scale = 1.0

        cb_model.change_molecule_display ( mol_a,  glyph='Cube',  scale=mol_scale, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( mol_b,  glyph='Cube',  scale=mol_scale, red=0.5, green=0.5, blue=1.0 )
        cb_model.change_molecule_display ( mol_bg, glyph='Torus', scale=mol_scale, red=1.0, green=1.0, blue=1.0 )

        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.05 )

        cb_model.play_animation()

        return { 'FINISHED' }



def LotkaVolterraTorus ( context, prey_birth_rate, predation_rate, pred_death_rate, interaction_radius, time_step, iterations, mdl_hash, wait_time ):

    cb_model = CellBlender_Model ( context )

    scn = cb_model.get_scene()
    mcell = cb_model.get_mcell()

    # Create the Torus
    bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=10,major_radius=0.1,minor_radius=0.03)
    scn.objects.active.name = 'arena'

    # Set up the material for the Torus
    bpy.data.materials[0].name = 'cell'
    bpy.data.materials['cell'].use_transparency = True
    bpy.data.materials['cell'].alpha = 0.3

    # Assign the material to the Torus
    bpy.ops.object.material_slot_add()
    scn.objects['arena'].material_slots[0].material = bpy.data.materials['cell']
    scn.objects['arena'].show_transparent = True

    # Add the new Torus to the model objects list
    mcell.cellblender_main_panel.objects_select = True
    bpy.ops.mcell.model_objects_add()

    # Add the molecules
    prey = cb_model.add_molecule_species_to_model ( name="prey", diff_const_expr="6e-6" )
    pred = cb_model.add_molecule_species_to_model ( name="predator", diff_const_expr="6e-6" )

    cb_model.add_molecule_release_site_to_model ( name="prey_rel", mol="prey", shape="OBJECT", obj_expr="arena", q_expr="1000" )
    cb_model.add_molecule_release_site_to_model ( name="pred_rel", mol="predator", shape="OBJECT", obj_expr="arena", q_expr="1000" )

    cb_model.add_reaction_to_model ( rin="prey", rtype="irreversible", rout="prey + prey", fwd_rate=prey_birth_rate, bkwd_rate="" )
    cb_model.add_reaction_to_model ( rin="prey + predator", rtype="irreversible", rout="predator + predator", fwd_rate=predation_rate, bkwd_rate="" )
    cb_model.add_reaction_to_model ( rin="predator", rtype="irreversible", rout="NULL", fwd_rate=pred_death_rate, bkwd_rate="" )

    bpy.ops.mcell.rxn_output_add()
    mcell.rxn_output.rxn_output_list[0].molecule_name = 'prey'

    bpy.ops.mcell.rxn_output_add()
    mcell.rxn_output.rxn_output_list[1].molecule_name = 'predator'

    mcell.rxn_output.plot_layout = ' '

    mcell.partitions.include = True
    bpy.ops.mcell.auto_generate_boundaries()

    if interaction_radius == None:
        mcell.initialization.interaction_radius.set_expr ( "" )
    else:
        mcell.initialization.interaction_radius.set_expr ( interaction_radius )

    # mcell.run_simulation.simulation_run_control = 'JAVA'
    cb_model.run_model ( iterations=iterations, time_step=time_step, wait_time=wait_time )

    cb_model.compare_mdl_with_sha1 ( mdl_hash )

    cb_model.refresh_molecules()

    scn.frame_current = 10

    cb_model.set_view_back()

    mcell.rxn_output.mol_colors = True

    cb_model.change_molecule_display ( prey, glyph='Cube',       scale=0.2, red=0.0, green=1.0, blue=0.0 )
    cb_model.change_molecule_display ( pred, glyph='Octahedron', scale=0.3, red=1.0, green=0.0, blue=0.0 )

    cb_model.scale_view_distance ( 0.015 )

    return cb_model


class LotkaVolterraTorusTestDiffLimOp(bpy.types.Operator):
    bl_idname = "cellblender_test.lotka_volterra_torus_test_diff_lim"
    bl_label = "Lotka Volterra Torus - Diffusion Limited Reaction"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = LotkaVolterraTorus ( context, prey_birth_rate="8.6e6", predation_rate="1e12", pred_death_rate="5e6", interaction_radius="0.003", time_step="1e-8", iterations="1200", mdl_hash="be2169e601b5148c9d2da24143aae99367bf7f39", wait_time=5.0 )
        cb_model.play_animation()

        return { 'FINISHED' }


class LotkaVolterraTorusTestPhysOp(bpy.types.Operator):
    bl_idname = "cellblender_test.lotka_volterra_torus_test_phys"
    bl_label = "Lotka Volterra Torus - Physiologic Reaction"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = LotkaVolterraTorus ( context, prey_birth_rate="129e3", predation_rate="1e8", pred_death_rate="130e3", interaction_radius=None, time_step="1e-6", iterations="1200", mdl_hash="bd1033a5ec4f6c51c017da4640d5bce7df5cdbd8", wait_time=50.0 )
        cb_model.play_animation()

        return { 'FINISHED' }



class OrganelleTestOp(bpy.types.Operator):
    bl_idname = "cellblender_test.organelle_test"
    bl_label = "Organelle Test"

    def invoke(self, context, event):
        self.execute ( context )
        return {'FINISHED'}

    def execute(self, context):

        cb_model = CellBlender_Model ( context )

        scn = cb_model.get_scene()
        mcell = cb_model.get_mcell()


        # Set some shared parameters
        subdiv = 3


        # Create Organelle 1

        # Create the object and add it to the CellBlender model
        cb_model.add_icosphere_to_model ( name="Organelle_1", draw_type="WIRE", size=0.3, y=-0.25, subdiv=subdiv+1 )
        cb_model.add_surface_region_to_model_by_normal ( "Organelle_1", "top", 0, 1, 0, 0.92 )


        # Create Organelle 2

        # Create the object and add it to the CellBlender model
        cb_model.add_icosphere_to_model ( name="Organelle_2", draw_type="WIRE", size=0.2, y=0.31, subdiv=subdiv+1 )
        cb_model.add_surface_region_to_model_by_normal ( "Organelle_2", "top", 0, -1, 0, 0.8 )


        # Create Cell itself

        cb_model.add_icosphere_to_model ( name="Cell", draw_type="WIRE", size=0.625, subdiv=subdiv )


        # Define the molecule species

        mola = cb_model.add_molecule_species_to_model ( name="a", mol_type="3D", diff_const_expr="1e-6" )
        molb = cb_model.add_molecule_species_to_model ( name="b", mol_type="3D", diff_const_expr="1e-6" )
        molc = cb_model.add_molecule_species_to_model ( name="c", mol_type="3D", diff_const_expr="1e-6" )
        mold = cb_model.add_molecule_species_to_model ( name="d", mol_type="3D", diff_const_expr="1e-6" )

        molt1 = cb_model.add_molecule_species_to_model ( name="t1", mol_type="2D", diff_const_expr="1e-6" )
        molt2 = cb_model.add_molecule_species_to_model ( name="t2", mol_type="2D", diff_const_expr="0" )



        cb_model.add_molecule_release_site_to_model ( name="rel_a",  mol="a",  shape="OBJECT", obj_expr="Cell[ALL] - (Organelle_1[ALL] + Organelle_2[ALL])", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( name="rel_b",  mol="b",  shape="OBJECT", obj_expr="Organelle_1[ALL]", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( name="rel_t1", mol="t1", shape="OBJECT", obj_expr="Organelle_1[top]", orient="'", q_expr="1000" )
        cb_model.add_molecule_release_site_to_model ( name="rel_t2", mol="t2", shape="OBJECT", obj_expr="Organelle_2[top]", orient="'", q_expr="1000" )
        # Add a single c and d molecule so the display values can be set ... otherwise they're not applied properly
        cb_model.add_molecule_release_site_to_model ( mol="c", shape="OBJECT", obj_expr="Organelle_2", q_expr="1" )
        cb_model.add_molecule_release_site_to_model ( mol="d", shape="OBJECT", obj_expr="Organelle_2", q_expr="1" )


        cb_model.add_reaction_to_model ( rin="a + b",    rtype="irreversible", rout="c",        fwd_rate="1e9", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="a' + t1'", rtype="irreversible", rout="a, + t1'", fwd_rate="3e8", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="c' + t2'", rtype="irreversible", rout="d, + t2'", fwd_rate="3e9", bkwd_rate="" )
        cb_model.add_reaction_to_model ( rin="c, + t1'", rtype="irreversible", rout="c' + t1'", fwd_rate="3e8", bkwd_rate="" )


        cb_model.add_reaction_output_to_model ( 'a' )
        cb_model.add_reaction_output_to_model ( 'b' )
        cb_model.add_reaction_output_to_model ( 'c' )
        cb_model.add_reaction_output_to_model ( 'd' )
        #cb_model.add_reaction_output_to_model ( 't1' )
        #cb_model.add_reaction_output_to_model ( 't2' )
        mcell.rxn_output.plot_layout = ' '
        mcell.rxn_output.mol_colors = True


        mcell.partitions.include = True
        bpy.ops.mcell.auto_generate_boundaries()


        cb_model.run_model ( iterations='1000', time_step='1e-6', wait_time=4.0 )

        cb_model.compare_mdl_with_sha1 ( "8f0782e3d8b8deda85cc2275b6168f02d7d9c117" )

        cb_model.refresh_molecules()

        scn.frame_current = 2

        # For some reason, changing some of these molecule display settings crashes Blender (tested for both 2.74 and 2.75)
        cb_model.change_molecule_display ( mola, glyph='Cube', scale=3.0, red=1.0, green=0.0, blue=0.0 )
        #cb_model.change_molecule_display ( molb, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )
        #cb_model.change_molecule_display ( molc, glyph='Cube', scale=6.0, red=1.0, green=1.0, blue=1.0 )

        #cb_model.change_molecule_display ( molt1, glyph='Cone', scale=2.0, red=1.0, green=0.0, blue=0.0 )
        cb_model.change_molecule_display ( molt2, glyph='Cone', scale=1.5, red=0.7, green=0.7, blue=0.0 )


        cb_model.set_view_back()

        cb_model.scale_view_distance ( 0.07 )

        cb_model.play_animation()

        return { 'FINISHED' }





def register():
    print ("Registering ", __name__)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.cellblender_test_suite = bpy.props.PointerProperty(type=CellBlenderTestPropertyGroup)

def unregister():
    print ("Unregistering ", __name__)
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.cellblender_test_suite

if __name__ == "__main__":
    register()


# test call
#bpy.ops.modtst.dialog_operator('INVOKE_DEFAULT')


