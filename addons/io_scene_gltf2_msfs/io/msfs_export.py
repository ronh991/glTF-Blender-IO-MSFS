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


def equality_check(arr1, arr2, size1, size2):
   if (size1 != size2):
      return False
   for i in range(0, size2):
      # blender python color channel issues in floats ???
      if (int(arr1[i] * 10000000)/10000000 != int(arr2[i] * 10000000)/10000000):
         return False
   return True

class Export:
    
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

        # for the vetex color rainbow
        # asset hook is called first before the nodes and objects and mesh, so we make changes to the meshes here
        # possible caching of blender data may result in changes not takeng at the point of hook function running
        # does not work in:
        # def gather_mesh_hook(self, gltf2_mesh, blender_mesh, blender_object, vertex_groups, modifiers, skip_filter, materials, export_settings):

        #print("gather_asset_hook - Started with ", gltf2_asset)
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        for o in selected_objects:
        #for o in bpy.context.scene.objects:
            #print("gather_asset_hook - Scene Object",o)
            # only for meshes
            if o.type == 'MESH':
                obj = o
                #print("gather_asset_hook - obj", obj, obj.data)
                for ca in obj.data.color_attributes:
                    if ca.data_type != 'FLOAT_COLOR':
                        #print("gather_asset_hook - col before", obj, ca.domain, ca.data_type)
                        bpy.context.view_layer.objects.active = obj
                        #print("gather_asset_hook - col view_layer", obj, ca.domain, ca.data_type)
                        bpy.ops.geometry.attribute_convert(mode='GENERIC', domain='CORNER', data_type='FLOAT_COLOR')
                        #print("gather_asset_hook - After", obj, obj.data)
                        for ca in obj.data.color_attributes:
                            #print("gather_asset_hook - col after", obj, ca.data_type)
                            pass
        #print("gather_asset_hook - Done")

    def gather_gltf_extensions_hook(self, gltf2_plan, export_settings):
        if self.properties.enabled:
            for i, image in enumerate(gltf2_plan.images):
                image.uri = os.path.basename(urllib.parse.unquote(image.uri))

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
        if self.properties.enabled and MSFSGizmo:
            #print("gather_scene_hook - properties enabled", MSFSGizmo)
            MSFSGizmo.export(gltf2_scene.nodes, blender_scene, export_settings)

    def gather_material_hook(self, gltf2_material, blender_material, export_settings):
        # blender 4.0 issue with detail textures added twice once correct and once as a regular basecolor texture
        # if it has a detail color texture then set basecolor to none
        print("gather_material_hook - Started with gltf2_material", gltf2_material, gltf2_material.pbr_metallic_roughness, gltf2_material.pbr_metallic_roughness.base_color_texture)
        print("gather_material_hook - blender material - delete base color before", blender_material, blender_material.msfs_detail_color_texture, blender_material.msfs_base_color_texture)
        if blender_material.msfs_detail_color_texture is not None and blender_material.msfs_base_color_texture is None:
            #blender_material.msfs_material_type == "msfs_windshield":
            gltf2_material.pbr_metallic_roughness.base_color_texture = None
            print("gather_material_hook - blender material - delete base color after", blender_material, blender_material.msfs_detail_color_texture, blender_material.msfs_base_color_texture)
        print("gather_material_hook - blender material - delete base color before", blender_material, blender_material.msfs_detail_color_texture, blender_material.msfs_base_color_texture)

        # blender 3.3 removes base color values with base color texture - have to add back in
        print("gather_material_hook - Started with gltf2_material", gltf2_material, gltf2_material.pbr_metallic_roughness, gltf2_material.pbr_metallic_roughness.base_color_texture, gltf2_material.pbr_metallic_roughness.base_color_factor)
        base_color = blender_material.msfs_base_color_factor
        gltf2_base_color = gltf2_material.pbr_metallic_roughness.base_color_factor
        print("gather_material_hook - blender material - set base color factor before", blender_material, blender_material.msfs_base_color_texture, base_color[0], base_color[1], base_color[2], base_color[3])
        if  not (base_color is None or gltf2_base_color is None):
            if not equality_check(base_color, gltf2_base_color, len(base_color), len(gltf2_base_color)):
                print("gather_material_hook - changing")
                gltf2_material.pbr_metallic_roughness.base_color_factor = [base_color[0],base_color[1],base_color[2],base_color[3]]
        print("gather_material_hook - blender material - set base color after", blender_material, blender_material.msfs_base_color_texture, blender_material.msfs_base_color_factor, gltf2_material.pbr_metallic_roughness.base_color_factor)


        if self.properties.enabled:
            print("gather_material_hook - export")
            MSFSMaterial.export(gltf2_material, blender_material, export_settings)
        print("gather_material_hook - Done")

    # def gather_texture_info_hook(self, gltf2_io, blender_shader_sockets, export_settings):
        # print("gather_texture_info_hook - Started with ", blender_shader_sockets)
        # print("exportsettings", export_settings)
        # print("gather_texture_info_hook - io", gltf2_io.extensions, gltf2_io.extras, gltf2_io.index, gltf2_io.tex_coord)
        # if self.properties.enabled:
            # pass
            # #MSFSMaterial.export(gltf2_material, blender_material, export_settings)
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
