# Helper functions for version detection and compatibility

import bpy

def get_blender_version():
    """Return the Blender version as a tuple (major, minor, patch)"""
    major, minor, patch = bpy.app.version
    return (major, minor, patch)

def is_blender_4_plus():
    """Check if the Blender version is 4.0 or higher"""
    major, _, _ = get_blender_version()
    return major >= 4

def is_texture_nodes_supported():
    """Check if the current Blender version uses the new texture system"""
    # All Blender 4.x versions use the new texture nodes system
    return is_blender_4_plus()

def is_equal_or_higher_than(major, minor=0, patch=0):
    """Check if the current Blender version is equal or higher than the specified version"""
    current_major, current_minor, current_patch = get_blender_version()
    
    if current_major > major:
        return True
    if current_major < major:
        return False
    
    if current_minor > minor:
        return True
    if current_minor < minor:
        return False
    
    return current_patch >= patch

def run_ops_with_context(op_function, *args, **kwargs):
    """Run a Blender operator function with proper context handling for any Blender version
    
    Usage example:
        run_ops_with_context(bpy.ops.object.mode_set, mode='OBJECT')
    """
    try:
        # Try direct call (Blender 4.2+)
        return op_function(*args, **kwargs)
    except TypeError as e:
        if 'context' in str(e).lower():
            # For older Blender versions that need context
            ctx = bpy.context.copy()
            return op_function(ctx, *args, **kwargs)
        else:
            # Re-raise if it's a different TypeError
            raise

def create_vertex_group(mesh_object, name):
    """Create a vertex group with a name in a way that's compatible with any Blender version
    
    In Blender 2.7x-2.9x: vertex_groups.new(name)
    In Blender 4.x+: vertex_groups.new(name=name)
    
    Args:
        mesh_object: The mesh object to add the vertex group to
        name: Name for the new vertex group
    
    Returns:
        The newly created vertex group
    """
    try:
        # Try Blender 4.x style (keyword argument)
        return mesh_object.vertex_groups.new(name=name)
    except TypeError:
        # Fall back to older style (positional argument)
        return mesh_object.vertex_groups.new(name)
        
def set_object_property(obj, property_name, value):
    """Safely set a custom property on a Blender object
    
    This function handles property setting for both registered properties and custom properties
    in a way that works across different Blender versions.
    
    Args:
        obj: The Blender object to set the property on
        property_name: The name of the property to set
        value: The value to set the property to
    """
    # First, check if this is a registered property that exists directly on the object
    if hasattr(obj, property_name):
        # If it's a registered property, set it directly
        setattr(obj, property_name, value)
    else:
        # Otherwise, fall back to custom properties dictionary
        # This should work across all Blender versions
        obj[property_name] = value
        
def get_object_property(obj, property_name, default=None):
    """Safely get a custom property from a Blender object
    
    This function handles property retrieval for both registered properties and custom properties
    in a way that works across different Blender versions.
    
    Args:
        obj: The Blender object to get the property from
        property_name: The name of the property to get
        default: Default value to return if the property doesn't exist
        
    Returns:
        The property value or the provided default
    """
    # First, check if this is a registered property that exists directly on the object
    if hasattr(obj, property_name):
        # If it's a registered property, get it directly
        return getattr(obj, property_name)
    elif property_name in obj:
        # Otherwise, check in custom properties dictionary
        return obj[property_name]
    else:
        # Return default value if property doesn't exist
        return default

def write_fmdl_file(context, fmdl_file, filename):
    """Write an FMDL file to disk, handling any compatibility issues
    
    Args:
        context: The Blender context
        fmdl_file: The FMDL file object to write
        filename: The path to write the file to
    
    Returns:
        True if successful, False if an error occurred
    """
    try:
        # Make sure the directory exists
        import os
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Try to write the file
        fmdl_file.writeFile(filename)
        
        # Verify the file was written
        if not os.path.exists(filename):
            print(f"Error: File {filename} was not created")
            return False
            
        return True
    except Exception as e:
        print(f"Error writing FMDL file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
