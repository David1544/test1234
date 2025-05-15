import bpy
import os
import math
import mathutils
import bmesh
import re
import time
import traceback
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper

from . import FmdlFile
from . import IO
from . import PesSkeletonData
from . import MaterialPresets
from . import FmdlMeshSplitting
from . import FmdlAntiBlur
from . import FMDL_Util_TrackChanges

# Define skeletonTypes as a list of tuples with string keys
skeletonTypes = [
    ('0', 'None', ''),
    ('1', 'Body', ''),
    ('2', 'Face', ''),
    ('3', 'Left Hand', ''),
    ('4', 'Right Hand', '')
]

# Define defaultSkeletonType as a string
defaultSkeletonType = '1'

def FMDL_Scene_Skeleton_update_type(self, context):
    if hasattr(context.scene, "fmdl_skeleton_type"):
        skeletonType = int(context.scene.fmdl_skeleton_type)
        if skeletonType == PesSkeletonData.SKELETON_TYPE_NONE:
            context.scene.fmdl_skeleton_source = 'NONE'
        else:
            context.scene.fmdl_skeleton_source = 'REFERENCE'

class FMDL_Scene_Import_Panel(bpy.types.Panel):
    bl_idname = "FMDL_PT_Scene_Import_Panel"
    bl_label = "Import Fmdl"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FMDL"

    def draw(self, context):
        layout = self.layout
        layout.operator("fmdl.import_fmdl", text = "Import Fmdl")
        layout.prop(context.scene, "fmdl_import_all_bounding_boxes")

class FMDL_Scene_Import_Operator(bpy.types.Operator, ImportHelper):
    bl_idname = "fmdl.import_fmdl"
    bl_label = "Import Fmdl"
    bl_description = "Import a Fox Model file (.fmdl)"
    bl_options = {'PRESET'}

    filename_ext = ".fmdl"
    filter_glob: StringProperty(default="*.fmdl", options={'HIDDEN'})

    def execute(self, context):
        filename = self.filepath

        try:
            fmdlFile = FmdlFile.FmdlFile()
            fmdlFile.readFile(filename)
            importSettings = IO.ImportSettings()
            importSettings.enableImportAllBoundingBoxes = context.scene.fmdl_import_all_bounding_boxes
            IO.importFmdl(context, fmdlFile, filename, importSettings)
        except Exception as error:
            self.report({'ERROR'}, "Error importing Fmdl: " + str(error))
            print("Error importing Fmdl: " + str(error))
            return {'CANCELLED'}

        self.report({'INFO'}, "Fmdl imported successfully.")
        return {'FINISHED'}

class FMDL_Scene_Export_Panel(bpy.types.Panel):
    bl_idname = "FMDL_PT_Scene_Export_Panel"
    bl_label = "Export Fmdl"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FMDL"

    def draw(self, context):
        layout = self.layout
        layout.operator("fmdl.export_fmdl", text = "Export Fmdl")
        layout.operator_menu_enum("fmdl.export_fmdl_selection", "selection_type", text = "Export Selection")
        layout.prop(context.scene, "fmdl_export_selected_only")
        layout.prop(context.scene, "fmdl_export_optimize_materials")
        layout.prop(context.scene, "fmdl_export_apply_modifiers")
        layout.prop(context.scene, "fmdl_export_mesh_splitting")
        layout.prop(context.scene, "fmdl_export_mesh_splitting_auto_seams")
        layout.prop(context.scene, "fmdl_export_mesh_splitting_use_materials")
        layout.prop(context.scene, "fmdl_export_mesh_splitting_merge_uvs")
        layout.prop(context.scene, "fmdl_export_mesh_splitting_merge_vertices")
        layout.prop(context.scene, "fmdl_export_mesh_splitting_merge_threshold")
        layout.prop(context.scene, "fmdl_export_antiblur")
        layout.prop(context.scene, "fmdl_export_antiblur_threshold")
        layout.prop(context.scene, "fmdl_export_antiblur_angle_threshold")
        layout.prop(context.scene, "fmdl_export_antiblur_edges_only")
        layout.prop(context.scene, "fmdl_export_sort_materials")
        layout.prop(context.scene, "fmdl_export_hidden_meshes")
        layout.prop(context.scene, "fmdl_export_copy_textures")
        layout.prop(context.scene, "fmdl_export_all_bones")
        layout.prop(context.scene, "fmdl_export_all_vertices")
        layout.prop(context.scene, "fmdl_export_bounding_boxes")

class FMDL_Scene_Export_Operator(bpy.types.Operator, ExportHelper):
    bl_idname = "fmdl.export_fmdl"
    bl_label = "Export Fmdl"
    bl_description = "Export a Fox Model file (.fmdl)"
    bl_options = {'PRESET'}

    filename_ext = ".fmdl"
    filter_glob: StringProperty(default="*.fmdl", options={'HIDDEN'})

    def execute(self, context):
        filename = self.filepath

        try:
            exportSettings = IO.ExportSettings()
            # Set extension-related settings
            exportSettings.enableExtensions = True
            exportSettings.enableMeshSplitting = context.scene.fmdl_export_mesh_splitting
            exportSettings.enableAntiblur = context.scene.fmdl_export_antiblur
            
            # Create a dictionary for other settings that aren't part of ExportSettings class
            otherSettings = {}
            otherSettings["selected_only"] = context.scene.fmdl_export_selected_only
            otherSettings["optimize_materials"] = context.scene.fmdl_export_optimize_materials
            otherSettings["apply_modifiers"] = context.scene.fmdl_export_apply_modifiers
            otherSettings["mesh_splitting_auto_seams"] = context.scene.fmdl_export_mesh_splitting_auto_seams
            otherSettings["mesh_splitting_use_materials"] = context.scene.fmdl_export_mesh_splitting_use_materials
            otherSettings["mesh_splitting_merge_uvs"] = context.scene.fmdl_export_mesh_splitting_merge_uvs
            otherSettings["mesh_splitting_merge_vertices"] = context.scene.fmdl_export_mesh_splitting_merge_vertices
            otherSettings["mesh_splitting_merge_threshold"] = context.scene.fmdl_export_mesh_splitting_merge_threshold
            otherSettings["antiblur_threshold"] = context.scene.fmdl_export_antiblur_threshold
            otherSettings["antiblur_angle_threshold"] = context.scene.fmdl_export_antiblur_angle_threshold
            otherSettings["antiblur_edges_only"] = context.scene.fmdl_export_antiblur_edges_only
            otherSettings["sort_materials"] = context.scene.fmdl_export_sort_materials
            otherSettings["hidden_meshes"] = context.scene.fmdl_export_hidden_meshes
            otherSettings["copy_textures"] = context.scene.fmdl_export_copy_textures
            otherSettings["all_bones"] = context.scene.fmdl_export_all_bones
            otherSettings["all_vertices"] = context.scene.fmdl_export_all_vertices
            otherSettings["bounding_boxes"] = context.scene.fmdl_export_bounding_boxes
            otherSettings["selection_type"] = 'ALL'
            otherSettings["selection_object"] = None
            otherSettings["selection_slot"] = None
            IO.exportFmdl(context, filename, exportSettings, otherSettings)
        except Exception as error:
            self.report({'ERROR'}, "Error exporting Fmdl: " + str(error))
            print("Error exporting Fmdl: " + str(error))
            traceback.print_exc()
            return {'CANCELLED'}

        self.report({'INFO'}, "Fmdl exported successfully.")
        return {'FINISHED'}

class FMDL_Scene_Export_Object_Menu(bpy.types.Operator):
    bl_idname = "fmdl.export_fmdl_selection"
    bl_label = "Export Selection"
    bl_description = "Export a selection to a Fox Model file (.fmdl)"
    bl_options = {'PRESET'}

    selection_type: EnumProperty(
        name = "Selection Type",
        items = [
            ('ACTIVE_OBJECT', "Active Object", "Export the active object"),
            ('ACTIVE_MATERIAL', "Active Material", "Export all objects with the active material"),
            ('MATERIAL_SLOT', "Material Slot", "Export all objects with the active material slot"),
        ],
        default = 'ACTIVE_OBJECT'
    )

    def execute(self, context):
        bpy.ops.fmdl.export_fmdl_selection_dialog('INVOKE_DEFAULT', selection_type = self.selection_type)
        return {'FINISHED'}

class FMDL_Scene_Export_Selection_Dialog(bpy.types.Operator, ExportHelper):
    bl_idname = "fmdl.export_fmdl_selection_dialog"
    bl_label = "Export Selection"
    bl_description = "Export a selection to a Fox Model file (.fmdl)"
    bl_options = {'PRESET'}

    filename_ext = ".fmdl"
    filter_glob: StringProperty(default="*.fmdl", options={'HIDDEN'})

    selection_type: StringProperty(default = 'ACTIVE_OBJECT')

    def execute(self, context):
        filename = self.filepath

        try:
            exportSettings = IO.ExportSettings()
            # Set extension-related settings
            exportSettings.enableExtensions = True
            exportSettings.enableMeshSplitting = context.scene.fmdl_export_mesh_splitting
            exportSettings.enableAntiblur = context.scene.fmdl_export_antiblur
            
            # Create a dictionary for other settings
            otherSettings = {}
            otherSettings["selected_only"] = context.scene.fmdl_export_selected_only
            otherSettings["optimize_materials"] = context.scene.fmdl_export_optimize_materials
            otherSettings["apply_modifiers"] = context.scene.fmdl_export_apply_modifiers
            otherSettings["mesh_splitting_auto_seams"] = context.scene.fmdl_export_mesh_splitting_auto_seams
            otherSettings["mesh_splitting_use_materials"] = context.scene.fmdl_export_mesh_splitting_use_materials
            otherSettings["mesh_splitting_merge_uvs"] = context.scene.fmdl_export_mesh_splitting_merge_uvs
            otherSettings["mesh_splitting_merge_vertices"] = context.scene.fmdl_export_mesh_splitting_merge_vertices
            otherSettings["mesh_splitting_merge_threshold"] = context.scene.fmdl_export_mesh_splitting_merge_threshold
            otherSettings["antiblur_threshold"] = context.scene.fmdl_export_antiblur_threshold
            otherSettings["antiblur_angle_threshold"] = context.scene.fmdl_export_antiblur_angle_threshold
            otherSettings["antiblur_edges_only"] = context.scene.fmdl_export_antiblur_edges_only
            otherSettings["sort_materials"] = context.scene.fmdl_export_sort_materials
            otherSettings["hidden_meshes"] = context.scene.fmdl_export_hidden_meshes
            otherSettings["copy_textures"] = context.scene.fmdl_export_copy_textures
            otherSettings["all_bones"] = context.scene.fmdl_export_all_bones
            otherSettings["all_vertices"] = context.scene.fmdl_export_all_vertices
            otherSettings["bounding_boxes"] = context.scene.fmdl_export_bounding_boxes
            otherSettings["selection_type"] = self.selection_type
            otherSettings["selection_object"] = context.active_object
            otherSettings["selection_slot"] = context.active_object.active_material_index if context.active_object else 0
            IO.exportFmdl(context, filename, exportSettings, otherSettings)
        except Exception as error:
            self.report({'ERROR'}, "Error exporting Fmdl: " + str(error))
            print("Error exporting Fmdl: " + str(error))
            traceback.print_exc()
            return {'CANCELLED'}

        self.report({'INFO'}, "Fmdl exported successfully.")
        return {'FINISHED'}

class FMDL_Scene_Skeleton_Panel(bpy.types.Panel):
    bl_idname = "FMDL_PT_Scene_Skeleton_Panel"
    bl_label = "Skeleton"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FMDL"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "fmdl_skeleton_type")
        layout.prop(context.scene, "fmdl_skeleton_source")
        if context.scene.fmdl_skeleton_source == 'REFERENCE':
            layout.prop_search(context.scene, "fmdl_skeleton_reference", context.scene, "objects")
        elif context.scene.fmdl_skeleton_source == 'FILE':
            layout.prop(context.scene, "fmdl_skeleton_file")
            layout.operator("fmdl.load_skeleton", text = "Load Skeleton")

class FMDL_Scene_Skeleton_Load_Operator(bpy.types.Operator, ImportHelper):
    bl_idname = "fmdl.load_skeleton"
    bl_label = "Load Skeleton"
    bl_description = "Load a skeleton from a Fox Model file (.fmdl)"
    bl_options = {'PRESET'}

    filename_ext = ".fmdl"
    filter_glob: StringProperty(default="*.fmdl", options={'HIDDEN'})

    def execute(self, context):
        filename = self.filepath
        context.scene.fmdl_skeleton_file = filename

        try:
            fmdlFile = FmdlFile.FmdlFile()
            fmdlFile.readFile(filename)
            IO.importSkeleton(context, fmdlFile)
        except Exception as error:
            self.report({'ERROR'}, "Error loading skeleton: " + str(error))
            print("Error loading skeleton: " + str(error))
            return {'CANCELLED'}

        self.report({'INFO'}, "Skeleton loaded successfully.")
        return {'FINISHED'}

class FMDL_Object_File_Panel(bpy.types.Panel):
    bl_idname = "FMDL_PT_Object_File_Panel"
    bl_label = "Fmdl File"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        layout = self.layout
        layout.prop(context.active_object, "fmdl_file_path")
        layout.prop(context.active_object, "fmdl_file_version")
        layout.prop(context.active_object, "fmdl_file_section_count")

class FMDL_Object_Skeleton_Panel(bpy.types.Panel):
    bl_idname = "FMDL_PT_Object_Skeleton_Panel"
    bl_label = "Fmdl Skeleton"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        layout.prop(context.active_object, "fmdl_skeleton_replace")
        if context.active_object.fmdl_skeleton_replace:
            layout.prop(context.active_object, "fmdl_skeleton_replace_with")

class FMDL_Material_Parameter_List(bpy.types.UIList):
    bl_idname = "FMDL_UL_Material_Parameter_List"
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text = "", emboss = False)
        layout.prop(item, "parameters", text = "")

class FMDL_Material_Panel(bpy.types.Panel):
    bl_idname = "FMDL_PT_Material_Panel"
    bl_label = "Fmdl Material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.active_material is not None

    def draw(self, context):
        layout = self.layout
        material = context.active_object.active_material
        layout.prop(material, "fmdl_material_shader")
        layout.prop(material, "fmdl_material_technique")
        layout.template_list("FMDL_UL_Material_Parameter_List", "", material, "fmdl_material_parameters", material, "fmdl_material_parameters_active")
        layout.operator("fmdl.material_preset", text = "Apply Preset")

class FMDL_Material_Preset_Operator(bpy.types.Operator):
    bl_idname = "fmdl.material_preset"
    bl_label = "Apply Material Preset"
    bl_description = "Apply a material preset"
    bl_options = {'PRESET'}

    preset: EnumProperty(
        name = "Preset",
        items = MaterialPresets.getPresetItems,
        default = 0
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "preset")

    def execute(self, context):
        material = context.active_object.active_material
        MaterialPresets.applyPreset(material, self.preset)
        return {'FINISHED'}

def register():
    # Register properties
    if not hasattr(bpy.types.Scene, "fmdl_import_all_bounding_boxes"):
        bpy.types.Scene.fmdl_import_all_bounding_boxes = bpy.props.BoolProperty(name = "Import all bounding boxes", default = False)
    
    # Register skeleton properties with hasattr check for Blender 4.4
    if not hasattr(bpy.types.Scene, "fmdl_skeleton_type"):
        bpy.types.Scene.fmdl_skeleton_type = bpy.props.EnumProperty(name = "Skeleton type",
            items = skeletonTypes,
            default = "1",  # Force string value
            update = FMDL_Scene_Skeleton_update_type,
            options = {'SKIP_SAVE'}
        )
    if not hasattr(bpy.types.Object, "fmdl_skeleton_replace"):
        bpy.types.Object.fmdl_skeleton_replace = bpy.props.BoolProperty(name = "Replace skeleton", default = False)
    if not hasattr(bpy.types.Object, "fmdl_skeleton_replace_with"):
        bpy.types.Object.fmdl_skeleton_replace_with = bpy.props.StringProperty(name = "Replace with", default = "")
    if not hasattr(bpy.types.Scene, "fmdl_skeleton_source"):
        bpy.types.Scene.fmdl_skeleton_source = bpy.props.EnumProperty(name = "Skeleton source",
            items = [
                ('NONE', "None", ""),
                ('REFERENCE', "Reference", ""),
                ('FILE', "File", ""),
            ],
            default = 'NONE',
            options = {'SKIP_SAVE'}
        )
    if not hasattr(bpy.types.Scene, "fmdl_skeleton_reference"):
        bpy.types.Scene.fmdl_skeleton_reference = bpy.props.StringProperty(name = "Reference", default = "")
    if not hasattr(bpy.types.Scene, "fmdl_skeleton_file"):
        bpy.types.Scene.fmdl_skeleton_file = bpy.props.StringProperty(name = "File", default = "")
    
    # Register export properties
    if not hasattr(bpy.types.Scene, "fmdl_export_selected_only"):
        bpy.types.Scene.fmdl_export_selected_only = bpy.props.BoolProperty(name = "Selected only", default = False)
    if not hasattr(bpy.types.Scene, "fmdl_export_optimize_materials"):
        bpy.types.Scene.fmdl_export_optimize_materials = bpy.props.BoolProperty(name = "Optimize materials", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_apply_modifiers"):
        bpy.types.Scene.fmdl_export_apply_modifiers = bpy.props.BoolProperty(name = "Apply modifiers", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_mesh_splitting"):
        bpy.types.Scene.fmdl_export_mesh_splitting = bpy.props.BoolProperty(name = "Mesh splitting", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_mesh_splitting_auto_seams"):
        bpy.types.Scene.fmdl_export_mesh_splitting_auto_seams = bpy.props.BoolProperty(name = "Auto seams", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_mesh_splitting_use_materials"):
        bpy.types.Scene.fmdl_export_mesh_splitting_use_materials = bpy.props.BoolProperty(name = "Use materials", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_mesh_splitting_merge_uvs"):
        bpy.types.Scene.fmdl_export_mesh_splitting_merge_uvs = bpy.props.BoolProperty(name = "Merge UVs", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_mesh_splitting_merge_vertices"):
        bpy.types.Scene.fmdl_export_mesh_splitting_merge_vertices = bpy.props.BoolProperty(name = "Merge vertices", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_mesh_splitting_merge_threshold"):
        bpy.types.Scene.fmdl_export_mesh_splitting_merge_threshold = bpy.props.FloatProperty(name = "Merge threshold", default = 0.0001, min = 0.0, max = 1.0)
    if not hasattr(bpy.types.Scene, "fmdl_export_antiblur"):
        bpy.types.Scene.fmdl_export_antiblur = bpy.props.BoolProperty(name = "Anti-blur", default = False)
    if not hasattr(bpy.types.Scene, "fmdl_export_antiblur_threshold"):
        bpy.types.Scene.fmdl_export_antiblur_threshold = bpy.props.FloatProperty(name = "Anti-blur threshold", default = 0.1, min = 0.0, max = 1.0)
    if not hasattr(bpy.types.Scene, "fmdl_export_antiblur_angle_threshold"):
        bpy.types.Scene.fmdl_export_antiblur_angle_threshold = bpy.props.FloatProperty(name = "Anti-blur angle threshold", default = 0.5, min = 0.0, max = 1.0)
    if not hasattr(bpy.types.Scene, "fmdl_export_antiblur_edges_only"):
        bpy.types.Scene.fmdl_export_antiblur_edges_only = bpy.props.BoolProperty(name = "Anti-blur edges only", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_sort_materials"):
        bpy.types.Scene.fmdl_export_sort_materials = bpy.props.BoolProperty(name = "Sort materials", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_hidden_meshes"):
        bpy.types.Scene.fmdl_export_hidden_meshes = bpy.props.BoolProperty(name = "Export hidden meshes", default = False)
    if not hasattr(bpy.types.Scene, "fmdl_export_copy_textures"):
        bpy.types.Scene.fmdl_export_copy_textures = bpy.props.BoolProperty(name = "Copy textures", default = True)
    if not hasattr(bpy.types.Scene, "fmdl_export_all_bones"):
        bpy.types.Scene.fmdl_export_all_bones = bpy.props.BoolProperty(name = "Export all bones", default = False)
    if not hasattr(bpy.types.Scene, "fmdl_export_all_vertices"):
        bpy.types.Scene.fmdl_export_all_vertices = bpy.props.BoolProperty(name = "Export all vertices", default = False)
    if not hasattr(bpy.types.Scene, "fmdl_export_bounding_boxes"):
        bpy.types.Scene.fmdl_export_bounding_boxes = bpy.props.BoolProperty(name = "Export bounding boxes", default = True)
    
    # Register file properties
    if not hasattr(bpy.types.Object, "fmdl_file_path"):
        bpy.types.Object.fmdl_file_path = bpy.props.StringProperty(name = "File path", default = "")
    if not hasattr(bpy.types.Object, "fmdl_file_version"):
        bpy.types.Object.fmdl_file_version = bpy.props.IntProperty(name = "File version", default = 0)
    if not hasattr(bpy.types.Object, "fmdl_file_section_count"):
        bpy.types.Object.fmdl_file_section_count = bpy.props.IntProperty(name = "Section count", default = 0)
    
    # Register material properties
    if not hasattr(bpy.types.Material, "fmdl_material_shader"):
        bpy.types.Material.fmdl_material_shader = bpy.props.StringProperty(name = "Shader", default = "")
    if not hasattr(bpy.types.Material, "fmdl_material_technique"):
        bpy.types.Material.fmdl_material_technique = bpy.props.StringProperty(name = "Technique", default = "")
    if not hasattr(bpy.types.Material, "fmdl_material_parameters"):
        bpy.types.Material.fmdl_material_parameters = bpy.props.CollectionProperty(type = FMDL_Util_TrackChanges.FMDL_MaterialParameter)
    if not hasattr(bpy.types.Material, "fmdl_material_parameters_active"):
        bpy.types.Material.fmdl_material_parameters_active = bpy.props.IntProperty(name = "Active parameter", default = 0)
    
    # Register classes
    bpy.utils.register_class(FMDL_Material_Parameter_List)
    bpy.utils.register_class(FMDL_Material_Panel)
    bpy.utils.register_class(FMDL_Material_Preset_Operator)
    bpy.utils.register_class(FMDL_Object_File_Panel)
    bpy.utils.register_class(FMDL_Object_Skeleton_Panel)
    bpy.utils.register_class(FMDL_Scene_Export_Object_Menu)
    bpy.utils.register_class(FMDL_Scene_Export_Operator)
    bpy.utils.register_class(FMDL_Scene_Export_Panel)
    bpy.utils.register_class(FMDL_Scene_Export_Selection_Dialog)
    bpy.utils.register_class(FMDL_Scene_Import_Operator)
    bpy.utils.register_class(FMDL_Scene_Import_Panel)
    bpy.utils.register_class(FMDL_Scene_Skeleton_Load_Operator)
    bpy.utils.register_class(FMDL_Scene_Skeleton_Panel)

def unregister():
    # Unregister classes
    bpy.utils.unregister_class(FMDL_Scene_Skeleton_Panel)
    bpy.utils.unregister_class(FMDL_Scene_Skeleton_Load_Operator)
    bpy.utils.unregister_class(FMDL_Scene_Import_Panel)
    bpy.utils.unregister_class(FMDL_Scene_Import_Operator)
    bpy.utils.unregister_class(FMDL_Scene_Export_Selection_Dialog)
    bpy.utils.unregister_class(FMDL_Scene_Export_Panel)
    bpy.utils.unregister_class(FMDL_Scene_Export_Operator)
    bpy.utils.unregister_class(FMDL_Scene_Export_Object_Menu)
    bpy.utils.unregister_class(FMDL_Object_Skeleton_Panel)
    bpy.utils.unregister_class(FMDL_Object_File_Panel)
    bpy.utils.unregister_class(FMDL_Material_Preset_Operator)
    bpy.utils.unregister_class(FMDL_Material_Panel)
    bpy.utils.unregister_class(FMDL_Material_Parameter_List)
    
    # Unregister properties
    del bpy.types.Material.fmdl_material_parameters_active
    del bpy.types.Material.fmdl_material_parameters
    del bpy.types.Material.fmdl_material_technique
    del bpy.types.Material.fmdl_material_shader
    del bpy.types.Object.fmdl_file_section_count
    del bpy.types.Object.fmdl_file_version
    del bpy.types.Object.fmdl_file_path
    del bpy.types.Scene.fmdl_export_bounding_boxes
    del bpy.types.Scene.fmdl_export_all_vertices
    del bpy.types.Scene.fmdl_export_all_bones
    del bpy.types.Scene.fmdl_export_copy_textures
    del bpy.types.Scene.fmdl_export_hidden_meshes
    del bpy.types.Scene.fmdl_export_sort_materials
    del bpy.types.Scene.fmdl_export_antiblur_edges_only
    del bpy.types.Scene.fmdl_export_antiblur_angle_threshold
    del bpy.types.Scene.fmdl_export_antiblur_threshold
    del bpy.types.Scene.fmdl_export_antiblur
    del bpy.types.Scene.fmdl_export_mesh_splitting_merge_threshold
    del bpy.types.Scene.fmdl_export_mesh_splitting_merge_vertices
    del bpy.types.Scene.fmdl_export_mesh_splitting_merge_uvs
    del bpy.types.Scene.fmdl_export_mesh_splitting_use_materials
    del bpy.types.Scene.fmdl_export_mesh_splitting_auto_seams
    del bpy.types.Scene.fmdl_export_mesh_splitting
    del bpy.types.Scene.fmdl_export_apply_modifiers
    del bpy.types.Scene.fmdl_export_optimize_materials
    del bpy.types.Scene.fmdl_export_selected_only
    del bpy.types.Scene.fmdl_skeleton_file
    del bpy.types.Scene.fmdl_skeleton_reference
    del bpy.types.Scene.fmdl_skeleton_source
    del bpy.types.Object.fmdl_skeleton_replace_with
    del bpy.types.Object.fmdl_skeleton_replace
    del bpy.types.Scene.fmdl_skeleton_type
    del bpy.types.Scene.fmdl_import_all_bounding_boxes