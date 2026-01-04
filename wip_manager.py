bl_info = {
    "name": "WIP Manager Ultimate",
    "author": "Expert Blender Dev",
    "version": (3, 5),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > WIP",
    "description": "Gestion complète de projet WIP",
    "category": "Development",
}

import bpy
import os
import re
import datetime
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty

# ------------------------------------------------------------------------
#   Opérateur : Génération (Reste inchangé)
# ------------------------------------------------------------------------

class WIP_OT_CreateFolders(bpy.types.Operator):
    bl_idname = "wip.create_folders"
    bl_label = "Générer Structure"
    
    def execute(self, context):
        wip_tool = context.scene.wip_props
        
        if not wip_tool.project_root:
            self.report({'ERROR'}, "Veuillez choisir un dossier racine")
            return {'CANCELLED'}

        # Nettoyage nom
        clean_name = wip_tool.title.strip()
        clean_name = re.sub(r'[^a-zA-Z0-9\s_\-]', '', clean_name)
        clean_name = clean_name.replace(" ", "_")
        if not clean_name: clean_name = "Untitled_Project"

        # Chemins
        base_path = bpy.path.abspath(wip_tool.project_root)
        project_path = os.path.join(base_path, clean_name)
        scene_path = os.path.join(project_path, "scene")

        try:
            # Création dossiers
            for sub in ["scene", "materials", "refs", "rendus"]:
                os.makedirs(os.path.join(project_path, sub), exist_ok=True)

            # Création README
            readme_path = os.path.join(project_path, "info.txt")
            now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            
            types = []
            if wip_tool.is_archi: types.append("Architecture")
            if wip_tool.is_landscape: types.append("Paysage")
            if wip_tool.is_abstract: types.append("Abstrait")
            
            content =f"""PROJET : {wip_tool.title}
DATE   : {now}
TYPE   : {", ".join(types)}
STATUS : {wip_tool.status}
--------------------------------------------------
[CONCEPT]
{wip_tool.concept}

[DESCRIPTION]
{wip_tool.description}

[LIENS]
{wip_tool.link_ref}
"""
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Auto-Save Blend
            blend_filename = f"{clean_name}_v001.blend"
            full_blend_path = os.path.join(scene_path, blend_filename)
            bpy.ops.wm.save_as_mainfile(filepath=full_blend_path)
            
            self.report({'INFO'}, f"Projet sauvegardé : {blend_filename}")
            bpy.ops.wm.path_open(filepath=project_path)

        except Exception as e:
            self.report({'ERROR'}, f"Erreur : {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

# ------------------------------------------------------------------------
#   Propriétés
# ------------------------------------------------------------------------

class WIP_Properties(bpy.types.PropertyGroup):
    # SETUP
    title: StringProperty(name="Titre", default="Projet Sans Titre")
    project_root: StringProperty(name="Racine", subtype='DIR_PATH', default="//")

    # DETAILS
    is_archi: BoolProperty(name="Archi", default=False)
    is_landscape: BoolProperty(name="Paysage", default=False)
    is_abstract: BoolProperty(name="Abstrait", default=False)
    
    concept: StringProperty(name="Concept", default="")
    description: StringProperty(name="Description", default="")
    
    # STATUS & REF
    status: EnumProperty(
        name="Statut",
        items=[
            ('IN_PROGRESS', "En cours", "", 'PLAY', 0),
            ('STANDBY', "Standby", "", 'PAUSE', 1),
            ('ABANDONED', "Stop", "", 'CANCEL', 2),
            ('FINISHED', "Fini", "", 'CHECKBOX_HLT', 3),
        ],
        default='IN_PROGRESS'
    )
    
    link_ref: StringProperty(name="Lien Tuto", subtype='FILE_PATH', description="URL ou chemin")
    ref_image_path: StringProperty(name="Image Ref", subtype='FILE_PATH', description="Image de référence")

    # TODO LIST
    todo_modeling: BoolProperty(name="Modélisation", default=False)
    todo_uvs: BoolProperty(name="UVs / Unwrap", default=False)
    todo_texturing: BoolProperty(name="Texturing", default=False)
    todo_lighting: BoolProperty(name="Lighting", default=False)
    todo_compositing: BoolProperty(name="Compositing", default=False)
    todo_rendering: BoolProperty(name="Rendu", default=False)

# ------------------------------------------------------------------------
#   Interface
# ------------------------------------------------------------------------

class WIP_PT_Panel(bpy.types.Panel):
    bl_label = "WIP Manager"
    bl_idname = "WIP_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'WIP'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if not hasattr(scene, "wip_props"):
            layout.label(text="Erreur chargement props - Redémarrer Blender")
            return
            
        wip_tool = scene.wip_props

        # --- 1. SETUP ---
        box = layout.box()
        box.label(text="Projet", icon="FILE_FOLDER")
        box.prop(wip_tool, "title")
        box.prop(wip_tool, "project_root", text="")
        row = box.row()
        row.scale_y = 1.5
        row.operator("wip.create_folders", icon="EXPORT", text="Générer & Sauver")

        # --- 2. INFOS GENERALES ---
        layout.label(text="Informations :", icon="INFO")
        box = layout.box()
        
        row = box.row()
        row.prop(wip_tool, "is_archi")
        row.prop(wip_tool, "is_landscape")
        row.prop(wip_tool, "is_abstract")
        
        box.prop(wip_tool, "concept", text="Concept")
        box.prop(wip_tool, "description", text="Notes")

        # --- 3. STATUT & LIENS ---
        layout.separator()
        box = layout.box()
        box.label(text="Suivi & Références :", icon="URL")
        
        row = box.row()
        row.prop(wip_tool, "status", expand=True)
        
        box.prop(wip_tool, "link_ref", icon="WORLD")
        
        row = box.row(align=True)
        row.prop(wip_tool, "ref_image_path", text="")
        
        if wip_tool.ref_image_path:
            # Correction de l'icône FILE_IMAGE par l'icône de dossier plus sûre
            row.operator("wm.path_open", text="Ouvrir", icon="FILE_FOLDER").filepath = wip_tool.ref_image_path
        else:
            row.label(text="", icon="IMAGE_DATA")


        # --- 4. TO-DO LIST (CORRIGÉE) ---
        layout.separator()
        box = layout.box()
        # Ligne 197 : Correction de l'icône "CHECKLIST" par "MENU_PANEL"
        box.label(text="To-Do List :", icon="MENU_PANEL")
        col = box.column(align=True)
        col.prop(wip_tool, "todo_modeling")
        col.prop(wip_tool, "todo_uvs")
        col.prop(wip_tool, "todo_texturing")
        col.prop(wip_tool, "todo_lighting")
        col.prop(wip_tool, "todo_compositing")
        col.prop(wip_tool, "todo_rendering")

# ------------------------------------------------------------------------
#   Registration
# ------------------------------------------------------------------------

classes = (
    WIP_OT_CreateFolders,
    WIP_Properties,
    WIP_PT_Panel,
)

def register():
    if hasattr(bpy.types.Scene, "wip_props"):
        del bpy.types.Scene.wip_props
        
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.wip_props = PointerProperty(type=WIP_Properties)

def unregister():
    if hasattr(bpy.types.Scene, "wip_props"):
        del bpy.types.Scene.wip_props
        
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()