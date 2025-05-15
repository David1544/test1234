# PES FMDL Plugin for Blender 4.2 and 4.4

This plugin allows you to import and export PES FMDL model files in Blender 4.2 and 4.4.

## Installation Instructions

1. Download this plugin as a ZIP file.
2. In Blender, go to Edit > Preferences > Add-ons.
3. Click "Install..." and select the ZIP file.
4. Enable the "Import-Export: PES FMDL format" add-on.

## How to Use

After installation, you'll find new options in both the File > Import and File > Export menus:
- File > Import > PES FMDL (.fmdl)
- File > Export > PES FMDL (.fmdl)

You'll also find a new panel in the 3D View sidebar (press 'N' to show it) under the "FMDL" tab with additional options.

## Features

- Import PES FMDL models with materials, textures, and skeletons
- Export models to FMDL format
- Support for normal maps
- Material customization
- Mesh splitting options
- Anti-blur features for certain shader types
- Custom bounding box support

## Compatibility Notes

### Texture Handling in Blender 4.2+

In Blender 4.2 and above, the texture system works differently than in earlier versions:

- Textures are managed through shader nodes instead of the legacy texture slots
- The plugin uses multiple fallback mechanisms to ensure texture properties are preserved:
  1. Standard properties on images and textures
  2. Custom properties stored on the objects
  3. Information stored in texture/image names (format: `[role] filename`)

If you're having issues with texture export, check that your image nodes have proper labels or that the image names follow the `[role] filename` format. Common texture roles include:
- `Base_Tex_SRGB` - Main diffuse texture in sRGB color space
- `Base_Tex_LIN` - Main diffuse texture in Linear color space
- `NormalMap_Tex_NRM` - Normal map texture

### Colorspace Handling

Blender 4.2+ uses different colorspace names compared to previous versions:

- The plugin automatically finds the best matching colorspace for each texture type
- For sRGB textures: Uses 'sRGB' or 'Filmic sRGB' 
- For linear textures: Uses 'Linear Rec.709' or any available Linear colorspace
- For normal maps: Uses 'Non-Color' or equivalent utility colorspace

If the original colorspace name isn't available in your Blender version, the plugin will:
1. Find the closest match based on name and intended use
2. Display a warning in the console with the substitution made
3. Default to a safe option if no appropriate match is found

### Operator Context Changes in Blender 4.2+

Blender 4.2+ introduced changes to how operator context is handled:

- Previous versions required passing a context parameter to operators (e.g., `bpy.ops.object.mode_set(context.copy(), mode='EDIT')`)
- Blender 4.2+ doesn't accept the context parameter in the same way, expecting operators to be called without it
- This plugin uses a compatibility layer to handle both formats automatically
- If you encounter "1-2 args execution context is supported" errors, this is related to these context changes
- The error should be fixed with our compatibility helper, but you may need to restart Blender after updating the plugin

### Materials in Blender 4.2+

Blender 4.2+ uses a node-based material system:

- The plugin automatically creates Principled BSDF shader nodes when importing materials
- Normal maps are properly set up with Normal Map nodes connected to the shader
- Material properties like emission and transparency are set on the shader inputs
- Material parameters are stored as custom properties and can be accessed through the FMDL panel

When creating materials for export:
1. Use the Principled BSDF shader as your main material node
2. Add Image Texture nodes for each texture
3. Label your texture nodes according to their role (Base_Tex_SRGB, NormalMap_Tex_NRM, etc.)
4. For normal maps, use a Normal Map node between the texture and shader

## Troubleshooting

### Import Issues

1. **Missing textures**: Textures might not be found if they're not in the expected locations. The plugin searches for textures in:
   - The same directory as the FMDL file
   - The parent directory
   - A "Common" subdirectory
   - A "Kit Textures" subdirectory
   - Place your texture files in one of these locations or manually assign them after import

2. **Colorspace errors**: If you see errors about colorspace names not found:
   - The plugin should automatically use compatible alternatives
   - Check the console for messages about colorspace substitutions
   - You can manually adjust image colorspaces after import if needed
   - Common substitutions: 'Linear Rec.709' instead of 'Linear', 'sRGB' instead of other color spaces

3. **Material errors**: If materials don't display correctly, check the material setup in the Shader Editor. You may need to:
   - Connect texture nodes properly
   - Adjust texture color spaces (sRGB for color textures, Non-Color for normal maps)
   - Set up proper normal map nodes

### Export Issues

1. **Attribute errors**: If you encounter errors about missing attributes:
   - Make sure your Blender version is 4.2 or higher
   - Try restarting Blender after installing the plugin
   - Check that you're using the correct version of the plugin for your Blender version

2. **Texture issues**: If textures don't export correctly:
   - Make sure texture nodes have proper labels that match FMDL roles
   - Check that images have proper names in the format `[role] filename`
   - Verify that textures are connected to the correct shader inputs

3. **Mesh splitting errors**: If you get errors about mesh limits:
   - Try enabling mesh splitting in the export options
   - Check the mesh statistics in the FMDL panel
   - Consider manually splitting very large meshes

- This version has been tested with Blender 4.2
- Material system is compatible with Blender's node-based materials
- Both the legacy texture system and modern node-based system are supported

## Troubleshooting

### Common Errors

1. **"1-2 args execution context is supported" error**:
   - This occurs due to changes in how Blender 4.2+ handles operator contexts
   - Solution: Use the latest version of this plugin which includes our context compatibility fixes
   - If the error persists, try restarting Blender after updating the plugin
   - If you're developing your own scripts using this plugin, use the `BlenderCompatibility.run_ops_with_context()` helper function for Blender operators

2. **"'Mesh' object has no attribute 'use_auto_smooth'" error**:
   - This occurs because Blender 4.2+ handles mesh auto smoothing differently
   - Solution: Use the latest version of this plugin which includes our mesh attribute compatibility fixes
   - The plugin now uses `MeshAttributes.set_auto_smooth()` and `MeshAttributes.get_auto_smooth()` helper functions

3. **"'Mesh' object has no attribute 'uv_textures'" error**:
   - This occurs because Blender 4.2+ removed the uv_textures attribute in favor of uv_layers
   - Solution: Use the latest version of this plugin which includes our UV handling compatibility
   - The plugin now uses `MeshAttributes.create_uv_layer()` which creates a compatibility wrapper

4. **"VertexGroups.new(): required parameter 'name' to be a keyword argument!" error**:
   - This occurs because Blender 4.2+ changed the vertex_groups.new() method to require a keyword argument
   - Solution: Use the latest version of this plugin which includes our vertex group compatibility
   - The plugin now uses `BlenderCompatibility.create_vertex_group()` which handles both formats

If you encounter other issues:

1. **Missing textures**: Make sure texture files are in the same folder as the .fmdl file or in a "Common" subfolder.

2. **Import errors**: Check the console output for detailed error messages.

3. **Material appearance issues**: The plugin creates Principled BSDF node setups, but you may need to adjust the material settings manually for the best visual result.

4. **"Entry point not found" error**: You might need to update your Blender installation.

## Known Limitations

- Some advanced FMDL material parameters may not be fully supported
- Complex animations or mesh transformations may require manual adjustments

## Credits

Originally created by foreground, updated for Blender 4.2 and 4.4.

## Compatibility Notes

### Blender 4.2 and 4.4 Compatibility Fixes

This version of the plugin includes several fixes for compatibility with Blender 4.2 and 4.4:

- Fixed version declaration in `__init__.py`
- Fixed `use_auto_smooth` attribute compatibility with a helper function
- Fixed UV texture handling with compatibility wrappers
- Fixed vertex group creation compatibility
- Fixed object property handling for FMDL file metadata
- Added compatibility helpers for setting/getting object properties safely

These changes ensure the plugin works correctly across different Blender versions, including the latest 4.x series. The compatibility layer handles differences between Blender versions transparently so that the plugin works the same way regardless of which Blender version you're using.
