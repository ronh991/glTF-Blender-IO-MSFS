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
from .msfs_gizmo import MSFSGizmo
from .msfs_light import MSFSLight
from .msfs_material import MSFSMaterial
from .msfs_unique_id import MSFS_unique_id
from datetime import datetime

current_time = {"time": datetime.now(), "timestr": "Zero", "blender_ob": None}

def equality_check(arr1, arr2, size1, size2):
   if (size1 != size2):
      return False
   for i in range(0, size2):
      # blender python color channel issues in floats ???
      if (int(arr1[i] * 10000000)/10000000 != int(arr2[i] * 10000000)/10000000):
         return False
   return True

def global_time(blender_object):
    global current_time
    current_time["time"] = datetime.now()
    current_time["timestr"] = datetime.now().strftime("%H:%M:%S")
    current_time["blender_ob"] = blender_object


class Export:

    def fix_neutral_bone(self, gltf2_node):
        neutral_bone = None
        # base
        if gltf2_node is None:
            return None
        if gltf2_node.children is None:
            print("fix no children", gltf2_node.name)
            return None
        else:
            # node is orange armature, skin is green armature, joints is bones
            for c in gltf2_node.children:
                if c.mesh is not None and c.skin is not None:
                    print("child", c.name, c.mesh.name, c.skin.name)
                if c.skin is None:
                    neutral_bone = self.fix_neutral_bone(c)
                    if neutral_bone is None:
                        continue
                    else:
                        #pass
                        return neutral_bone
                else:
                    print("Skin name c", c.skin.name)
                    if c.skin.joints is not None:
                        for neutral_bone in c.skin.joints:
                            print("joints-bones found", neutral_bone.name)
                            if "neutral_bone" in neutral_bone.name:
                                neutral_bone.name = c.skin.name + "_neutral_bone"
                                print("Neutral Bone fixed", neutral_bone.name)
                                #return neutral_bone
                    else:
                        continue

                if neutral_bone is not None and neutral_bone.extensions is None:
                    neutral_bone.extensions = {}
                if self.properties.use_unique_id and neutral_bone is not None:
                    MSFS_unique_id.export_no_blender_object(neutral_bone)

        return None

    def gather_asset_hook(self, gltf2_asset, export_settings):
        #print("gather_asset_hook")
        if self.properties.enable_msfs_extension == True:
            #print("gather_asset_hook - ext true")
            if gltf2_asset.extensions is None:
                gltf2_asset.extensions = {}
            gltf2_asset.extensions["ASOBO_normal_map_convention"] = self.Extension(
                name="ASOBO_normal_map_convention",
                extension={"tangent_space_convention": "DirectX"},
                required=False
            )

            #print("gather_asset_hook - write version")
            gltf2_asset.generator += " and Asobo Studio MSFS Blender I/O v" + get_version_string()

        # for the vetex color rainbow
        # asset hook is called first before the nodes and objects and mesh, so we make changes to the meshes here
        # possible caching of blender data may result in changes not taking at the point of hook function running
        # does not work in:
        # def gather_mesh_hook(self, gltf2_mesh, blender_mesh, blender_object, vertex_groups, modifiers, skip_filter, materials, export_settings):

        # with 1.3.3 and my 1.6.3.1 changes to FLOAT_COLOR - this  may not be needed

        #print("gather_asset_hook - Started with ", gltf2_asset)
        selected_objects = bpy.context.selected_objects
        #active_object = bpy.context.active_object
        for o in selected_objects:
        #for o in bpy.context.scene.objects:
            #print("gather_asset_hook - Scene Object",o)
            # only for meshes
            if o.type == 'MESH':
                obj = o
                #print("gather_asset_hook - obj", obj, obj.data)
                for ca in obj.data.color_attributes:
                    #print("gather_asset_hook - ca",ca)
                    if ca.data_type != 'FLOAT_COLOR':
                        #print("gather_asset_hook - col before", obj, ca.domain, ca.data_type)
                        bpy.context.view_layer.objects.active = obj
                        #print("gather_asset_hook - col view_layer", obj, ca.domain, ca.data_type)
                        try:
                            bpy.ops.geometry.attribute_convert(mode='GENERIC', domain='CORNER', data_type='FLOAT_COLOR')
                        except:
                            print("*** MSFS WARNING *** - Error attribute convert to FLOAT COLOR", obj, obj.data, ca.domain, ca.data_type)
                        for ca in obj.data.color_attributes:
                            #print("gather_asset_hook - col after", obj, ca.data_type)
                            pass
        #print("gather_asset_hook - Done")

    # def gather_gltf_encoded_hook(self, export_settings, gltf_format, sort_order):
        # print("gather_gltf_encoded_hook - started")

    def gather_gltf_extensions_hook(self, gltf2_plan, export_settings):
        # print("gather_gltf_extensions_hook - export_settings", export_settings["gltf_user_extensions"])
        # for ex in export_settings["gltf_user_extensions"]:
            # print("ex", ex, ex.Extension, ex.properties, ex.properties.enabled, ex.properties.enable_msfs_extension, ex.properties.use_unique_id)

        # need to append a new export_setting to keep the user extensions in the list of user_extentions
        #export_settings.append ("gltf_user_extensions")
        # print("gltf extensions_used",gltf2_plan.extensions_used)
        # for extused in gltf2_plan.extensions_used:
            # print("EX used", extused)
            # # if ASOBO in name then add to gltf_need_to_keep_extension_declaration
            # # add into the gltf_need_to_keep_extension_declaration export_setting
        if self.properties.enable_msfs_extension:
            #print("gather_gltf_extensions_hook - enabled")
            for i, image in enumerate(gltf2_plan.images):
                image.uri = os.path.basename(urllib.parse.unquote(image.uri))

    def gather_node_hook(self, gltf2_object, blender_object, export_settings):
        if self.properties.enable_msfs_extension:
            if gltf2_object.extensions is None:
                gltf2_object.extensions = {}

            if self.properties.use_unique_id:
                MSFS_unique_id.export(gltf2_object, blender_object)

            if blender_object.type == 'LIGHT':
                MSFSLight.export(gltf2_object, blender_object)
    
    def gather_joint_hook(self, gltf2_node, blender_bone, export_settings):
        if self.properties.enable_msfs_extension:

            if gltf2_node.extensions is None:
                gltf2_node.extensions = {}

            if self.properties.use_unique_id:
                MSFS_unique_id.export(gltf2_node, blender_bone)

    def gather_scene_hook(self, gltf2_scene, blender_scene, export_settings):
        if self.properties.enable_msfs_extension and MSFSGizmo:
            #print("gather_scene_hook - properties enabled", MSFSGizmo)
            MSFSGizmo.export(gltf2_scene.nodes, blender_scene, export_settings)

        if self.properties.enable_msfs_extension:
            #print("Scene gltf2_scene_nodes", gltf2_scene.nodes, gltf2_scene.extras)
            for gltf2_node in gltf2_scene.nodes: 
                if gltf2_node is None:
                    continue
                if gltf2_node.children is None:
                    continue
                print("Scene node loop", gltf2_node.name)
                gltf2_object = self.fix_neutral_bone(gltf2_node)
                print("return Scene object", gltf2_object, gltf2_object.name if gltf2_object is not None else None)
                # there is no blender_object because of Khronos stupid neutral_bone thing

                if gltf2_object is not None and gltf2_object.extensions is None:
                    gltf2_object.extensions = {}
                if self.properties.use_unique_id and gltf2_object is not None:
                    MSFS_unique_id.export_no_blender_object(gltf2_object)

    def gather_material_hook(self, gltf2_material, blender_material, export_settings):
        # blender 4.0 and now 3.6 issue with detail textures added twice once correct and once as a regular basecolor texture
        # if it has a detail color texture then set basecolor texture to none
        #print("*** MSFS WARNING *** - gather_material_hook - Started with gltf2_material", gltf2_material, gltf2_material.pbr_metallic_roughness, gltf2_material.pbr_metallic_roughness.base_color_texture)
        #print("*** MSFS WARNING *** - gather_material_hook - blender material - delete base color before", blender_material, blender_material.msfs_detail_color_texture, blender_material.msfs_base_color_texture)
        print("gather_material_hook - bmat list", blender_material.msfs_base_color_texture, blender_material.msfs_detail_color_texture, blender_material.msfs_occlusion_metallic_roughness_texture)
        print("gather_material_hook - gmat list", gltf2_material.pbr_metallic_roughness.base_color_texture, gltf2_material.pbr_metallic_roughness.metallic_roughness_texture)
        if blender_material.msfs_detail_color_texture is not None and blender_material.msfs_base_color_texture is None:
            gltf2_material.pbr_metallic_roughness.base_color_texture = None
            print("*** MSFS WARNING *** - blender material - delete the base color", blender_material, blender_material.msfs_detail_color_texture, blender_material.msfs_base_color_texture)
        if gltf2_material.pbr_metallic_roughness.base_color_texture is not None and blender_material.msfs_base_color_texture is None:
            gltf2_material.pbr_metallic_roughness.base_color_texture = None
            print("*** MSFS WARNING *** - blender material - delete the base color - has gltf2 base color no blender texture", blender_material, gltf2_material.pbr_metallic_roughness.base_color_texture, blender_material.msfs_base_color_texture)
        if (gltf2_material.pbr_metallic_roughness.metallic_roughness_texture is not None or gltf2_material.occlusion_texture is not None) and blender_material.msfs_occlusion_metallic_roughness_texture is None:
            gltf2_material.pbr_metallic_roughness.metallic_roughness_texture = None
            gltf2_material.occlusion_texture = None
            print("*** MSFS WARNING *** - blender material - delete the OMR color - has gltf2 OMR color no blender texture", blender_material, gltf2_material.pbr_metallic_roughness.metallic_roughness_texture, blender_material.msfs_occlusion_metallic_roughness_texture)

        # late 4.2 change alphamode always set to BLEND
        # blender 4.2 June 6 beta - there is no longer a Blender Blend_mode variable - this was used to set the gltf alphaMode json
        # variable - since ASOBO now controls the msfs_alpha_mode - we must push this setting to the gltf and bypass the Khronos code - settings to BLEND
        # this BLEND setting causes the sim flickering of all textures. - what a mess
        #print("*** MSFS WARNING *** - alpha mode mat",blender_material.msfs_material_type, blender_material.msfs_alpha_mode, gltf2_material.alpha_mode)
        if blender_material.msfs_alpha_mode != gltf2_material.alpha_mode and gltf2_material.alpha_mode is not None:
            if blender_material.msfs_alpha_mode == "OPAQUE":
                before_gltf_alpha_mode = gltf2_material.alpha_mode
                if gltf2_material.alpha_mode != None:
                    gltf2_material.alpha_mode = None
                    print("*** MSFS WARNING *** - Force Khronos alpha mode changed to Opaque/None",blender_material.msfs_material_type, blender_material.name, blender_material.msfs_alpha_mode, gltf2_material.alpha_mode, "gltf alpha mode was", before_gltf_alpha_mode)
            else:
                gltf2_material.alpha_mode = blender_material.msfs_alpha_mode
                print("*** MSFS WARNING *** - Force Khrons alpha mode changed",blender_material.msfs_material_type, blender_material.name, blender_material.msfs_alpha_mode, gltf2_material.alpha_mode)

        if self.properties.enable_msfs_extension:
            #print("*** MSFS WARNING *** - gather_material_hook - extenson export")
            MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        #print("*** MSFS WARNING *** - gather_material_hook - Done")

    # def gather_image_hook(self, image, blender_shader_sockets, export_settings):
        # print("*** MSFS WARNING *** - gather_image_hook - Started with ", image, blender_shader_sockets)
        # #print("exportsettings", export_settings)
        # print("*** MSFS WARNING *** gather_image_hook - image", image.name, image.mime_type, image.uri)
        # #if self.properties.enabled:
            # #MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        # print("*** MSFS WARNING *** - gather_image_hook - Done")

    # def pre_gather_tracks_hook(self, blender_object, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("pre_gather_tracks_hook - Started with ", current_time, blender_object)
        # print("pre_gather_tracks_hook - Done")

    # def animation_track_switch_loop_hook(self, blender_object, Done, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # if not Done:
            # print("animation_track_switch_loop_hook - Started with ", current_time, blender_object)
        # if Done:
            # print("animation_track_switch_loop_hook - Done", current_time, blender_object)

    def animation_switch_loop_hook(self, blender_object, Done, export_settings):
        if not Done:
            global_time(blender_object)
            #print("animation_switch_loop_hook - Started with ", current_time, blender_object)
            return
        c = datetime.now() - current_time["time"]
        #minutes = c.total_seconds() / 60
        #print("minutes", minutes, c, current_time["time"], c.total_seconds(), blender_object, current_time["blender_ob"], Done)
        if c.total_seconds() > 2 and blender_object == current_time["blender_ob"] and blender_object is not None:
            if Done:
                print("animation_switch_loop_hook - Long animation KF build - CHECK", c.total_seconds(), " seconds (>2) ", blender_object, c)
                global_time(None)

    # def pre_animation_track_switch_hook(self, blender_object, blender_action, track_name, on_type, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("pre_animation_track_switch_hook - Started with ", current_time, blender_object, blender_action, track_name, on_type)
        # print("pre_animation_track_switch_hook - Done")

    # def pre_animation_switch_hook(self, blender_object, blender_action, track_name, on_type, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("pre_animation_switch_hook - Started with ", current_time, blender_object, blender_action, track_name, on_type)
        # print("pre_animation_switch_hook - Done")

    # def post_animation_track_switch_hook(self, blender_object, blender_action, track_name, on_type, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("post_animation_track_switch_hook - Started with ", current_time, blender_object, blender_action, track_name, on_type)
        # print("post_animation_track_switch_hook - Done")

    # def post_animation_switch_hook(self, blender_object, blender_action, track_name, on_type, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("post_animation_switch_hook - Started with ", current_time, blender_object, blender_action, track_name, on_type)
        # print("post_animation_switch_hook - Done")

    # def gather_tracks_hook(self, blender_object, gathertrackhookparams, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("gather_tracks_hook - Started with ", current_time, blender_object, gathertrackhookparams)
        # print("gather_tracks_hook - Done")

    # def gather_actions_hook(self, blender_object, gatheractionhookparams, export_settings):
        # from datetime import datetime
        # now = datetime.now()
        # current_time = now.strftime("%H:%M:%S")
        # print("gather_actions_hook - Started with ", current_time, blender_object, gatheractionhookparams)
        # print("gather_actions_hook - Done")

    # def gather_texture_info_hook(self, texture_info, blender_shader_sockets, export_settings):
        # print("gather_texture_info_hook - Started with ", blender_shader_sockets)
        # #print("exportsettings", export_settings)
        # print("gather_texture_info_hook - texture_info", texture_info.extensions, texture_info.extras, texture_info.index)
        # # if self.properties.enabled:
            # #pass
            # # MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        # print("gather_texture_info_hook - Done")

    # def gather_material_pbr_metallic_roughness_hook(self, gltf2_material, blender_material, orm_texture, export_settings):
        # print("gather_material_pbr_metallic_roughness_hook - Started with ", gltf2_material.base_color_texture)
        # #print("exportsettings", export_settings)
        # print("blender_material", blender_material, blender_material.msfs_base_color_texture, blender_material.msfs_detail_color_texture)
        # #if self.properties.enabled:
            # #MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        # print("gather_material_pbr_metallic_roughness_hook - Done")

    # def gather_import_texture_before_hook(gltf, pytexture, mh, tex_info, location, label, color_socket, alpha_socket, is_data):
        # print("gather_import_texture_before_hook - Started with ", gltf)
        # #print("exportsettings", export_settings)
        # print("arg material", pytexture, mh, tex_info, location, label, color_socket, alpha_socket, is_data)
        # #if self.properties.enabled:
            # #MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        # print("gather_import_texture_before_hook - Done")

    # def gather_import_texture_after_hook(gltf, pytexture, mh, tex_info, location, label, color_socket, alpha_socket, is_data):
        # print("gather_import_texture_after_hook - Started with ", gltf)
        # #print("exportsettings", export_settings)
        # print("arg material", pytexture, mh, tex_info, location, label, color_socket, alpha_socket, is_data)
        # #if self.properties.enabled:
            # #MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        # print("gather_import_texture_after_hook - Done")

    # def gather_texture_hook(self, texture, blender_shader_sockets, export_settings):
        # print("gather_texture_hook - Started with ", blender_shader_sockets)
        # #print("exportsettings", export_settings)
        # print("texture", texture.name, texture.sampler, texture.extras, texture.source.name)
        # #if self.properties.enabled:
            # #MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        # print("gather_texture_hook - Done")
