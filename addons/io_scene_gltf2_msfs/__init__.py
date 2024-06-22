# Copyright 2021-2022 The glTF-Blender-IO-MSFS authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib
import inspect
import pkgutil
from pathlib import Path

import bpy
import os
import toml

bl_info = {
    "name": "Microsoft Flight Simulator glTF Extension",
    "author": "Luca Pierabella, Yasmine Khodja, Wing42, pepperoni505, ronh991, and others",
    "description": "This toolkit prepares your 3D assets to be used for Microsoft Flight Simulator",
    "blender": (4, 2, 0),
    "version": (2, 2, 9),
    "location": "File > Export > glTF 2.0",
    "category": "Import-Export",
    "developer":"Luca Pierabella, Yasmine Khodja, Wing42, pepperoni505, ronh991, and others",
    "tracker_url": "https://github.com/ronh991/glTF-Blender-IO-MSFS"
}

#from os import path as p

def get_version_string():
    SCRIPT_DIR = os.path.dirname(__file__)
    manifest_file = os.path.join(SCRIPT_DIR, "blender_manifest.toml")
    bl_info=toml.load(manifest_file)
    return bl_info["version"]

#get the folder path for the .py file containing this function
def get_path():
    return os.path.dirname(os.path.realpath(__file__))


#get the name of the "base" folder
def get_name():
    return os.path.basename(get_path())

## somehow these should also update the gltf export settings
def on_export_texture_folder_changed(self, context):
    # Update the texture folder name
    # changes
    settings = bpy.context.scene.msfs_multi_exporter_settings
    settings.export_texture_dir = self.export_texture_dir
    return

def on_export_copyright_changed(self, context):
    # Update the copyright data
    # changes
    settings = bpy.context.scene.msfs_multi_exporter_settings
    settings.export_copyright = self.export_copyright
    return

# def on_export_vertexcolor_project_changed(self, context):
    # # Update the vertex color setting data
    # # changes
    # settings = bpy.context.scene.msfs_multi_exporter_settings
    # settings.export_vertexcolor_project = self.export_vertexcolor_project
    # return


#now that we have the addons name we can get the preferences
def get_prefs():
    #return bpy.context.preferences.addons[get_name()].preferences
    return bpy.context.preferences.addons[__package__].preferences

## class to add the preference settings
class addSettingsPanel(bpy.types.AddonPreferences):
    bl_idname = __package__
 
    export_texture_dir: bpy.props.StringProperty (
        #name = "Default Texture Location",
        description = "Default Texture Location",
        default = "../texture/",
        update=on_export_texture_folder_changed
    )

    export_copyright: bpy.props.StringProperty (
        #name = "Default Copyright Name",
        description = "Default Copyright Name",
        default = "Your Copyright Here",
        update=on_export_copyright_changed
    )

    export_vertexcolor_project: bpy.props.BoolProperty (
        #name = "This Project uses Vertex Color Nodes",
        description = "Indicates if the project uses Vertex Color on mesh",
        default = False
        #update=on_export_vertexcolor_project_changed
    )

    ## draw the panel in the addon preferences
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Optional - You can set the multi-export default values. This will be used in the multi-export window ONLY", icon='INFO')

        box = layout.box()
        col = box.column(align = False)

        ## texture default location
        col.prop(self, "export_texture_dir", text="Default Texture Location")

        ## default copyright
        col.prop(self, "export_copyright", text="Default Copyright Name")

        ## default vertex color project
        col.prop(self, "export_vertexcolor_project", text="This Project uses Vertex Color Nodes")

class MSFS_ImporterProperties(bpy.types.PropertyGroup):
    enable_msfs_extension: bpy.props.BoolProperty(
        name='Microsoft Flight Simulator Extensions',
        description='Enable MSFS glTF import extensions',
        default=True
    )

class MSFS_ExporterProperties(bpy.types.PropertyGroup):
    def msfs_enable_msfs_extension_update(self, context):
        #props = bpy.context.scene.msfs_exporter_settings
        props = bpy.context.scene.MSFS_ExporterProperties
        settings = bpy.context.scene.msfs_multi_exporter_settings
        settings.enable_msfs_extension = props.enable_msfs_extension

    enabled: bpy.props.BoolProperty(
        name=bl_info["name"],
        description='Include this extension in the exported glTF file.',
        default=True
        )

    enable_msfs_extension: bpy.props.BoolProperty(
        name='Microsoft Flight Simulator Extensions',
        description='Enable MSFS glTF export extensions',
        default=True,
        update=msfs_enable_msfs_extension_update
    )

    use_unique_id: bpy.props.BoolProperty(
        name='Use ASOBO Unique ID',
        description='use ASOBO Unique ID extension',
        default=True,
    )
    

# class GLTF_PT_MSFSImporterExtensionPanel(bpy.types.Panel):
    # bl_space_type = 'FILE_BROWSER'
    # bl_region_type = 'TOOL_PROPS'
    # bl_label = ""
    # bl_parent_id = "GLTF_PT_import_user_extensions"
    # bl_location = "File > Import > glTF 2.0"

    # @classmethod
    # def poll(cls, context):
        # sfile = context.space_data
        # operator = sfile.active_operator
        # return operator.bl_idname == "IMPORT_SCENE_OT_gltf"

    # def draw_header(self, context):
        # layout = self.layout
        # layout.label(text="MSFS Extensions", icon='TOOL_SETTINGS')

    # def draw(self, context):
        # props = bpy.context.scene.msfs_importer_properties

        # layout = self.layout
        # layout.use_property_split = True
        # layout.use_property_decorate = False  # No animation.

        # layout.prop(props, 'enable_msfs_extension', text="Enabled")

# class GLTF_PT_MSFSExporterExtensionPanel(bpy.types.Panel):
    # bl_space_type = 'FILE_BROWSER'
    # bl_region_type = 'TOOL_PROPS'
    # bl_label = ""
    # bl_parent_id = "GLTF_PT_export_user_extensions"
    # bl_location = "File > Export > glTF 2.0"

    # @classmethod
    # def poll(cls, context):
        # sfile = context.space_data
        # operator = sfile.active_operator
        # return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

    # def draw_header(self, context):
        # layout = self.layout
        # layout.label(text="Microsoft Flight Simulator Extensions", icon='TOOL_SETTINGS')

    # def draw(self, context):
        # props = bpy.context.scene.msfs_exporter_settings

        # layout = self.layout
        # layout.use_property_split = True
        # layout.use_property_decorate = False  # No animation.

        # layout.prop(props, 'enable_msfs_extension', text="Enabled")
        # if props.enable_msfs_extension:
            # layout.prop(props, 'use_unique_id', text="Enable ASOBO Unique ID extension")

def recursive_module_search(path, root=""):
    for _, name, ispkg in pkgutil.iter_modules([str(path)]):
        if ispkg:
            yield from recursive_module_search(path / name, f"{root}.{name}")
        else:
            yield root, name


def modules():
    for root, name in recursive_module_search(Path(__file__).parent):
        if name in locals():
            yield importlib.reload(locals()[name])
        else:
            yield importlib.import_module(f".{name}", package=f"{__package__}{root}")


classes = []
extension_classes = [MSFS_ImporterProperties, MSFS_ExporterProperties]

# Refresh the list of classes
def update_class_list():
    global classes

    classes = []

    for module in modules():
        for obj in module.__dict__.values():
            if inspect.isclass(obj) \
                    and module.__name__ in str(obj) \
                    and "bpy" in str(inspect.getmro(obj)[1]):
                classes.append(obj)


def register():
    bpy.utils.register_class(addSettingsPanel)
    # Refresh the list of classes whenever the addon is reloaded so we can stay up to date with the files on disk.
    update_class_list()

    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            print("ERROR in register classes", cls)
            pass

    for module in modules():
        if hasattr(module, "register"):
            module.register()

    for cls in extension_classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            print("ERROR in register extension classes", cls)
            pass

    bpy.types.Scene.MSFS_ImporterProperties = bpy.props.PointerProperty(type=MSFS_ImporterProperties)
    bpy.types.Scene.MSFS_ExporterProperties = bpy.props.PointerProperty(type=MSFS_ExporterProperties)


def unregister():
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass

    for module in modules():
        if hasattr(module, "unregister"):
            module.unregister()

    for cls in extension_classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.MSFS_ExporterProperties
    bpy.utils.unregister_class(addSettingsPanel)

def draw(self, layout):
    header, body = layout.panel("GLTF_addon_msfs_exporter", default_closed=False)
    #print("header body", header, body, header.active, header.enabled)
    props = bpy.context.scene.MSFS_ExporterProperties
    if body is not None:
        body.use_property_decorate = False  # No animation.

        body.prop(props, 'enable_msfs_extension', text="Enabled")
        if props.enable_msfs_extension:
            body.prop(props, 'use_unique_id', text="Enable ASOBO Unique ID extension")

    header.label(text="Microsoft Flight Simulator Extensions")

##################################################################################
from .io.msfs_import import Import


class glTF2ImportUserExtension(Import):
    def __init__(self):
        self.properties = bpy.context.scene.msfs_importer_properties


##################################################################################
from .io.msfs_export import Export


class glTF2ExportUserExtension(Export):
    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        #print("glTF2ExportUserExtension - __init__ start")
        self.Extension = Extension
        #print("glTF2ExportUserExtension - __init__ extension", Extension)
        self.properties = bpy.context.scene.MSFS_ExporterProperties
        #print("glTF2ExportUserExtension - __init__ properties", bpy.context.scene.msfs_exporter_properties)
