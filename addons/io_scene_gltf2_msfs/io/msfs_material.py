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

import bpy
# added .material to next line for 3.6 file structure
if(bpy.app.version < (3, 4, 0)):
    from io_scene_gltf2.blender.exp.gltf2_blender_gather_texture_info import (
        gather_material_normal_texture_info_class,
        gather_material_occlusion_texture_info_class, gather_texture_info)
else:
    from io_scene_gltf2.blender.exp.material.gltf2_blender_gather_texture_info import (
        gather_material_normal_texture_info_class,
        gather_material_occlusion_texture_info_class, gather_texture_info)
from io_scene_gltf2.blender.imp.gltf2_blender_image import BlenderImage

from ..com import msfs_material_props as MSFSMaterialExtensions
import typing

#TODOSNode : @cached? If yes, need to use id of node tree, has this is probably not fully hashable
# For now, not caching it. If we encounter performance issue, we will see later
def get_material_nodes_msfs(node_tree: bpy.types.NodeTree, group_path, type, nodename):
    """
    For a given tree, recursively return all nodes including node groups.
    """

    print("get_material_nodes_msfs - start")
    nodes = []
    for node in [n for n in node_tree.nodes if isinstance(n, type) and not n.mute and n.name == nodename]:
        nodes.append((node, group_path.copy()))

    # # Some weird node groups with missing datablock can have no node_tree, so checking n.node_tree (See #1797)
    # for node in [n for n in node_tree.nodes if n.type == "GROUP" and n.node_tree is not None and not n.mute and n.node_tree.name != get_gltf_old_group_node_name()]: # Do not enter the olf glTF node group
        # new_group_path = group_path.copy()
        # new_group_path.append(node)
        # nodes.extend(get_material_nodes_msfs(node.node_tree, new_group_path, type))

    print("get_material_nodes_msfs - done")
    return nodes

class NodeSocket:
    def __init__(self, socket, group_path):
        self.socket = socket
        self.group_path = group_path

def get_node_socket_msfs(blender_material, type, name, nodename):
    """
    For a given material input name, retrieve the corresponding node tree socket for a given node type.

    :param blender_material: a blender material for which to get the socket
    :return: a blender NodeSocket for a given type
    """
    #print("get_node_socket_msfs - start")
    nodes = get_material_nodes_msfs(blender_material.node_tree, [blender_material], type, nodename)
    #TODOSNode : Why checking outputs[0] ? What about alpha for texture node, that is outputs[1] ????
    #nodes = [node for node in nodes if check_if_is_linked_to_active_output(node[0].outputs[0], node[1])]
    nodes = [node for node in nodes]
    inputs = sum([[(input, node[1]) for input in node[0].inputs if input.name == name] for node in nodes], [])
    #print("get_node_socket_msfs - done")
    if inputs:
        return NodeSocket(inputs[0][0], inputs[0][1])
    return NodeSocket(None, None)


def get_socket_msfs(blender_material: bpy.types.Material, name: str, nodename: str, volume=False):
    """
    For a given material input name, retrieve the corresponding node tree socket.

    :param blender_material: a blender material for which to get the socket
    :param name: the name of the socket
    :return: a blender NodeSocket
    """
    #print("get_socket_msfs - start")
    if blender_material.node_tree and blender_material.use_nodes:
        #i = [input for input in blender_material.node_tree.inputs]
        #o = [output for output in blender_material.node_tree.outputs]
        if name == "Emissive":
            # Check for a dedicated Emission node first, it must supersede the newer built-in one
            # because the newer one is always present in all Principled BSDF materials.
            emissive_socket = get_node_socket_msfs(blender_material, bpy.types.ShaderNodeEmission, "Color", nodename)
            if emissive_socket.socket is not None:
                return emissive_socket
            # If a dedicated Emission node was not found, fall back to the Principled BSDF Emission socket.
            name = "Emission Color"
            type = bpy.types.ShaderNodeBsdfPrincipled
        elif name == "Background":
            type = bpy.types.ShaderNodeBackground
            name = "Color"
        else:
            if volume is False:
                type = bpy.types.ShaderNodeBsdfPrincipled
            else:
                type = bpy.types.ShaderNodeVolumeAbsorption

        return get_node_socket_msfs(blender_material, type, name, nodename)

    #print("get_socket_msfs - done")
    return NodeSocket(None, None)


class MSFSMaterial:
    bl_options = {"UNDO"}

    extensions = [
        MSFSMaterialExtensions.AsoboMaterialCommon,
        MSFSMaterialExtensions.AsoboMaterialGeometryDecal,
        MSFSMaterialExtensions.AsoboMaterialGhostEffect,
        MSFSMaterialExtensions.AsoboMaterialDrawOrder,
        MSFSMaterialExtensions.AsoboDayNightCycle,
        MSFSMaterialExtensions.AsoboDisableMotionBlur,
        MSFSMaterialExtensions.AsoboPearlescent,
        MSFSMaterialExtensions.AsoboAlphaModeDither,
        MSFSMaterialExtensions.AsoboMaterialInvisible,
        MSFSMaterialExtensions.AsoboMaterialEnvironmentOccluder,
        MSFSMaterialExtensions.AsoboMaterialUVOptions,
        MSFSMaterialExtensions.AsoboMaterialShadowOptions,
        MSFSMaterialExtensions.AsoboMaterialResponsiveAAOptions,
        MSFSMaterialExtensions.AsoboMaterialDetail,
        MSFSMaterialExtensions.AsoboMaterialFakeTerrain,
        MSFSMaterialExtensions.AsoboMaterialFresnelFade,
        MSFSMaterialExtensions.AsoboSSS,
        MSFSMaterialExtensions.AsoboAnisotropic,
        MSFSMaterialExtensions.AsoboWindshield,
        MSFSMaterialExtensions.AsoboClearCoat,
        MSFSMaterialExtensions.AsoboParallaxWindow,
        MSFSMaterialExtensions.AsoboGlass,
        MSFSMaterialExtensions.AsoboTags,
        MSFSMaterialExtensions.AsoboMaterialCode
    ]

    def __new__(cls, *args, **kwargs):
        raise RuntimeError("%s should not be instantiated" % cls)

    @staticmethod
    def create_image(index, import_settings):
        pytexture = import_settings.data.textures[index]
        BlenderImage.create(import_settings, pytexture.source)
        pyimg = import_settings.data.images[pytexture.source]

        # Find image created
        blender_image_name = pyimg.blender_image_name
        if blender_image_name:
            return bpy.data.images[blender_image_name]

    @staticmethod
    def export_image(
        blender_material, blender_image, type, export_settings, normal_scale=None
    ):
        nodes = blender_material.node_tree.nodes
        links = blender_material.node_tree.links
        
        # should all be in a try finally to remove Fake nodes
        # Fake Fake Fake Fake Fake Fake Fake Fake Fake Fake 

        # Create a fake texture node temporarily (unfortunately this is the only solid way of doing this)
        texture_node = nodes.new("ShaderNodeTexImage")
        texture_node.name = "FakeTextureNode"
        texture_node.image = blender_image

        # Create shader to plug texture into
        shader_node = nodes.new("ShaderNodeBsdfPrincipled")
        shader_node.name = "FakeBSDFNode"
        print("MSFSMaterial - export_image type", type)


        # Gather texture info
        if type == "DEFAULT":
            link = links.new(shader_node.inputs["Base Color"], texture_node.outputs[0])
            # from Khronos gltf core example pbr sockets geather_texture_info

            print("MSFSMaterial - export_image DEFAULT if", link)
            base_color_socket = get_socket_msfs(blender_material, "Base Color", "FakeBSDFNode")
            #alpha_socket = get_socket_msfs(blender_material, "Alpha", "FakeBSDFNode")

            # keep sockets that have some texture : color and/or alpha
            print("MSFSMaterial - socket", base_color_socket)
            inputs = tuple(
                socket for socket in [base_color_socket]
            )
            print("MSFSMaterial - inputs", inputs)

            # had to add in a default socket argument for compatability with 4.0  added (),
            # had to remove the default socket argument for compatability with 4.1+  removed (),
            print("MSFSMaterial - export_image DEFAULT if - sockets", inputs[0], inputs)
            for inp in inputs:
                print("inputs",inp)
            texture_info = gather_texture_info(
                inputs[0],
                inputs,
                export_settings
            )
            print("MSFSMaterial - export_image DEFAULT if - return", texture_info)
        elif type == "NORMAL":
            print("MSFSMaterial - export_image NORMAL if")

            normal_node = nodes.new("ShaderNodeNormalMap")
            if normal_scale:
                normal_node.inputs["Strength"].default_value = normal_scale
            link = links.new(normal_node.inputs["Color"], texture_node.outputs[0])
            normal_blend_link = links.new(
                shader_node.inputs["Normal"], normal_node.outputs[0]
            )

           # from Khronos gltf core example pbr sockets geather_texture_info
            normal_socket = get_socket_msfs(blender_material, "Normal", "FakeBSDFNode")

            # keep sockets that have some texture : color and/or alpha
            print("MSFSMaterial - normal socket", normal_socket)
            inputs = tuple(
                socket for socket in [normal_socket]
            )
            print("MSFSMaterial - inputs Normal", inputs)
            texture_info = gather_material_normal_texture_info_class(
                inputs[0],
                inputs,
                export_settings
            )

            links.remove(normal_blend_link)
            print("MSFSMaterial - export_image NORMAL if - return", texture_info)
        elif type == "OCCLUSION":
            print("MSFSMaterial - export_image OCCLUSION if")
            # TODO: handle this - may not be needed
            # from Khronos gltf core example pbr sockets geather_texture_info



            # # Check for the presence of Occlusion, Roughness, Metallic sharing a single image.
            # # If not fully shared, return None, so the images will be cached and processed separately.

            # occlusion = get_socket(blender_material, "Occlusion")
            # if occlusion.socket is None or not has_image_node_from_socket(occlusion, export_settings):
                # occlusion = get_socket_from_gltf_material_node(blender_material, "Occlusion")
                # if occlusion.socket is None or not has_image_node_from_socket(occlusion, export_settings):
                    # return None

            # metallic_socket = get_socket(blender_material, "Metallic")
            # roughness_socket = get_socket(blender_material, "Roughness")

            # hasMetal = metallic_socket.socket is not None and has_image_node_from_socket(metallic_socket, export_settings)
            # hasRough = roughness_socket.socket is not None and has_image_node_from_socket(roughness_socket, export_settings)

            # # Warning: for default socket, do not use NodeSocket object, because it will break cache
            # # Using directlty the Blender socket object
            # if not hasMetal and not hasRough:
                # metallic_roughness = get_socket_from_gltf_material_node(blender_material, "MetallicRoughness")
                # if metallic_roughness.socket is None or not has_image_node_from_socket(metallic_roughness, export_settings):
                    # return None
                # result = (occlusion, metallic_roughness)
            # elif not hasMetal:
                # result = (occlusion, roughness_socket)
            # elif not hasRough:
                # result = (occlusion, metallic_socket)
            # else:
                # result = (occlusion, roughness_socket, metallic_socket)

            # if not gltf2_blender_gather_texture_info.check_same_size_images(result, export_settings):
                # print_console("INFO",
                    # "Occlusion and metal-roughness texture will be exported separately "
                    # "(use same-sized images if you want them combined)")
                # return None

            # # # Double-check this will past the filter in texture_info
            # # info, _, _, _ = gltf2_blender_gather_texture_info.gather_texture_info(result[0], result, export_settings)
            # # if info is None:
                # # return None

            # # return result



            occlusionr_socket = get_socket_msfs(blender_material, "Occlusion", "FakeBSDFNode")

            # keep sockets that have some texture : color and/or alpha
            print("MSFSMaterial - socket", occlusion_socket)
            inputs = tuple(
                socket for socket in [occlusion_socket]
            )
            print("MSFSMaterial - inputs OMR", inputs)

            texture_info = gather_material_occlusion_texture_info_class(
                inputs[0],
                inputs,
                export_settings
            )

        # Delete temp Fake nodes
        links.remove(link)
        nodes.remove(shader_node)
        nodes.remove(texture_node)
        if type == "NORMAL":
            nodes.remove(normal_node)

        # Some versions of the Khronos exporter have gather_texture_info return a tuple
        if isinstance(texture_info, tuple):
            texture_info = texture_info[0]

        return texture_info

    @staticmethod
    def create(gltf2_material, blender_material, import_settings):
        for extension in MSFSMaterial.extensions:
            extension.from_dict(blender_material, gltf2_material, import_settings)

    @staticmethod
    def export(gltf2_material, blender_material, export_settings):
        for extension in MSFSMaterial.extensions:
            extension.to_extension(blender_material, gltf2_material, export_settings)
