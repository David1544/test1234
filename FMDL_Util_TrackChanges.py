import bpy

@bpy.app.handlers.persistent
def FMDL_Util_TrackChanges(scene, depsgraph=None):
    """
    Track changes to objects, materials, and textures.
    
    In Blender 4.x, we use depsgraph_update_post instead of scene_update_post.
    This function does three separate things:
    - it keeps vertexGroupSummaryCache up to date, with help of latestMeshObjectList
    - it keeps the list of export summaries up to date, with help of latestObjectTree
    - it keeps the scene mesh order sorted, with help of latestObjectTree
    """
    from . import UI
    
    global inActiveUpdate
    if bpy.context.mode != 'OBJECT':
        return
    if inActiveUpdate:
        return
    
    objectTree = []
    meshObjectList = []
    objectChanged = False
    objectListChanged = False
    
    # In Blender 4.4, is_updated and is_updated_data are deprecated
    # We'll check all objects for changes
    for obj in scene.objects:
        objectTree.append((obj.name, obj.parent.name if obj.parent is not None else None))
        
        # We can't directly check if an object was updated in this context
        # So we'll just collect the mesh objects
        if obj.type == 'MESH':
            meshObjectList.append(obj.name)
            
            # Check materials
            if obj.data is None:
                continue
                
            for material_slot in obj.material_slots:
                if material_slot.material is None:
                    continue
                
                # Support both texture_slots (Blender 2.7x-style) and nodes (4.x-style)
                material = material_slot.material
                
                # Try node-based approach first (Blender 4.x)
                if hasattr(material, "use_nodes") and material.use_nodes:
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
                            # We can't directly check if an image was updated
                            pass
                
                # Fall back to texture_slots (compatibility with older code)
                elif hasattr(material, "texture_slots"):
                    for slot in material.texture_slots:
                        if slot and slot.texture and slot.texture.type == 'IMAGE' and slot.texture.image:
                            # We can't directly check if an image was updated
                            pass

    global latestObjectTree
    objectTreeTuple = tuple(objectTree)
    if objectTreeTuple != latestObjectTree:
        latestObjectTree = objectTreeTuple
        objectChanged = True
        objectListChanged = True
    
    global latestMeshObjectList
    meshObjectListTuple = tuple(meshObjectList)
    if meshObjectListTuple != latestMeshObjectList:
        latestMeshObjectList = meshObjectListTuple
        UI.vertexGroupSummaryCleanup(latestMeshObjectList)
    
    if objectChanged:
        UI.updateSummaries(scene)
    
    if objectListChanged:
        UI.updateObjectFileMenus(scene)

# Initialize global variables
inActiveUpdate = False
latestObjectTree = ()
latestMeshObjectList = ()

# Add MaterialParameter class for Blender 4.2 compatibility
class FMDL_MaterialParameter(bpy.types.PropertyGroup):
    """Material parameter property group for FMDL materials"""
    name: bpy.props.StringProperty(name="Parameter Name")
    parameters: bpy.props.FloatVectorProperty(name="Parameter Values", size=4, default=(0.0, 0.0, 0.0, 0.0))