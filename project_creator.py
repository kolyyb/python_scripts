import bpy
import os
import pathlib
from bpy.types import Menu, Operator
from bpy.utils import register_class, unregister_class

# --- Configuration de l'Add-on ---
bl_info = {
    "name": "Project Creator",
    "author": "Votre Nom",
    "version": (1, 0, 0),
    "blender": (4, 0, 0), # Version minimale de Blender supportée
    "location": "File > New > Project",
    "description": "Crée une nouvelle structure de projet avec les dossiers standard (scene, Material, ref, Rendu).",
    "category": "System",
}

# --- Dossiers à créer ---
PROJECT_FOLDERS = ["scene", "Material", "ref", "Rendu"]

# --- Opérateur (La logique de création) ---
class PROJECT_OT_create_new_project(Operator):
    """Crée un nouveau projet et sa structure de dossiers."""
    bl_idname = "project.create_new_project" # <--- IMPORTANT: doit être en minuscules et contenir un point (type.nom)
    bl_label = "Nouveau Projet Structuré"
# ... reste de la classe
    
    # Propriété pour stocker le chemin de base choisi par l'utilisateur
    directory: bpy.props.StringProperty(
        name="Dossier Parent du Projet",
        description="Sélectionnez le répertoire où le nouveau dossier de projet sera créé (par exemple: D:/MesProjets)",
        subtype='DIR_PATH',
    )
    
    # Propriété pour le nom du nouveau dossier de projet
    project_name: bpy.props.StringProperty(
        name="Nom du Projet",
        description="Nom du dossier principal du nouveau projet (ex: MonSuperFilm)",
        default="NouveauProjet",
    )

    def execute(self, context):
        # 1. Nettoyer et valider les chemins
        base_dir = pathlib.Path(self.directory).resolve()
        project_dir_name = self.project_name.strip()
        
        if not base_dir.is_dir() or not project_dir_name:
            self.report({'ERROR'}, "Chemin de base ou nom de projet invalide.")
            return {'CANCELLED'}

        # Chemin complet du nouveau projet
        project_path = base_dir / project_dir_name

        # 2. Créer le dossier principal du projet
        try:
            os.makedirs(project_path, exist_ok=False)
            self.report({'INFO'}, f"Dossier de projet créé : {project_path}")
        except FileExistsError:
            self.report({'ERROR'}, f"Le dossier de projet '{project_dir_name}' existe déjà à cet emplacement.")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erreur lors de la création du dossier principal : {e}")
            return {'CANCELLED'}

        # 3. Créer les sous-dossiers
        for folder in PROJECT_FOLDERS:
            folder_path = project_path / folder
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                self.report({'ERROR'}, f"Erreur lors de la création du sous-dossier '{folder}' : {e}")
                # Continuer pour essayer de créer les autres dossiers
                
        # 4. Enregistrer la scène Blender par défaut dans le dossier 'scene'
        try:
            default_scene_path = project_path / "scene" / (project_dir_name + "_main.blend")
            bpy.ops.wm.save_as_mainfile(filepath=str(default_scene_path))
            self.report({'INFO'}, f"Scène enregistrée dans : {default_scene_path}")
            
            # (Optionnel) Changer le chemin de travail de Blender pour le nouveau projet
            # context.preferences.filepaths.asset_libraries_path = str(project_path) # Ex: Changer les chemins de bibliothèque
            
        except Exception as e:
            self.report({'WARNING'}, f"Impossible d'enregistrer la scène Blender par défaut : {e}")


        self.report({'INFO'}, f"Structure de projet '{project_dir_name}' créée avec succès à l'emplacement : {project_path}")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Ouvre une fenêtre de dialogue pour que l'utilisateur choisisse le chemin et le nom
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def menu_func(self, context):
    """Ajoute l'opérateur au menu File > New."""
    self.layout.separator()
    # Suppression du paramètre 'icon' pour éviter le TypeError
    self.layout.operator(PROJECT_OT_create_new_project.bl_idname, text=PROJECT_OT_create_new_project.bl_label)


# --- Enregistrement et Désenregistrement de l'Add-on ---
classes = (
    PROJECT_OT_create_new_project,
)

def register():
    """Fonction appelée à l'activation de l'Add-on."""
    
    # 1. ENREGISTREMENT DES CLASSES (L'Opérateur est ici)
    for cls in classes:
        register_class(cls)
        
    # 2. AJOUT DU MENU (Doit arriver après l'enregistrement des classes)
    # L'opérateur PROJECT_OT_create_new_project est désormais connu de Blender.
    bpy.types.TOPBAR_MT_file_new.append(menu_func)

def unregister():
    """Fonction appelée à la désactivation de l'Add-on."""
    
    # 1. RETRAIT DU MENU (Doit arriver avant le désenregistrement des classes)
    bpy.types.TOPBAR_MT_file_new.remove(menu_func)

    # 2. DÉSENREGISTREMENT DES CLASSES
    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
    # Pour le test direct dans l'éditeur de texte de Blender :
    # bpy.ops.project.create_new_project('INVOKE_DEFAULT') 
