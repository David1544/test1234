bl_info = {
	"name": "PES FMDL format",
	"author": "foreground, updated for Blender 4.2",
	"blender": (4, 2, 0),
	"category": "Import-Export",
	"version": (0, 8, 0),
	"location": "File > Import/Export",
	"description": "Import-Export PES FMDL models",
	"warning": "",
	"doc_url": "https://github.com/the4chancup/pes-fmdl-blender",
}

import bpy
import bpy.props

# Import compatibility helpers
from . import BlenderCompatibility
from . import MeshAttributes

# Import and expose PesSkeletonData variables
from . import PesSkeletonData
from .PesSkeletonData import skeletonTypeNames, getObjectSkeletonType
from .PesSkeletonData import SKELETON_TYPE_NONE, SKELETON_TYPE_BODY, SKELETON_TYPE_FACE
from .PesSkeletonData import SKELETON_TYPE_HAND_L, SKELETON_TYPE_HAND_R

from . import UI
# Ensure defaultSkeletonType is a string
UI.defaultSkeletonType = '1'

class FMDL_MaterialParameter(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name = "Parameter Name")
	parameters: bpy.props.FloatVectorProperty(name = "Parameter Values", size = 4, default = (0.0, 0.0, 0.0, 0.0))

def register():
	bpy.utils.register_class(FMDL_MaterialParameter)
	
	# Register properties for Mesh
	if not hasattr(bpy.types.Mesh, "fmdl_high_precision_uvs"):
		bpy.types.Mesh.fmdl_high_precision_uvs = bpy.props.BoolProperty(
			name = "FMDL High Precision UVs", 
			default = False, 
			description = "Allows for higher quality UV coordinates, at the cost of slightly higher file size"
		)
	
	# Register properties for Material
	if not hasattr(bpy.types.Material, "fmdl_material_shader"):
		bpy.types.Material.fmdl_material_shader = bpy.props.StringProperty(name = "Shader")
	if not hasattr(bpy.types.Material, "fmdl_material_technique"):
		bpy.types.Material.fmdl_material_technique = bpy.props.StringProperty(name = "Technique")
	if not hasattr(bpy.types.Material, "fmdl_material_parameters"):
		bpy.types.Material.fmdl_material_parameters = bpy.props.CollectionProperty(name = "Material Parameters", type = FMDL_MaterialParameter)
	if not hasattr(bpy.types.Material, "fmdl_alpha_flags"):
		bpy.types.Material.fmdl_alpha_flags = bpy.props.IntProperty(name = "Alpha Flags", default = 0, min = 0, max = 255)
	if not hasattr(bpy.types.Material, "fmdl_shadow_flags"):
		bpy.types.Material.fmdl_shadow_flags = bpy.props.IntProperty(name = "Shadow Flags", default = 0, min = 0, max = 255)
	if not hasattr(bpy.types.Material, "fmdl_material_antiblur"):
		bpy.types.Material.fmdl_material_antiblur = bpy.props.BoolProperty(
			name = "Automatic Constant-Shader Antiblur", 
			default = False, 
			description = "Apply automatic anti-blur measures for constant shaders"
		)
	
	# In Blender 4.2+, the Texture system has been replaced with Image nodes
	# We'll create custom properties for Image objects instead
	try:
		if not hasattr(bpy.types.Image, "fmdl_texture_filename"):
			bpy.types.Image.fmdl_texture_filename = bpy.props.StringProperty(name = "Texture Filename")
		if not hasattr(bpy.types.Image, "fmdl_texture_directory"):
			bpy.types.Image.fmdl_texture_directory = bpy.props.StringProperty(name = "Texture Directory")
		if not hasattr(bpy.types.Image, "fmdl_texture_role"):
			bpy.types.Image.fmdl_texture_role = bpy.props.StringProperty(name = "Texture Role")
	except Exception as e:
		print(f"Warning: Could not register Image properties: {str(e)}")
		print("Using custom properties as fallback for texture metadata")
	
	UI.register()

def unregister():
	UI.unregister()
	
	# Clean up custom properties
	try:
		del bpy.types.Mesh.fmdl_high_precision_uvs
		
		del bpy.types.Material.fmdl_material_shader
		del bpy.types.Material.fmdl_material_technique
		del bpy.types.Material.fmdl_material_parameters
		del bpy.types.Material.fmdl_alpha_flags
		del bpy.types.Material.fmdl_shadow_flags
		del bpy.types.Material.fmdl_material_antiblur
		
		del bpy.types.Image.fmdl_texture_filename
		del bpy.types.Image.fmdl_texture_directory
		del bpy.types.Image.fmdl_texture_role
	except:
		pass
	
	bpy.utils.unregister_class(FMDL_MaterialParameter)
