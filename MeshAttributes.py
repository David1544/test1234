import bpy
from . import BlenderCompatibility

def set_auto_smooth(mesh, value=True, angle=None):
    """Set auto smooth on a mesh in a way that's compatible with any Blender version
    
    Args:
        mesh: The blender mesh object to modify
        value: Boolean indicating whether to enable auto smooth
        angle: Optional angle threshold in radians (if not specified, uses mesh's existing value)
    """
    # First try direct attribute access (older Blender versions)
    if hasattr(mesh, "use_auto_smooth"):
        mesh.use_auto_smooth = value
        if angle is not None:
            mesh.auto_smooth_angle = angle
    else:
        # For Blender 4.2+, auto smooth is a property of polygons
        # Method 1: Try using the API (if available)
        if hasattr(mesh, "polygons") and hasattr(mesh.polygons, "use_smooth"):
            for poly in mesh.polygons:
                poly.use_smooth = value
        
        # Store setting in mesh custom properties for reference/export
        mesh["use_auto_smooth"] = value
        if angle is not None:
            mesh["auto_smooth_angle"] = angle

def get_auto_smooth(mesh):
    """Get auto smooth status in a way that's compatible with any Blender version
    
    Args:
        mesh: The blender mesh object to check
    
    Returns:
        Boolean indicating whether auto smooth is enabled
    """
    # First try direct attribute access (older Blender versions)
    if hasattr(mesh, "use_auto_smooth"):
        return mesh.use_auto_smooth
    
    # For Blender 4.2+, check custom properties
    if "use_auto_smooth" in mesh:
        return mesh["use_auto_smooth"]
    
    # As a fallback, check if any polygons are smooth
    if hasattr(mesh, "polygons") and len(mesh.polygons) > 0:
        # If any polygon has smooth enabled, consider auto smooth to be enabled
        return any(poly.use_smooth for poly in mesh.polygons)
    
    # Default to False if we can't determine
    return False

def create_uv_layer(mesh, name):
    """Create a UV layer in a way that's compatible with any Blender version
    
    Args:
        mesh: The blender mesh object to modify
        name: Name for the new UV layer
    
    Returns:
        A tuple containing (uv_layer, uv_texture_compat) where uv_texture_compat is an object
        that mimics the old uv_texture behavior for backward compatibility
    """
    # Create the UV layer - this works in all Blender versions
    uv_layer = mesh.uv_layers.new(name=name)
    
    # Create a compatibility wrapper that mimics the old uv_texture behavior
    class UVTextureCompat:
        def __init__(self, mesh, uv_layer_name):
            self.mesh = mesh
            self.name = uv_layer_name
            self.active = False
            self.active_clone = False
            self.active_render = False
            self._data = []
            
            # Initialize data objects to mimic the old behavior
            for _ in range(len(mesh.loops)):
                self._data.append(type('UVTextureData', (), {'image': None}))
        
        @property
        def data(self):
            """Return a list of objects with an 'image' attribute that can be set"""
            return self._data
        
        def make_active(self):
            """Make this the active UV layer"""
            # Find the index of our layer
            for i, uv in enumerate(self.mesh.uv_layers):
                if uv.name == self.name:
                    self.mesh.uv_layers.active_index = i
                    break
    
    # Create our compatibility object
    uv_texture_compat = UVTextureCompat(mesh, name)
    
    return uv_layer, uv_texture_compat

def calculate_tangents(mesh, uv_map):
    """Calculate tangents on a mesh in a way that's compatible with any Blender version
    
    Args:
        mesh: The blender mesh to calculate tangents on
        uv_map: The UV map to use for calculating tangents
        
    In Blender 2.7x-2.9x: mesh.calc_tangents(uv_map)
    In Blender 4.x+: mesh.calc_tangents(uvmap=uv_map)
    """
    try:
        # Try older style (positional argument)
        mesh.calc_tangents(uv_map)
    except TypeError:
        try:
            # Try newer style (keyword argument)
            mesh.calc_tangents(uvmap=uv_map)
        except Exception as e:
            # If both methods fail, print the error and fallback to not calculating tangents
            print(f"Error calculating tangents: {str(e)}")
            print("Tangents may not be correctly calculated. This could affect normal mapping.")
            return False
    
    return True
