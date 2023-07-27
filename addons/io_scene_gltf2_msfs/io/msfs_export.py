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

import os
import urllib
import bpy

from .. import get_version_string
#from .. import get_prefs
#from io_scene_gltf2 import ExportGLTF2_Base
from io_scene_gltf2.blender.exp.gltf2_blender_gather_materials_emission import export_emission_factor
from .msfs_gizmo import MSFSGizmo
from .msfs_light import MSFSLight
from .msfs_material import MSFSMaterial
from .msfs_unique_id import MSFS_unique_id
from .msfs_material_animation import MSFSMaterialAnimation


class Export:

    gathered_material_actions = []
    
    # get the preferences set in add-on intall menu
    #addonpreferences = get_prefs()
    #texture_dir = ''
    #copyright = ''
    #print(addonpreferences)
    #print("addon preferences - ", addonpreferences.export_texture_dir, addonpreferences.export_copyright)
    #texture_dir = addonpreferences.export_texture_dir
    #copyright = addonpreferences.export_copyright
    #print("base GLTF", ExportGLTF2_Base.export_format)
    # ExportGLTF2_Base.export_format = ''
    # ExportGLTF2_Base.export_format.default = 'GLTF_SEPARATE'

    def gather_asset_hook(self, gltf2_asset, export_settings):
        if self.properties.enabled == True:
            if gltf2_asset.extensions is None:
                gltf2_asset.extensions = {}
            gltf2_asset.extensions["ASOBO_normal_map_convention"] = self.Extension(
                name="ASOBO_normal_map_convention",
                extension={"tangent_space_convention": "DirectX"},
                required=False
            )

            gltf2_asset.generator += " and Asobo Studio MSFS Blender I/O v" + get_version_string()

    def gather_gltf_extensions_hook(self, gltf2_plan, export_settings):
        print("gather_gltf_extensions_hook - start", self.properties.enabled)
        if self.properties.enabled:
            for i, image in enumerate(gltf2_plan.images):
                image.uri = os.path.basename(urllib.parse.unquote(image.uri))
            print("gather_gltf_extensions_hook - for animation", gltf2_plan.animations)
            for animation in gltf2_plan.animations:
                print("gather_gltf_extensions_hook - animation", animation)
                MSFSMaterialAnimation.finalize_target(animation, gltf2_plan)

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if self.properties.enabled:

            if gltf2_object.extensions is None:
                gltf2_object.extensions = {}

            if self.properties.use_unique_id:
                MSFS_unique_id.export(gltf2_object, blender_object)

            if blender_object.type == 'LIGHT':
                MSFSLight.export(gltf2_object, blender_object)
    
    def gather_joint_hook(self, gltf2_node, blender_bone, export_settings):
        if self.properties.enabled:

            if gltf2_node.extensions is None:
                gltf2_node.extensions = {}

            if self.properties.use_unique_id:
                MSFS_unique_id.export(gltf2_node, blender_bone)

    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        if self.properties.enabled:
            MSFSGizmo.export(gltf2_scene.nodes, blender_scene, export_settings)

    def gather_material_hook(self, gltf2_material, blender_material, export_settings):
        if self.properties.enabled:
            # KHR_materials_emissive_strength issue with msfs materials for bloom

            # KHR_materials_emissive_strength revert the Khronos gltf code to add an extension for emissive scale > 1.0
            # return the emissive_factor back to the missive color multiplied by the emissive scale
            for extension in gltf2_material.extensions:
                if extension:
                    print("gather_gltf_extensions_hook - KHR Extension", gltf2_material.name, gltf2_material.extensions, extension, gltf2_material.emissive_factor)
                    if extension == "KHR_materials_emissive_strength":

                        for colorChannel in blender_material.node_tree.nodes['Emissive RGB'].outputs[0].default_value[0:3]:
                            print ("gather_gltf_extensions_hook - Color value", colorChannel)
                        maxchannel = max(blender_material.node_tree.nodes['Emissive RGB'].outputs[0].default_value[0:3])
                        emissive_scale = blender_material.node_tree.nodes['Emissive Scale'].outputs[0].default_value
                        print("gather_gltf_extensions_hook - maxchannel", maxchannel, emissive_scale)

                        print("gather_gltf_extensions_hook - change remove emissive_factor KHR_materials_emissive_strength")
                        gltf2_material.emissive_factor = [f * maxchannel * emissive_scale for f in gltf2_material.emissive_factor]
                        del gltf2_material.extensions['KHR_materials_emissive_strength']

            MSFSMaterial.export(gltf2_material, blender_material, export_settings)

    def gather_actions_hook(self, blender_object, blender_actions, blender_tracks, action_on_type, export_settings):
        print("gather_actions_hook - Started")
        if self.properties.enabled:
            print("gather_actions_hook", blender_object)
            # Keep track of what material actions we've already exported - no need to export it more than once. All values passed to the hook get modified by reference
            found_blender_actions, found_blender_tracks, found_action_on_type = MSFSMaterialAnimation.gather_actions(blender_object, self.gathered_material_actions, export_settings)

            if found_blender_actions:
                print("gather_actions_hook - Found Blender Actions", found_blender_actions)
                blender_actions.extend(found_blender_actions)
                self.gathered_material_actions.extend(found_blender_actions)
            if found_blender_tracks:
                print("gather_actions_hook - Found Blender Tracks", found_blender_tracks)
                blender_tracks.update(found_blender_tracks)
            if found_action_on_type:
                print("gather_actions_hook - Found Blender Action on type", found_action_on_type)
                action_on_type.update(found_action_on_type)
        print("gather_actions_hook - Done")

    # need a gather_animation_channel_hook ?????
    def gather_animation_channel_hook(self, gltf2_animation_channel, channels, blender_object, bake_bone, bake_channel, bake_range_start, bake_range_end, action_name, export_settings):
        print("gather_animation_channel_hook - Started with ", gltf2_animation_channel, channels, blender_object, action_name)
        # not needed???? MSFSMaterialAnimation.gather_channels(gltf2_animation_channel, channels, blender_object, bake_bone, bake_channel, bake_range_start, bake_range_end, action_name, export_settings)
        print("gather_animation_channel_hook - Done")

    def gather_animation_channel_target_hook(self, gltf2_animation_channel_target, channels, blender_object, bake_bone, bake_channel, export_settings):
        print("gather_animation_channel_target_hook - Started with ", gltf2_animation_channel_target, channels, blender_object)
        MSFSMaterialAnimation.replace_channel_target(gltf2_animation_channel_target, channels, blender_object, export_settings)
        print("gather_animation_channel_target_hook - Done")

    def pre_gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        print("pre_gather_animation_hook - add_placeholder_channel Started")
        MSFSMaterialAnimation.add_placeholder_channel(gltf2_animation, blender_action, blender_object, export_settings)
        print("pre_gather_animation_hook - add_placeholder_channel Done")

    def gather_animation_hook(self, gltf2_animation, blender_action, blender_object, export_settings):
        print("gather_animation_hook - finalize_animation Started", gltf2_animation, blender_action, blender_object)
        MSFSMaterialAnimation.finalize_animation(gltf2_animation)
        print("gather_animation_hook - finalize_animation Done", gltf2_animation, blender_action, blender_object)
