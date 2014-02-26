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

"""
This file contains classes supporting CellBlender Parameters.

"""

import bpy
from bpy.props import *

from math import *
from random import uniform, gauss
import parser
import re
import token
import symbol
import sys


import cellblender

# For timing code:
import time


####################### Start of Profiling Code #######################

# From: http://wiki.blender.org/index.php/User:Z0r/PyDevAndProfiling

prof = {}

class profile:
    ''' Function decorator for code profiling.'''
    
    def __init__(self,name):
        self.name = name
    
    def __call__(self,fun):
        def profile_fun(*args, **kwargs):
            start = time.clock()
            try:
                return fun(*args, **kwargs)
            finally:
                duration = time.clock() - start
                if not fun in prof:
                    prof[fun] = [self.name, duration, 1]
                else:
                    prof[fun][1] += duration
                    prof[fun][2] += 1
        return profile_fun

#def print_statistics(c):
def print_statistics():
    '''Prints profiling results to the console. Run from a Python controller.'''

    #if not c.sensors[0].positive:
    #    return

    def timekey(stat):
        return stat[1] / float(stat[2])

    stats = sorted(prof.values(), key=timekey, reverse=True)

    print ( '=== Execution Statistics ===' )
    print ( '{:<55} {:>6} {:>7} {:>6}'.format('FUNCTION', 'CALLS', 'SUM(ms)', 'AV(ms)'))
    for stat in stats:
        print ( '{:<55} {:>6} {:>7.0f} {:>6.2f}'.format(stat[0],stat[2],stat[1]*1000,(stat[1]/float(stat[2]))*1000))


class MCELL_OT_print_profiling(bpy.types.Operator):
    bl_idname = "mcell.print_profiling"
    bl_label = "Print Profiling"
    bl_description = ("Print Profiling Information")
    bl_options = {'REGISTER'}

    def execute(self, context):
        mcell = context.scene.mcell
        print_statistics()
        return {'FINISHED'}

    def invoke(self, context, event):
        print_statistics()
        return {'RUNNING_MODAL'}


class MCELL_OT_clear_profiling(bpy.types.Operator):
    bl_idname = "mcell.clear_profiling"
    bl_label = "Clear Profiling"
    bl_description = ("Clear Profiling Information")
    bl_options = {'REGISTER'}

    def execute(self, context):
        prof.clear()
        return {'FINISHED'}

    def invoke(self, context, event):
        prof.clear()
        return {'RUNNING_MODAL'}


####################### End of Profiling Code #######################



# We use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


def threshold_print_enabled ( thresh ):
    # Items will print if the user selected level is greater than the level in the print statement (thresh)
    #  User setting = 100 -> print everything
    #  User setting =   0 -> print nothing
    return thresh < bpy.context.scene.mcell.cellblender_preferences.debug_level

def threshold_print ( thresh, s, obj=None ):
    # Pass in the optional object when you don't want to convert it to a string before the call (in case it might be expensive)
    #if threshold_print_enabled ( thresh ):
    #    if obj == None:
    #        print ( s )
    #    else:
    #        print ( s + str(obj) )
    pass

def print_info_about_self ( self, thresh, context ):
    #threshold_print ( thresh, "Info:" )
    #threshold_print ( thresh, "  Self: " + str(self) )
    #threshold_print ( thresh, "    Self contains " + str(dir(self)) )
    #threshold_print ( thresh, "__qualname__ = " + str(self.__qualname__) )
    #threshold_print ( thresh, "name = \"" + str(self.name) + "\"" )
    #threshold_print ( thresh, "rna_type = \"" + str(self.rna_type) + "\"" )
    pass


#@profile('get_path_to_parent')
def get_path_to_parent(self_object):
    """ Return the Blender class path to the parent object with regard to the Blender Property Tree System """
    path_to_self = "bpy.context.scene." + self_object.path_from_id()
    #print ( "Path to self = " + path_to_self )
    path_to_parent = path_to_self[0:path_to_self.rfind(".")]
    return path_to_parent

#@profile('get_parent')
def get_parent(self_object):
    """ Return the parent Blender object with regard to the Blender Property Tree System """
    #print ( "top of get_parent" )
    path_to_parent = get_path_to_parent(self_object)
    #print ( "Path to parent = " + path_to_parent )
    parent = eval(path_to_parent)
    return parent



##### vvvvvvvvv   General Parameter Code   vvvvvvvvv

class MCELL_OT_add_parameter(bpy.types.Operator):
    bl_idname = "mcell.add_parameter"
    bl_label = "Add Parameter"
    bl_description = "Add a new parameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.general_parameters.add_parameter(context)
        return {'FINISHED'}
        

class MCELL_OT_remove_parameter(bpy.types.Operator):
    bl_idname = "mcell.remove_parameter"
    bl_label = "Remove Parameter"
    bl_description = "Remove selected parameter"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        status = context.scene.mcell.general_parameters.remove_active_parameter(context)
        if status != "":
            # One of: 'DEBUG', 'INFO', 'OPERATOR', 'PROPERTY', 'WARNING', 'ERROR', 'ERROR_INVALID_INPUT', 'ERROR_INVALID_CONTEXT', 'ERROR_OUT_OF_MEMORY'
            self.report({'ERROR'}, status)
        return {'FINISHED'}


class MCELL_OT_print_general_parameters(bpy.types.Operator):
    bl_idname = "mcell.print_general_parameters"
    bl_label = "Print General Parameters"
    bl_description = "Print all General Parameters to the console"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.mcell.general_parameters.print_all_general_parameters(-1)
        return {'FINISHED'}
        

class MCELL_OT_print_panel_parameters(bpy.types.Operator):
    bl_idname = "mcell.print_panel_parameters"
    bl_label = "Print Panel Params"
    bl_description = "Print all Panel Parameters to the console"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print_numeric_parameter_list ( -1, prefix="", fast=False )
        return {'FINISHED'}
        

class MCELL_OT_print_panel_parameters_fast(bpy.types.Operator):
    bl_idname = "mcell.print_panel_parameters_fast"
    bl_label = "Print Panel Params Fast"
    bl_description = "Print all Panel Parameters to the console without showing their path"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print_numeric_parameter_list ( -1, prefix="", fast=True )
        return {'FINISHED'}
        


class MCELL_UL_draw_parameter(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mcell = context.scene.mcell
        par = mcell.general_parameters.parameter_list[index]
        disp = par.name + " = " + par.expr
        # Try to force None to be 0 ... doesn't seem to work!!
        if par.value == None:
            par.value = "0"
        disp = disp + " = " + par.value
        if par.unit != "":
            disp = disp + " (" + par.unit + ")"
        icon = 'FILE_TICK'
        if not par.valid:
            icon = 'ERROR'
        if item.status:
            icon = 'ERROR'
            disp = disp + "  <= " + item.status
        layout.label(disp, icon=icon)

  
class MCELL_PT_general_parameters(bpy.types.Panel):
    bl_label = "CellBlender - General Parameters"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        #threshold_print (99, "Panel Draw with context.scene.mcell = " + str(context.scene.mcell) + " of type " + str(type(context.scene.mcell)) )

        mcell = context.scene.mcell

        layout = self.layout
        row = layout.row()
        if mcell.general_parameters.param_group_error == "":
            row.label(text="Defined Parameters:", icon='FORCE_LENNARDJONES')
        else:
            row.label(text=mcell.general_parameters.param_group_error, icon='ERROR')

        row = layout.row()
        col = row.column()
        col.template_list("MCELL_UL_draw_parameter", "general_parameters",
                          mcell.general_parameters, "parameter_list",
                          mcell.general_parameters, "active_par_index",
                          rows=5, maxrows=12)
        col = row.column(align=True)
        col.operator("mcell.add_parameter", icon='ZOOMIN', text="")
        col.operator("mcell.remove_parameter", icon='ZOOMOUT', text="")
        if len(mcell.general_parameters.parameter_list) > 0:
            par = mcell.general_parameters.parameter_list[mcell.general_parameters.active_par_index]
            layout.prop(par, "name")
            if len(par.pending_expr) > 0:
                layout.prop(par, "expr")
                row = layout.row()
                row.label(text="Undefined Expression: " + str(par.pending_expr), icon='ERROR')
            else:
                layout.prop(par, "expr")
            layout.prop(par, "unit")
            layout.prop(par, "desc")
        if mcell.cellblender_preferences.debug_level > 0:
            row = layout.row()
            col = row.column()
            col.operator("mcell.print_general_parameters")
            col = row.column()
            col.operator("mcell.print_panel_parameters")
            col = row.column()
            col.operator("mcell.print_panel_parameters_fast")

        row = layout.row()
        col = row.column()
        col.operator("mcell.print_profiling", text="Print Profiling")
        col = row.column()
        col.operator("mcell.clear_profiling", text="Clear Profiling")


# Callbacks for Property updates appear to require global (non-member) functions
# This is circumvented by simply calling the associated member function passed as self

def update_parameter_name ( self, context ):
    """ The "self" passed in is a GeneralParameterProperty object. """
    self.update_name ( context )

def update_parameter_expression ( self, context ):
    """ The "self" passed in is a GeneralParameterProperty object. """
    self.update_expression ( context )


# These are the properties that make up the general parameter classes

class GeneralParameterProperty(bpy.types.PropertyGroup):

    """An instance of this class exists for every general parameter"""

    id = IntProperty(name="ID", default=0, description="Unique ID for each parameter")
    name = StringProperty(name="Name", default="Parameter", description="Unique name for this parameter", update=update_parameter_name)
    expr = StringProperty(name="Expression", default="0", description="Expression to be evaluated for this parameter", update=update_parameter_expression)
    value = StringProperty(name="Value", default="0", description="Current evaluated value for this parameter" )

    last_name = StringProperty(name="Last Name", default="", description="Last value of name (used for comparison to detect changes)")
    last_expr = StringProperty(name="Last Expression", default="", description="Last value of expr (used for comparison to detect changes)")
    last_value = StringProperty(name="Last Value", default="", description="Last value of value (used for comparison to detect changes)")

    id_expr_str = StringProperty(name="EncodedExpressionString", default="", description="Parsed and Encoded Expression list stored as a string")
    
    pending_expr = StringProperty(name="PendingExpression", default="", description="Expression as entered with errors pending correction")

    valid = BoolProperty(default=False) # Transient value used when evaluating all parameters to flag which have been updated

    initialized = BoolProperty(default=False) # Set to true by "set_defaults"

    unit = StringProperty(name="Units", default="", description="Parameter Unit")
    desc = StringProperty(name="Description", default="", description="Parameter Description")

    status = StringProperty(name="Status", default="")  # Normal="", Otherwise contains any error messages
    
    def set_defaults ( self ):
        self.name = "Parameter_" + str(self.id)
        self.expr = "0"
        self.value = "0"
        
        self.last_name = self.name
        self.last_expr = self.expr
        self.last_value = self.value

        self.valid = True
        self.status = ""
        self.initialized = True

    def print_parameter(self, thresh, prefix=""):
        #threshold_print ( thresh, prefix + self.name + " (#" + str(self.id) + ") = " + self.expr + " = " + self.id_expr_str + " = " + str(self.value) )
        pass

    def print_details(self, thresh, prefix=""):
        #threshold_print ( thresh, prefix + "ID = " + str(self.id) )
        #threshold_print ( thresh, prefix + "  Name  = " + self.name + ", previously " + self.last_name )
        #threshold_print ( thresh, prefix + "  Expr  = " + self.expr + ", previously " + self.last_expr )
        #threshold_print ( thresh, prefix + "  IDExp = " + self.id_expr_str )
        #threshold_print ( thresh, prefix + "  _expr = " + self.pending_expr )
        #threshold_print ( thresh, prefix + "  Value = " + str(self.value) )
        #threshold_print ( thresh, prefix + "  Valid = " + str(self.valid) )
        #threshold_print ( thresh, prefix + "  Init  = " + str(self.initialized) )
        #threshold_print ( thresh, prefix + "  Stat  = " + str(self.status) )
        pass

    #@profile('update_name')
    def update_name ( self, context ):
        """
        Update the entire parameter system based on a parameter's name being changed.
        This function is called with a "self" which is a GeneralParameterProperty
        whenever the name is changed (either programatically or via the GUI).
        This function needs to force the redraw of all parameters that depend
        on this one so their expressions show the new name as needed.

        The "self" passed in is a GeneralParameterProperty object.
        """
        #print ( "Top of update name" )
        #threshold_print ( 60, "==================================================================" )
        #threshold_print ( 60, "Updating name for parameter " + self.name )
        if (self.name == self.last_name):
            #threshold_print ( 60, "Names are identical, no change made" )
            pass
        else:
            #threshold_print ( 60, "Names are different, ask parent to change name checking for duplicates" )
            gen_params = get_parent ( self )
            gen_params.name_update_in_progress = True
            
            gen_params.name_change(self)
            
            # Is this needed for a name change?
            gen_params.eval_all_any_order()

            # Update all the panel parameters based on all the general parameters
            plist = get_numeric_parameter_list ( None, [], debug=False )      # <<<<<<<  This could be changed to be just the panel parameters that depend on this one
            # current_numeric_parameter_list = plist
            for p in plist:
                # Fix any potential broken references
                fixed_expression = gen_params.fix_broken_references ( p.param_data.ID_expression )
                if fixed_expression != p.param_data.ID_expression:
                    # Re-evaluate the fixed expression
                    #threshold_print ( 60, "Fixing reference from " + str(p.param_data.ID_expression) + " to " + fixed_expression )
                    p.param_data.ID_expression = fixed_expression

                    value = gen_params.eval_panel_param_ID_expr ( p.param_data.ID_expression )
                    if value == None:
                        #threshold_print ( 5, "Invalid expression detected in update_name!!!" )
                        p.param_data.status = "Invalid Expression"
                    else:
                        if p.param_data.value != value:
                            p.param_data.value = value
                        p.param_data.status = ""
                    
                    p.expression = gen_params.translate_panel_param_ID_expr ( p.param_data.ID_expression )
                # Translate the expression to reflect the new name
                #threshold_print ( 60, "Translating " + str(p.param_data.ID_expression) + " during update_name" )
                expr = gen_params.translate_panel_param_ID_expr ( p.param_data.ID_expression )
                if p.expression != expr:
                    p.expression = expr
            gen_params.name_update_in_progress = False

        #threshold_print ( 60, "Done updating name for parameter " + self.name )
        #threshold_print ( 60, "==================================================================" )
        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
        #print ( "Bottom of update name" )

    #@profile('update_expression')
    def update_expression ( self, context ):
        """ 
        Update the entire parameter system based on a parameter's expression being changed.
        This function is called with a "self" which is a GeneralParameterProperty
        whenever the string expression is changed (either programatically or via the GUI).
        This function needs to force the redraw of all parameters that depend on this
        one so their values are updated as needed.

        The "self" passed in is a GeneralParameterProperty object.
        """
        #print ( "Top of update expression" )
        #threshold_print ( 60, "==================================================================" )
        #threshold_print ( 60, "Inside update_expression with self = " + str(self) )

        gen_params = get_parent ( self )

        if gen_params.name_update_in_progress:
            #threshold_print ( 60, "update_expression not executed because name update is in progress" )
            return

        status = gen_params.expression_change(self)
        if len(status) > 0:
            print ( "Should report this error: " + status )
            # Can't report without being an "operator" and this is through a callback
            #self.report({'ERROR'}, status)
            pass

        # Is this needed? No, it's now done in gen_params.expression_change()  gen_params.eval_all_any_order()

        #threshold_print ( 60, "Inside update_expression, calling print_all_general_parameters()" )
        # gen_params.print_all_general_parameters(60)

        plist = get_numeric_parameter_list ( None, [], debug=False )
        # current_numeric_parameter_list = plist

        for p in plist:
            # Create a string encoded version of the expression (like "#1~+~3~*~(~#2~+~7.0~)")
            id_expr = gen_params.parse_panel_param_expr ( p.expression )
            #threshold_print ( 60, "Inside update_expression, id_expr = " + str(id_expr) )
            if p.param_data.ID_expression != id_expr:
                p.param_data.ID_expression = id_expr
                #threshold_print ( 60, "Changing self.ID_expression to " + str(p.param_data.ID_expression) )
            expr = gen_params.translate_panel_param_ID_expr ( p.param_data.ID_expression )
            if p.expression != expr:
                p.expression = expr
            value = gen_params.eval_panel_param_ID_expr ( p.param_data.ID_expression )
            if value != None:
                if p.param_data.value != value:
                    p.param_data.value = value
        #threshold_print ( 60, "Done updating expression for parameter " + self.name )
        #threshold_print ( 60, "==================================================================" )
        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
        #print ( "Bottom of update expression" )


class MCellParametersPropertyGroup(bpy.types.PropertyGroup):
    """This is the class that encapsulates a group (or list) of general purpose parameters"""
    parameter_list = CollectionProperty(type=GeneralParameterProperty, name="Parameters List")
    active_par_index = IntProperty(name="Active Parameter", default=0)
    param_group_error = StringProperty( default="", description="Error Message for Entire Parameter Group")
    next_id = IntProperty(name="Counter for Unique Parameter IDs", default=1)  # Start ID's at 1 to confirm initialization
    name_update_in_progress = BoolProperty(default=False)  # Used to disable expression evaluation when names are being changed
    batch_add_in_progress = BoolProperty(default=False)  # Used to disable expression evaluation when many new parameters are being added
    # parameter_space_string = StringProperty ( name="ParameterSpace", default="", description="ParameterSpace object pickled as a string" )
    
    """
      String encoding of expression lists:
      
      Rules:
        The tilde character (~) separates all terms
        Any term that does not start with # is a string literal
        Any term that starts with #? is an undefined parameter name
        Any term that starts with # followed by an integer is a parameter ID

      Example:
        Parameter 'a' has an ID of 1
        Parameter 'b' has an ID of 2
        Parameter 'c' is undefined
        Original Expression:  a + 5 + b + c
          Expression as a List: [1, '+', '5', '+', 2, '+', None, 'c' ]
          Expression as string:  #1~+~5~+~#2~+~#?c
    """
    
    @profile('get_term_sep')
    def get_term_sep (self):
        return ( "~" )    # This is the string used to separate terms in an expression. It should be illegal in whatever syntax is being parsed.

    @profile('UNDEFINED_NAME')
    def UNDEFINED_NAME(self):
        return ( "   (0*1111111*0)   " )   # This is a string that evaluates to zero, but is easy to spot in expressions
    
    @profile('get_expression_keywords')
    def get_expression_keywords(self):
        return ( { '^': '**', 'SQRT': 'sqrt', 'EXP': 'exp', 'LOG': 'log', 'LOG10': 'log10', 'SIN': 'sin', 'COS': 'cos', 'TAN': 'tan', 'ASIN': 'asin', 'ACOS':'acos', 'ATAN': 'atan', 'ABS': 'abs', 'CEIL': 'ceil', 'FLOOR': 'floor', 'MAX': 'max', 'MIN': 'min', 'RAND_UNIFORM': 'uniform', 'RAND_GAUSSIAN': 'gauss', 'PI': 'pi', 'SEED': '1' } )

    @profile('encode_expr_list_to_str')
    def encode_expr_list_to_str ( self, expr_list ):
        """ Turns an expression list into a string that can be stored as a Blender StringProperty """
        term_sep = self.get_term_sep()
        expr_str = ""
        next_is_undefined = False
        for e in expr_list:
            if next_is_undefined:
                expr_str += term_sep + '#?' + e
                next_is_undefined = False
            else:
                if type(e) == type(None):
                    next_is_undefined = True
                elif type(e) == int:
                    expr_str += term_sep + "#" + str(e)
                elif type(e) == type("a"):
                    expr_str += term_sep + e
                else:
                    #threshold_print ( 0, "Unexepected type while encoding list: " + str(expr_list) )
                    pass

        if len(expr_str) >= len(term_sep):
            # Remove the first term_sep string (easier here than checking above)
            expr_str = expr_str[len(term_sep):]
        return expr_str


    @profile('decode_str_to_expr_list')
    def decode_str_to_expr_list ( self, expr_str ):
        """ Recovers an expression list from a string that has been stored as a Blender StringProperty """
        expr_list = []
        terms = expr_str.split(self.get_term_sep())
        #threshold_print ( 90, "   ...breaking into terms: " + str(terms) )
        for e in terms:
            #threshold_print ( 90, "  ...checking term: " + str(e) )
            if len(e) > 0:
                #threshold_print ( 90, "  ...storing term: " + str(e) )
                if e[0] == '#':
                    if (len(e) > 1) and (e[1] == '?'):
                        expr_list = expr_list + [None] + [e[2:]]
                    else:
                        expr_list = expr_list + [int(e[1:])]
                else:
                    expr_list = expr_list + [e]
        return expr_list


    @profile('print_all_general_parameters')
    def print_all_general_parameters ( self, thresh, prefix="" ):
        """ Prints all general parameters based on comparison to a user-adjustable threshold """
        #threshold_print ( thresh, prefix + "There are " + str(len(self.parameter_list)) + " general parameters defined" )
        #threshold_print ( thresh, prefix + "  [ name (#id) = expr = idexpr = value ]" )
        for p in self.parameter_list:
            p.print_parameter( thresh, prefix=prefix+"    " )


    @profile('fix_broken_references')
    def fix_broken_references ( self, id_expr_str ):
        """ Attempts to fix any broken references in this expression by searching for names """
        if "#?" in id_expr_str:
            # This indicates that there is at least one broken reference in the string, so convert to a list and fix
            expr_list = self.decode_str_to_expr_list ( id_expr_str )
            fixed_list = []
            last_none = False
            for term in expr_list:
                if last_none:
                    # The previous term was none, so try to evaluate this term as a name
                    found = False
                    for q in self.parameter_list:
                        if term.strip() == q.name.strip():
                            # Add the id to the list as an integer index
                            fixed_list.append ( int(q.id) )
                            found = True
                            break
                    if not found:
                        # The name wasn't found, so keep it as an undefined name
                        fixed_list.append ( None )
                        fixed_list.append ( term )
                    last_none = False
                elif term == None:
                    # Flag the next term as a name to try to evaluate
                    last_none = True
                else:
                    # Just add this term to the list
                    fixed_list.append ( term )
            return ( self.encode_expr_list_to_str(fixed_list) )
        else:
            return ( id_expr_str )

    @profile('fix_all_broken_references')
    def fix_all_broken_references ( self ):
        """ Attempts to fix all broken references """
        for p in self.parameter_list:
            p.id_expr_str = self.fix_broken_references ( p.id_expr_str )


    @profile('build_name_ID_dict')
    def build_name_ID_dict ( self ):
        """ Builds a dictionary mapping parameter names to their IDs """
        name_ID_dict = {}
        for p in self.parameter_list:
            name_ID_dict.update ( { p.name : p.id } )
        return name_ID_dict

    @profile('build_ID_name_dict')
    def build_ID_name_dict ( self ):
        """ Builds a dictionary mapping parameter IDs to their names """
        ID_name_dict = {}
        for p in self.parameter_list:
            ID_name_dict.update ( { p.id : p.name } )
        return ID_name_dict

    @profile('build_ID_value_dict')
    def build_ID_value_dict ( self ):
        """ Builds a dictionary mapping parameter IDs to their values """
        ID_value_dict = {}
        for p in self.parameter_list:
            ID_value_dict.update ( { p.id : p.value } )
        return ID_value_dict

    @profile('load_ID_value_dict')
    def load_ID_value_dict ( self, ID_value_dict, ID_valid_dict ):
        """ Uses a Python dictionary to update values into the parameter properties """
        for p in self.parameter_list:
            if p.id in ID_value_dict:
                p.value = ID_value_dict[p.id]
            if p.id in ID_valid_dict:
                if ID_valid_dict[p.id]:
                    p.status = ""
                else:
                    p.status = "Evaluation Error"

    @profile('build_ID_valid_dict')
    def build_ID_valid_dict ( self, is_valid ):
        """ Builds a dictionary mapping each parameter ID to the is_valid value """
        ID_valid_dict = {}
        for p in self.parameter_list:
            ID_valid_dict.update ( { p.id : is_valid } )
        return ID_valid_dict

    @profile('build_depend_list_dict')
    def build_depend_list_dict ( self ):
        """ Builds a dictionary containing ID:[dependency_list] pairs for all parameters """
        dep_list_dict = {}
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            dep_list_p = []
            for e in expr_list:
                if (type(e) == int) or (e == None):
                    dep_list_p = dep_list_p + [e]
            dep_list_dict.update ( { p.id : dep_list_p } )
        return dep_list_dict

    @profile('used_by_other_general_parameters')
    def used_by_other_general_parameters ( self, id ):
        """ Return a boolean reflecting whether any general parameters use this parameter id (True) or not (False) """
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            if id in expr_list:
                return True
        return False

    @profile('used_by_these_general_parameters')
    def used_by_these_general_parameters ( self, id ):
        """ Return a string of names of any general parameters that use this parameter id """
        name_list = ""
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            if id in expr_list:
                if len(name_list) > 0:
                    name_list = name_list + ","
                name_list = name_list + p.name
        return name_list

    @profile('used_by_panel_parameters')
    def used_by_panel_parameters ( self, id ):
        """ Return a boolean reflecting whether any panel parameters use this parameter id (True) or not (False) """
        plist = get_numeric_parameter_list ( None, [] )
        for p in plist:
            expr_list = self.decode_str_to_expr_list ( p.get_ID_expression() )
            if id in expr_list:
                return True
        return False

    @profile('used_by_these_panel_parameters')
    def used_by_these_panel_parameters ( self, id ):
        """ Return a string of names of any panel parameters that use this parameter id """
        name_list = ""
        plist = get_numeric_parameter_list ( None, [] )
        plist_names = str(plist)[1:-1].split(",")
        for i in range(len(plist)):
            p = plist[i]
            expr_list = self.decode_str_to_expr_list ( p.get_ID_expression() )
            if id in expr_list:
                if len(name_list) > 0:
                    name_list = name_list + ","
                name_list = name_list + plist_names[i].split(".")[-1]
        return name_list

    @profile('used_by_any_other_parameters')
    def used_by_any_other_parameters ( self, id ):
        return self.used_by_other_general_parameters(id) | self.used_by_panel_parameters(id)

    @profile('used_by_these_other_parameters')
    def used_by_these_other_parameters ( self, id ):
        gpu = self.used_by_these_general_parameters(id)
        ppu = self.used_by_these_panel_parameters(id)
        apu = ""
        if (len(gpu) > 0) and (len(ppu) > 0):
            apu = gpu + "," + ppu
        else:
            apu = gpu + ppu
        return apu


    @profile('build_ID_pyexpr_dict')
    def build_ID_pyexpr_dict ( self, ID_name_dict ):
        """ Construct a dictionary containing python executable string representations of the expressions by substituting symbols for IDs """
        #threshold_print ( 90, "Inside build_ID_pyexpr_dict ... " )
        expression_keywords = self.get_expression_keywords()
        ID_pyexpr_dict = {}
        for p in self.parameter_list:
            expr_list = self.decode_str_to_expr_list ( p.id_expr_str )
            expr = ""
            if None in expr_list:
                expr = None
            else:
                for token in expr_list:
                    if type(token) == int:
                        # This is an integer parameter ID, so look up the variable name to concatenate
                        if token in ID_name_dict:
                            expr = expr + ID_name_dict[token]
                        else:
                            # In previous versions, this case might have defined a new parameter here.
                            # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                            ####  threshold_print ( 5, "build_ID_pyexpr_dict adding an undefined name to " + expr )
                            #threshold_print ( 1, "build_ID_pyexpr_dict did not find " + str(token) + " in " + str(ID_name_dict) + ", adding an undefined name flag to " + expr )
                            expr = expr + self.UNDEFINED_NAME()
                    else:
                        # This is a string so simply concatenate it after translation as needed
                        if token in expression_keywords:
                            expr = expr + expression_keywords[token]
                        else:
                            expr = expr + token
            ID_pyexpr_dict.update ( { p.id : expr } )
        return ID_pyexpr_dict


    @profile('build_expr_str')
    def build_expr_str ( self, encoded_ID_expr, ID_name_dict, to_python=False ):
        """ Translate an encoded ID expression string into a human-readable expression string with respect to current parameters """
        """ The to_python flag is used to generate a python executable string rather than the default MDL compatible string """
        #threshold_print ( 60, "Inside build_expr_str ... translating " + str(encoded_ID_expr) )
        #threshold_print ( 60, "  using dictionary: " + str(ID_name_dict) )
        new_expr = ""
        expr_list = self.decode_str_to_expr_list ( encoded_ID_expr )
        next_is_undefined = False
        # __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
        expression_keywords = self.get_expression_keywords()
        for token in expr_list:
            if token == None:
                next_is_undefined = True
            elif type(token) == int:
                # This is an integer parameter ID, so look up the variable name to concatenate
                if token in ID_name_dict:
                    new_expr = new_expr + ID_name_dict[token]
                else:
                    # In previous versions, this case might have defined a new parameter here.
                    # In this version, it should never happen, but appends an undefined name flag ... just in case!!
                    #threshold_print ( 1, "build_expr_str did not find " + str(token) + " in " + str(ID_name_dict) + ", adding an undefined name flag to " + new_expr )
                    new_expr = new_expr + self.UNDEFINED_NAME()
            else:
                # This is a string so simply concatenate it
                next_part = token
                if to_python:
                    if token in expression_keywords:
                        next_part = expression_keywords[token]
                if next_is_undefined:
                    new_expr = new_expr + next_part
                    next_is_undefined = False
                else:
                    new_expr = new_expr + next_part

        #threshold_print ( 60, "Returning from build_exp_str with     " + str(new_expr) )
        return new_expr


    @profile('name_change')
    def name_change ( self, param ):
        """ Change the name of a parameter and reflect the change in all expressions. This does not change any values. """
        #threshold_print ( 60, "MCellParametersPropertyGroup.name_change() called by parameter " + param.name + ":" )
        param.print_details ( 60, prefix="  " )
        #threshold_print ( 60, "  All other parameters:" )
        for p in self.parameter_list:
            p.print_details( 60, prefix="    " )
        # Assume name is OK, then test for various illegal conditions
        name_ok = True
        # Check to see if the new name is legal
        if not param.name.isidentifier():
            name_ok = False
        # Check to see if the new name already exists
        """
        if self.parameter_list.get(param.name) != None:
            name_ok = False
            #threshold_print ( 20, " Name conflict between " + param.name + " and " + p.name )
        """
        for p in self.parameter_list:
            # p.print_details( 40, prefix="  " )
            if param.name == p.name:
                if param != p:
                    name_ok = False
                    #threshold_print ( 20, " Name conflict between " + param.name + " and " + p.name )
                    break
        if not name_ok:
            #threshold_print ( 0, "Error: Name is not legal or duplicates another name, reverting to previous" )
            param.name = param.last_name
        else:
            param.last_name = param.name
            # Update all parameter expressions to reflect the new name
            ID_name_dict = self.build_ID_name_dict()
            for p in self.parameter_list:
                #threshold_print ( 60, "Inside name_change, building a new expression from " + p.id_expr_str + " and the current ID_name_dict" )
                new_expr = self.build_expr_str ( p.id_expr_str, ID_name_dict )
                # To prevent infinite recursion, only update the expression if it differs from the current one
                if p.expr != new_expr:
                    # The expression differs, so change it. NOTE: This triggers an update of the parameter!!
                    p.expr = new_expr
        # Re-evaluate all the parameters to force them to redraw their expressions
        self.eval_all_any_order()
        # Note that updating of the panel parameters is done after calling this function


    @profile('expression_change')
    def expression_change ( self, param ):
        """ Change the expression of a parameter and reflect the change in all expressions. This can change values. """
        #threshold_print ( 60, "MCellParametersPropertyGroup.expression_change() called by parameter " + param.name + ":" )
        status = ""
        expr_list = self.parse_param_expr ( param.expr )
        if None in expr_list:
            param.status = "Undefined variables in " + str(param.expr)
            #threshold_print ( 1, "Undefined variables in expression: " + param.expr )
        else:
            param.status = ""
        # Store the ID expression string back in the parameter
        param.id_expr_str = self.encode_expr_list_to_str ( expr_list )
        new_expr = self.translate_panel_param_ID_expr ( param.id_expr_str )
        if param.expr != new_expr:
            param.expr = new_expr
        #threshold_print ( 60, "After update: expr = " + param.expr + ", id_expr = " + param.id_expr_str )
        # Re-evaluate all the parameters
        self.eval_all_any_order()
        return status


    @profile('parse_panel_param_expr')
    def parse_panel_param_expr ( self, panel_param_expr ):
        """ Convert a string expression into an encoded ID expression string with respect to current parameters """
        return self.encode_expr_list_to_str ( self.parse_param_expr(panel_param_expr) )

    @profile('translate_panel_param_ID_expr')
    def translate_panel_param_ID_expr ( self, panel_param_ID_expr, to_python=False ):
        """ Translate a panel parameter's encoded ID expression into a string for display """
        #threshold_print ( 60, "Inside translate_panel_param_ID_expr: Translating expression " + str(panel_param_ID_expr ) )
        return self.build_expr_str ( panel_param_ID_expr, self.build_ID_name_dict(), to_python )

    @profile('eval_panel_param_ID_expr')
    def eval_panel_param_ID_expr ( self, panel_param_ID_expr ):
        """ Evaluate a panel parameter's ID expression (like "#1~+~3~*~(~#2~+~7.0~)") into a numeric value or None if invalid """
        #threshold_print ( 60, "Evaluating ID expression " + str(panel_param_ID_expr) )
        expr_list = self.decode_str_to_expr_list(panel_param_ID_expr)
        #threshold_print ( 60, "  Expression: " + str(panel_param_ID_expr) + " evaluates to list: " + str(expr_list) )
        (value,valid) = (None,False)
        if not (None in expr_list):
            (value,valid) = self.eval_all_any_order ( expression = self.translate_panel_param_ID_expr ( panel_param_ID_expr, to_python=True ) )
        return value

    @profile('eval_all_any_order')
    def eval_all_any_order ( self, prnt=False, requested_id=None, expression=None ):
        """ Evaluate all parameters based on dependencies without assuming any order of definition """
        if self.batch_add_in_progress:
            return (0,False)

        # from math import *
        from math import sqrt, exp, log, log10, sin, cos, tan, asin, acos, atan, ceil, floor, pi  # abs, max, and min are not from math?
        from random import uniform, gauss

        # Start by trying to fix any broken references

        self.fix_all_broken_references()
        
        # Build the working dictionaries needed for evaluation (built from Blender's Properties)

        ID_name_dict = self.build_ID_name_dict()
        ID_value_dict = self.build_ID_value_dict()
        ID_valid_dict = self.build_ID_valid_dict(False)
        dep_list_dict = self.build_depend_list_dict()
        ID_py_expr_dict = self.build_ID_pyexpr_dict ( ID_name_dict )

        requested_val = 0
        valid = True

        # Loop through all parameters over and over evaluating those parameters with valid dependencies
        
        num_passes = 0

        while (num_passes <= len(ID_name_dict)) and (False in ID_valid_dict.values()):

            num_passes = num_passes + 1

            # Visit each parameter
            for parid in ID_name_dict:
            
                # ID_valid_dict[parid] = True   # Used for performance testing to skip all this code

                # Only need to update parameters with invalid values
                if not ID_valid_dict[parid]:

                    # Check to see if this parameter can be updated based on ALL of its dependencies being valid
                    dep_list = dep_list_dict[parid]   # May contain "None" values which indicate unresolved references
                    
                    dep_satisfied = True
                    if None in dep_list:
                        # This parameter cannot be evalated regardless of any other dependencies being satisfied
                        dep_satisfied = False
                    else:
                        # Check to see if everything this parameter depends on is valid
                        dep_satisfied = True
                        for dep_id in dep_list:
                            if not ID_valid_dict[dep_id]:
                                dep_satisfied = False
                                break

                    if dep_satisfied:
                        # It's OK to evaluate this parameter
                        
                        something_changed = False
                        py_statement = ""
                        try:
                            if (len(str(ID_name_dict[parid]).strip()) <= 0) or (len(str(ID_py_expr_dict[parid]).strip()) <= 0):
                                val = 0
                                #threshold_print ( 20, "Empty name or expression: \"" + str(ID_name_dict[parid]) + " = " + str(ID_py_expr_dict[parid]) + "\"" )
                            else:
                                #py_statement = str(str(self.get_name(parid))) + " = " + str(self.get_expr ( parid, to_py=True ))
                                py_statement = str(ID_name_dict[parid]) + " = " + str(ID_py_expr_dict[parid])
                                #threshold_print ( 90, "About to exec: " + py_statement )
                                exec ( py_statement )
                                val = eval ( ID_name_dict[parid], locals() )
                            
                            # Check for changes ...
                            if parid in ID_value_dict:
                                # The parameter is already there, so check if it's different
                                if str(val) != ID_value_dict[parid]:
                                    something_changed = True
                            else:
                                # If it wasn't there, then this is a change!!
                                something_changed = True

                            ID_value_dict.update ( { parid : str(val) } )
                            if (requested_id == parid):
                                requested_val = val
                        except:
                            valid = False
                            #threshold_print ( 0, "==> Evaluation Exception for " + py_statement + ": " + str ( sys.exc_info() ) )
                            if prnt:
                                #threshold_print ( 0, "  Error in statement:   " + self.get_name(parid) + " = " + self.get_error(parid) )
                                #threshold_print ( 0, "    ... interpreted as: " + py_statement )
                                pass

                        ID_valid_dict[parid] = True

                    # End If
                # End If
            # End For
        # End While

        if expression != None:
            # Evaluate the requested expression in the context of the variables that have already been evaluated:
            try:
                requested_val = 0
                if len(expression.strip()) > 0:
                    val = eval ( expression, locals() )
                    requested_val = val
            except:
                valid = False
                #threshold_print ( 0, "==> Evaluation Exception for requested expression " + expression + ": " + str ( sys.exc_info() ) )
                if prnt:
                    #threshold_print ( 0, "  Error in requested statement:   " + expression )
                    pass

        # Load the updated values back into the Properties
        self.load_ID_value_dict ( ID_value_dict, ID_valid_dict )

        return ( requested_val, valid )


    @profile('new_parameter')
    def new_parameter ( self ):
        """ Add a new parameter to the list of parameters """
        new_par = self.parameter_list.add()
        new_par.id = self.allocate_available_id()
        new_par.set_defaults()
        return new_par

    @profile('start_batch_addition')
    def start_batch_addition ( self ):
        """ Disable evaluation of parameters while they are added """
        self.batch_add_in_progress = True
        return

    @profile('finish_batch_addition')
    def finish_batch_addition ( self ):
        """ Enable evaluation of parameters """
        self.batch_add_in_progress = False
        self.eval_all_any_order()
        return

    @profile('add_parameter_with_values')
    def add_parameter_with_values ( self, name, expression, units, description ):
        """ Add a new parameter to the list of parameters """
        p = self.new_parameter()
        p.name = name
        p.expr = expression
        p.unit = units
        p.desc = description
        return p

    @profile('add_parameter')
    def add_parameter ( self, context ):
        """ Add a new parameter to the list of parameters and set as the active parameter """
        p = self.new_parameter()
        self.active_par_index = len(self.parameter_list)-1
        return p

    @profile('remove_active_parameter')
    def remove_active_parameter ( self, context ):
        """ Remove the active parameter from the list of parameters if not needed by others """
        status = ""
        if len(self.parameter_list) > 0:
            if self.used_by_any_other_parameters(self.parameter_list[self.active_par_index].id):
                status = "Parameter is needed by: " + self.used_by_these_other_parameters(self.parameter_list[self.active_par_index].id)
            else:
                self.parameter_list.remove ( self.active_par_index )
                self.active_par_index -= 1
                if self.active_par_index < 0:
                    self.active_par_index = 0
        return ( status )

    @profile('allocate_available_id')
    def allocate_available_id ( self ):
        """ Return a unique parameter ID for a new parameter """
        if len(self.parameter_list) <= 0:
            # Reset the ID to 1 when there are no more parameters
            self.next_id = 1
        self.next_id += 1
        return ( self.next_id - 1 )


    @profile('parse_param_expr')
    def parse_param_expr ( self, param_expr ):
        """ Converts a string expression into a list expression with:
                 variable id's as integers,
                 None preceding undefined names
                 all others as strings
            Returns either a list (if successful) or None if there is an error

            Examples:

              Expression: "A * (B + C)" becomes something like: [ 3, "*", "(", 22, "+", 5, ")", "" ]
                 where 3, 22, and 5 are the ID numbers for parameters A, B, and C respectively

              Expression: "A * (B + C)" when B is undefined becomes: [ 3, "*", "(", None, "B", "+", 5, ")", "" ]

              Note that the parsing may produce empty strings in the list which should not cause any problem.
        """
        
        name_ID_dict = self.build_name_ID_dict()

        param_expr = param_expr.strip()

        if len(param_expr) == 0:
            return []

        st = None
        pt = None
        try:
            st = parser.expr(param_expr)
            pt = st.totuple()
        except:
            #threshold_print ( 0, "==> Parsing Exception: " + str ( sys.exc_info() ) )
            pass

        parameterized_expr = None  # param_expr
        if pt != None:
        
            parameterized_expr = self.recurse_tree_symbols ( name_ID_dict, pt, [] )
            
            if parameterized_expr != None:
            
                # Remove trailing empty strings from parse tree - why are they there?
                while len(parameterized_expr) > 0:
                    if parameterized_expr[-1] != '':
                        break
                    parameterized_expr = parameterized_expr[0:-2]

        return parameterized_expr


    @profile('recurse_tree_symbols')
    def recurse_tree_symbols ( self, name_ID_dict, pt, current_expr ):
        """ Recurse through the parse tree looking for "terminal" items which are added to the list """

        expression_keywords = self.get_expression_keywords()

        if type(pt) == tuple:
            # This is a tuple, so find out if it's a terminal leaf in the parse tree

            #threshold_print ( 95, "recurse_tree_symbols with a tuple (" + str(current_expr) + ")" )
            #threshold_print ( 95, "  pt = " + str(pt) )

            terminal = False
            if len(pt) == 2:
                if type(pt[1]) == str:
                    terminal = True

            if terminal:
                # This is a 2-tuple with a type and value
                if pt[0] == token.NAME:
                    if pt[1] in expression_keywords:
                        # This is a recognized name and not a user-defined symbol, so append the string itself
                        return current_expr + [ pt[1] ]
                    else:
                        # This must be a user-defined symbol, so check it it's in the dictionary
                        if pt[1] in name_ID_dict:
                            # Append the integer ID to the list
                            return current_expr + [ name_ID_dict[pt[1]] ]
                        else:
                            # Not in the dictionary, so append a None flag followed by the undefined name
                            return current_expr + [ None, pt[1] ]
                else:
                    # This is a non-name part of the expression
                    return current_expr + [ pt[1] ]
            else:
                # Break it down further
                for i in range(len(pt)):
                    next_segment = self.recurse_tree_symbols ( name_ID_dict, pt[i], current_expr )
                    if next_segment != None:
                        current_expr = next_segment
                return current_expr
        return None

##### ^^^^^^^^^   General Parameter Code   ^^^^^^^^^



##### vvvvvvvvv   Panel Parameter Code   vvvvvvvvv

# These are the classes that make up panel parameters

#    """
#    This is the callback function for all panel parameters.
#    This function should do all of the generic parsing and
#    updating and then call a specific user update callback
#    function to do any special processing with the result.
#    """

#@profile('update_PanelParameter')
def update_PanelParameter ( self, context ):

    #print ( "1 - top of call to update_PanelParameter" )

    #threshold_print ( 60, "update_PanelParameter called" )
    #threshold_print ( 60, "  self.expression = " + str(self.expression) )
    #threshold_print ( 60, "  self.param_data.value = " + str(self.param_data.value) )
    
    mcell = context.scene.mcell
    gen_params = mcell.general_parameters
    
    # Always test values first before setting to avoid infinite recursion since setting triggers re-evaluation
    
    # Create a string encoded version of the expression (like "#1~+~3~*~(~#2~+~7.0~)")
    id_expr = gen_params.parse_panel_param_expr ( self.expression )
    #threshold_print ( 60, "update_PanelParameter with id_expr = " + str(id_expr) )
    if self.param_data.ID_expression != id_expr:
        self.param_data.ID_expression = id_expr
        #threshold_print ( 60, "changing self.param_data.ID_expression to " + str(self.param_data.ID_expression) )
    expr = gen_params.translate_panel_param_ID_expr ( self.param_data.ID_expression )
    if self.expression != expr:
        self.expression = expr
    value = gen_params.eval_panel_param_ID_expr ( self.param_data.ID_expression )
    if value == None:
        #threshold_print ( 5, "Invalid expression detected in update_PanelParameter!!!" )
        self.param_data.status = "Invalid Expression: " + expr
    else:
        if self.param_data.value != value:
            self.param_data.value = value
        self.param_data.status = ""

    #threshold_print ( 60, " After Automatic Update:" )
    #threshold_print ( 60, "  self.expression = " + str(self.expression) )
    #threshold_print ( 60, "  self.param_data.value = " + str(self.param_data.value) )

    #get_parent(self).update()

    #print ( "2 - before call to get_parent(self).update(), value of \"" + expr + "\" = " + str(value) )
    #   temp_parent = get_parent(self)
    #print ( "3 - between call to get_parent(self).update()" )
    #   temp_parent.update()
    self.update()
    #print ( "4 - after call to get_parent(self).update()\n" )

    #threshold_print ( 60, " After User Update:" )
    #threshold_print ( 60, "  self.expression = " + str(self.expression) )
    #threshold_print ( 60, "  self.value = " + str(self.value) )

    #print ( "5 - bottom of call to update_PanelParameter" )
    


class PanelParameterData(bpy.types.PropertyGroup):
    # This class contains data that might have been better stored in the PanelParameter class,
    #  but for some reason, it was not able to be accessed there by subclasses.

    status = StringProperty(name="status", default="")

    # The expression itself has been moved out of PanelParameterData so it can get a custom description as a tool tip.
    # expression = StringProperty(name="expression", default="0", description="Panel Parameter Expression.", update=update_PanelParameter)
    ID_expression = StringProperty(name="ID_expression", default="0")
    value = FloatProperty(name="value", default=0)
    label = StringProperty(name="label", default="Parameter")

    min_set = bpy.props.BoolProperty(name="min_set", default=False)
    max_set = bpy.props.BoolProperty(name="max_set", default=False)
    min_value = FloatProperty(name="min_value", default=0)
    max_value = FloatProperty(name="max_value", default=1)
    

class PanelParameter(bpy.types.PropertyGroup):
    # For some reason, subclassing this class inherits functions, but not Properties. Is this a Blender/Python inconsistency?
    # Otherwise, the "param_data" would be here rather than in the subclasses.  : (

    def get_status(self):
        return str(self.param_data.status)
    def append_status(self, stat_string):
        self.param_data.status = self.param_data.status + "   " + stat_string
    def set_status_ok(self):
        self.param_data.status = ""
    def is_status_ok(self):
        return len(self.param_data.status) == 0

    def set_label(self, label):
        self.param_data.label = label
    def get_label(self):
        return str(self.param_data.label)

    def set_expression(self, expr):
        self.expression = expr
        return True
    def get_expression(self):
        return str(self.expression)

    def get_ID_expression(self):
        return str(self.param_data.ID_expression)

    def get_value(self):
        return float(self.param_data.value)

    def get_text(self):
        """ Default string expression for parameters ... overload for different functionality """
        return (  self.get_expression() + " = " + str(self.get_value()) )

    def get_formatted_string(self):
      return "PanelParameter " + self.get_label() + " = " + self.get_ID_expression() + " = " + self.get_expression() + " = " + '{:g}'.format(self.get_value() )


    def set_fields(self, label=None, expr=None, min_val=None, max_val=None):
        if label != None:
            self.set_label(label)
        if expr != None:
            self.set_expression(expr)
        if min_val != None:
            self.param_data.min_value = min_val
            self.param_data.min_set = True
        if max_val != None:
            self.param_data.max_value = max_val
            self.param_data.max_set = True
        return True

    def update(self):
        #threshold_print ( 90, "   Default PanelParameter.update() function ... overload for functionality" )
        """#plist = get_numeric_parameter_list ( None, [] )
        if threshold_print_enabled(95):
            #threshold_print ( 95, "     List of all panel parameters:" )
            #for pp in plist:
            #    threshold_print ( 95, pp )
            #plist_names = str(plist)[1:-1].split(",")
            #for pp in plist_names:
            #    threshold_print ( 95, "       " + pp.strip() )
            #for i in range(len(plist)):
            #    threshold_print ( 95, "      " + plist_names[i].strip() + " = " + str(plist[i].get_value()) )
        """
        pass

    def draw_in_new_row(self, layout):
        """ Default drawing for parameters ... overload for different functionality """
        # print ( self.expression.description ) # Attempting to get ahold of the description tool tip data ... failed
        row = layout.row()
        value = self.get_value()
        if (self.expression == None) or (self.expression == ''):
            row.prop ( self, "expression", text=self.param_data.label+" (Undefined)" )
        else:
            row.prop ( self, "expression", text=self.param_data.label+" = "+'{:g}'.format(value) )
        if not self.is_status_ok():
            row = layout.row()
            row.label(icon='ERROR', text=self.param_data.status)
        else:
            if self.param_data.min_set:
                if value < self.param_data.min_value:
                    row = layout.row()
                    row.label(icon='ERROR', text="Warning: Value of " + str(value) + " for " + self.get_label() + " is less than minimum of "+str(self.param_data.min_value))
            if self.param_data.max_set:
                if value > self.param_data.max_value:
                    row = layout.row()
                    row.label(icon='ERROR', text="Warning: Value of " + str(value) + " for " + self.get_label() + " is greater than maximum of "+str(self.param_data.max_value))



#This is the normal PanelParameterFloat that inherits from PanelParameter

class PanelParameterFloat(PanelParameter):
    """ Simple (but useful) subclass of PanelParameter """
    param_data = PointerProperty(type=PanelParameterData)
    expression = StringProperty(name="Parameter", default="0",
                 description="Generic Float Parameter - Please report missing tool tip.",
                 update=update_PanelParameter)


class PanelParameterInt(PanelParameter):
    """ Simple (but useful) subclass of PanelParameter """
    param_data = PointerProperty(type=PanelParameterData)
    expression = StringProperty(name="Parameter", default="0",
                 description="Generic Int Parameter - Please report missing tool tip.",
                 update=update_PanelParameter)
    # Over-ride the "get_value" function to return an integer
    def get_value(self):
        return int(self.param_data.value)


"""
class PanelParameterFloat(bpy.types.PropertyGroup):
    # This is a "hard-coded" version of PanelParameterFloat that doesn't inherit from PanelParameter

    param_data = PointerProperty(type=PanelParameterData)
    expression = StringProperty(name="Parameter", default="0",
                 description="Generic Float Parameter - Please report missing tool tip.",
                 update=update_PanelParameter)

    def get_status(self):
        return str(self.param_data.status)
    def append_status(self, stat_string):
        self.param_data.status = self.param_data.status + "   " + stat_string
    def set_status_ok(self):
        self.param_data.status = ""
    def is_status_ok(self):
        return len(self.param_data.status) == 0

    def set_label(self, label):
        self.param_data.label = label
    def get_label(self):
        return str(self.param_data.label)

    def set_expression(self, expr):
        self.expression = expr
        return True
    def get_expression(self):
        return str(self.expression)

    def get_ID_expression(self):
        return str(self.param_data.ID_expression)

    def get_value(self):
        return float(self.param_data.value)

    def get_text(self):
        # Default string expression for parameters ... overload for different functionality
        return (  self.get_expression() + " = " + str(self.get_value()) )

    def get_formatted_string(self):
      return "PanelParameter " + self.get_label() + " = " + self.get_ID_expression() + " = " + self.get_expression() + " = " + '{:g}'.format(self.get_value() )


    def set_fields(self, label=None, expr=None, min_val=None, max_val=None):
        if label != None:
            self.set_label(label)
        if expr != None:
            self.set_expression(expr)
        if min_val != None:
            self.param_data.min_value = min_val
            self.param_data.min_set = True
        if max_val != None:
            self.param_data.max_value = max_val
            self.param_data.max_set = True
        return True

    def update(self):
        #threshold_print ( 90, "   Default PanelParameter.update() function ... overload for functionality" )
        #plist = get_numeric_parameter_list ( None, [] )
        #if threshold_print_enabled(95):
        #    #threshold_print ( 95, "     List of all panel parameters:" )
        #    #for pp in plist:
        #    #    threshold_print ( 95, pp )
        #    #plist_names = str(plist)[1:-1].split(",")
        #    #for pp in plist_names:
        #    #    threshold_print ( 95, "       " + pp.strip() )
        #    #for i in range(len(plist)):
        #    #    threshold_print ( 95, "      " + plist_names[i].strip() + " = " + str(plist[i].get_value()) )
        
        pass

    def draw_in_new_row(self, layout):
        # Default drawing for parameters ... overload for different functionality
        # print ( self.expression.description ) # Attempting to get ahold of the description tool tip data ... failed
        row = layout.row()
        value = self.get_value()
        if (self.expression == None) or (self.expression == ''):
            row.prop ( self, "expression", text=self.param_data.label+" (Undefined)" )
        else:
            row.prop ( self, "expression", text=self.param_data.label+" = "+'{:g}'.format(value) )
        if not self.is_status_ok():
            row = layout.row()
            row.label(icon='ERROR', text=self.param_data.status)
        else:
            if self.param_data.min_set:
                if value < self.param_data.min_value:
                    row = layout.row()
                    row.label(icon='ERROR', text="Warning: Value of " + str(value) + " for " + self.get_label() + " is less than minimum of "+str(self.param_data.min_value))
            if self.param_data.max_set:
                if value > self.param_data.max_value:
                    row = layout.row()
                    row.label(icon='ERROR', text="Warning: Value of " + str(value) + " for " + self.get_label() + " is greater than maximum of "+str(self.param_data.max_value))
"""

depth_in_get_num_param_list = 0

# current_numeric_parameter_list = None

@profile('get_numeric_parameter_list')
def get_numeric_parameter_list ( objpath, plist, debug=False ):
    """ Recursive routine that builds a list of numeric (PanelParameterInt and PanelParameterFloat) parameters """
    #global current_numeric_parameter_list
    #if current_numeric_parameter_list != None:
    #    return plist

    global depth_in_get_num_param_list
    depth_to_print = -100
    
    if depth_in_get_num_param_list < depth_to_print:
        if objpath == None:
            print ( "=======================================================================" )
        print ( "Call to             get_numeric_parameter_list with " + str(objpath) )

    depth_in_get_num_param_list += 1
    
    # print ( "Top of get_numeric_parameter_list" )
    #threshold_print ( 98, "get_numeric_parameter_list() called with objpath = ", objpath )

    # This check can be used to speed up parameter searching in the future, but hasn't been critical so far

    if objpath != None:
        if objpath.endswith("rna_type") or objpath.endswith("mcell.mol_viz.mol_file_list"):
            # Don't search anything that is of type "rna_type" or is an mcell.mol_viz.mol_file_list
            depth_in_get_num_param_list += -1
            if depth_in_get_num_param_list < depth_to_print:
                #print ( "Return from call to get_numeric_parameter_list with " + str(objpath) )
                pass
            return plist

    if objpath == None:
        # Start with default path
        objpath = "bpy.context.scene.mcell"
    obj = eval(objpath)
    #threshold_print ( 95, "Path = " + str(objpath) + ", obj = ", obj )
    #threshold_print ( 98, "  plist = ", plist )


    if isinstance(obj,bpy.types.PanelParameter):
        # This is what we're looking for, so add it to the list (although this doesn't seem to happen!!)
        plist.append ( obj )
        #threshold_print ( 98, "   plist.append gives " + str(plist) )
    elif isinstance(obj,bpy.types.PropertyGroup):
        # print ( "Found a property group: " + str(objpath) )
        if 'expression' in obj.keys() and 'param_data' in obj.keys():
            # This is also what we're looking for (should be a PanelParameter), so add it to the list
            plist.append ( obj )
            if depth_in_get_num_param_list < depth_to_print:
                print ( "   ---------------- Parameter --------------------> " + str(objpath) )
            #threshold_print ( 98, "   plist.append gives " + str(plist) )
        elif 'contains_cellblender_parameters' in dir(obj):  # For some reason, obj.keys() didn't find this in mcell!?!
            # print ( "   " + str(objpath) + " contains cellblender parameters" )
            # This is some other property group with parameters, so walk through all of its properties using keys
            # for objkey in obj.keys():
            if depth_in_get_num_param_list < depth_to_print:
                print ( "   ---------------- Contains Parameters ----------> " + str(objpath) )
            for objkey in obj.bl_rna.properties.keys():    # This is somewhat ugly, but works best!!
                try:
                    pstr = objpath+"."+str(objkey)
                    plist = get_numeric_parameter_list(pstr, plist, debug)
                except:
                    # This can happen with properties in the .blend file that are no longer in the code or have been renamed!!!
                    print ( "Exception inside get_numeric_parameter()" )
                    # threshold_print ( 0, "  ===> Exception in get_numeric_parameter_list:" + str ( sys.exc_info() ) )
                    #threshold_print ( 0, "    ===> Exception type = " + sys.exc_type )
                    #threshold_print ( 0, "    ===> Exception value = " + sys.exc_value )
                    #threshold_print ( 0, "    ===> Exception traceback = " + sys.exc_traceback )
                    #threshold_print ( 0, "    ===> Exception in recursive call to get_numeric_parameter_list ( " + pstr + " )" )
                    # threshold_print ( 0, "    ===> Exception in get_numeric_parameter_list isinstance branch with " + objpath + "." + str(objkey) )
                    pass

    elif type(obj).__name__ == 'bpy_prop_collection_idprop':
        # This is a collection, so step through its elements as if it's an array using keys
        for objkey in obj.keys():
            try:
                plist = get_numeric_parameter_list(objpath+"[\""+str(objkey)+"\"]", plist, debug)
            except:
                # threshold_print ( 0, " ===> Exception in get_numeric_parameter_list idprop branch with " + objpath + "['" + str(objkey) + "']" )
                pass
    else:
        # This could be anything else ... like <'int'> or <'str'>
        pass

    #if threshold_print_enabled ( 90 ):
    #    print ( "  Parameters found so far by get_numeric_parameter_list(" + str(objpath) + "):" )
    #    for p in plist:
    #        print ( "    " + p.get_formatted_string() )      

    # print ( "Bottom of get_numeric_parameter_list" )

    depth_in_get_num_param_list += -1
    if depth_in_get_num_param_list < depth_to_print:
        # print ( "Return from call to get_numeric_parameter_list with " + str(objpath) )
        pass
    return plist



def print_numeric_parameter_list ( thresh, prefix="", param_list=None, fast=False ):
    """ Obtains a list of all numeric panel parameters and prints them to the console """
    plist = param_list
    if plist == None:
        plist = get_numeric_parameter_list ( None, [] )

    #threshold_print ( thresh, prefix + "There are " + str(len(plist)) + " panel parameters defined ..." )

    if fast:
        # Because converting the object to a string takes so long, process the list one at a time so it doesn't appear to freeze
        for i in range(len(plist)):
            plist_name = str(plist[i])  # For some reason, this doesn't give the full path name (like bpy.data.scenes['Scene'].mcell.molecules.molecule_list[0].diffusion_constant)
            #threshold_print ( thresh, prefix + "  " +  plist_name.strip() + " = " + str(plist[i].get_expression()) + " = " + str(plist[i].get_ID_expression()) + " = " + str(plist[i].get_value()) )
    else:
        # Remove the leading and trailing brackets and split by commas
        plist_names = str(plist)[1:-1].split(",")
        # Print each parameter
        for i in range(len(plist)):
            #threshold_print ( thresh, prefix + "  " +  plist_names[i].strip() + " = " + str(plist[i].get_expression()) + " = " + str(plist[i].get_ID_expression()) + " = " + str(plist[i].get_value()) )
            pass



### Some generic example classes ... WARNING: The examples in this section contain ideas that have not been fully tested

class PARAM_debug_class(PanelParameter):
    """ Example of subclassing PanelParameter and overloading its methods """
    param_data = PointerProperty(type=PanelParameterData)
    def update( self ):
        #threshold_print ( 20, "   User's update called with " + " self.expression = " + str(self.expression) + ", self.param_data.value = " + str(self.param_data.value) )
        #threshold_print ( 20, "     dir(self) = " + str(dir(self)) )
        #threshold_print ( 20, "     Starting python interactive console ... control-D to continue running..." )
        # This drops into a python interpreter on the console ( don't start Blender with an & !! )
        __import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})
        pass


class ExampleOverloadedPanelParameter(PanelParameter):
    """ Example of subclassing PanelParameter and overloading its methods """
    param_data = PointerProperty(type=PanelParameterData)
    def get_text(self):
        return (  str(self.expression) + "=" + str(self.param_data.value) )
    def update( self ):
        parent = get_parent ( self )
        #threshold_print ( 50, "Parent = " + str(parent) )

class Iterations_class(PanelParameter):
    """ Example class for handling the iterations panel parameter """
    param_data = PointerProperty(type=PanelParameterData)
    def get_text(self):
        return ( "n=" + str(self.param_data.value) )
    def update( self ):
        parent = get_parent ( self )


