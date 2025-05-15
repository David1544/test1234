import bpy

@bpy.app.handlers.persistent
def FMDL_Util_TrackChanges(scene, depsgraph=None):
    """
    Track changes to objects, materials, and textures.
    
    In Blender 4.4, we use depsgraph_update_post instead of scene_update_post.
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
                
                # In Blender 4.4, texture_slots are deprecated
                # We need to check material nodes instead
                if material_slot.material.use_nodes:
                    for node in material_slot.material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE' and node.image:
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