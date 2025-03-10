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

from .msfs_material_prop_update import MSFS_Material_Property_Update
from .msfs_material_function import MSFS_Material

from .material.utils.msfs_material_enum import (MSFS_MixNodeInputs,
                                                MSFS_MixNodeOutputs,
                                                MSFS_BSDFNodeInputs,
                                                MSFS_ShaderNodes)
from bpy.types import Material
from .. import get_prefs

def equality_check(arr1, arr2, size1, size2):
    if (size1 != size2):
        return False
    for i in range(0, size2):
        # blender python color channel issues in floats ???
        if (int(arr1[i] * 10000000)/10000000 != int(arr2[i] * 10000000)/10000000):
            return False
    return True

def Is_it_FBW_Material(mat):
    # ToDo: FBW msfs_material_type mapping
    Is_FBW_material = False
    n1_IsThere = False
    n2_IsThere = False
    try:
        for n in mat.node_tree.nodes:
            #print("get_material_types - Nodes", n, n.name, n.label)
            if n.label == "METALLIC ROUGHNESS":
                n1_IsThere = True
            if n.label == "OCCLUSION":
                n2_IsThere = True
        if n1_IsThere and n1_IsThere:
            Is_FBW_material = True
    except:
        print("*** MSFS Warning *** FBW Material error")
    # need other ways to check if FBW for glass
    return Is_FBW_material

def set_vertex_color_white(mat, obj):
    # now adding a base color triggers vertex color links - they make object black in blender - show texture by making mesh color attribute white
    # add color attribute to all meshes in material
    #if mat.msfs_base_color_texture or mat.msfs_detail_color_texture:
    if obj.type == 'MESH':
        for mat_slot in obj.material_slots:
            if mat_slot.material.name == mat.name:
                #print("update_base_color_texture - found mesh object with material base color texture", obj, mat.name, mat.msfs_base_color_texture, mat.msfs_detail_color_texture)
                for ca in obj.data.color_attributes:
                    if len(obj.data.color_attributes) > 0:
                        return
                # None found - make new Vertex_Color_white and assing to mesh
                # Create a new color attribute - seems to be white already ????
                color_attribute = obj.data.color_attributes.new(
                                      name='Col',
                                      #type='BYTE_COLOR',
                                      type='FLOAT_COLOR',
                                      domain='CORNER',
                                  )


# def reset_base_color_links(mat, obj):
        # # Ensure the mesh has a vertex_color_white attribute if it has a base color texture - detail color texture
        # if (mat and obj.type == "MESH"):
            # for n in mat.node_tree.nodes:
                # # possible check is base color is not (1,1,1) don't check alpha
                # if n.label == MSFS_ShaderNodes.baseColorRGB.value:
                    # #print("mat, obj", mat, obj)
                    # color = n.outputs[0].default_value
                    # #print("color", color, color[0], color[1], color[2])
                    # if (color[0] != 1 or color[1] != 1 or color[2] != 1):
                        # if MSFS_OT_vertex_color_white_Data.vertex_color_attribute_isfound(obj):
                            # nodes = mat.node_tree.nodes
                            # links = mat.node_tree.links
                            # for n in nodes:
                                # #print("node",n, n.label)
                                # if (n.label == MSFS_ShaderNodes.vertexBaseColorMul.value):
                                    # basecolorsocket = n.outputs[0]
                                    # print("socket",basecolorsocket,n, n.label)
                                    # if not(basecolorsocket.is_linked):
                                        # print("BasecolorMul link is to be reset")
                                        # mat.updateColorLinks()


class MSFS_OT_vertex_color_white_Data(bpy.types.Operator):
    """This addon changes some of the internal property names. vertex_color_white will be applied to mesh."""

    bl_idname = "msfs.vertex_color_white_attribute"
    bl_label = "Apply Vertex_Color_White attribute"


    @staticmethod
    def vertex_color_white_attribute_is_required(mat, obj):
        # Ensure the mesh has a vertex_color_white attribute if it has a base color texture - detail color texture
        if (mat and obj.type == "MESH"):
            try:
                for n in mat.node_tree.nodes:
                    if n.label == MSFS_ShaderNodes.baseColorTex.value and n.image:
                        if not MSFS_OT_vertex_color_white_Data.vertex_color_attribute_isfound(obj):
                            #print("vertex_color_white_attribute_is_required - required Tex")
                            return True
                    if n.label == MSFS_ShaderNodes.detailColorTex.value and n.image:
                        if not MSFS_OT_vertex_color_white_Data.vertex_color_attribute_isfound(obj):
                            #print("vertex_color_white_attribute_is_required - required Det Tex")
                            return True
                    if n.label == MSFS_ShaderNodes.baseColorRGB.value:
                        #print("mat, obj", mat, obj)
                        #color = n.outputs[0].default_value
                        #print("color", color, color[0], color[1], color[2])
                        #if (color[0] != 1 or color[1] != 1 or color[2] != 1):
                        if not MSFS_OT_vertex_color_white_Data.vertex_color_attribute_isfound(obj):
                            #print("vertex_color_white_attribute_is_required - required base")
                            # for this need to reset the links Base Color to BSDF to base color to Vertex Base Color Mul
                            # reset the links
                            return True
            except:
                print("*** MSFS Warning *** vertex color white attribute error")
        return False


    # @staticmethod
    # def basecolor_link_is_required(mat, obj):
        # # Ensure the mesh has a vertex_color_white attribute if it has a base color texture - detail color texture
        # if (mat and obj.type == "MESH"):
            # for n in mat.node_tree.nodes:
                # # possible check is base color is not (1,1,1) don't check alpha
                # if n.label == MSFS_ShaderNodes.baseColorRGB.value:
                    # #print("mat, obj", mat, obj)
                    # color = n.outputs[0].default_value
                    # #print("color", color, color[0], color[1], color[2])
                    # if (color[0] != 1 or color[1] != 1 or color[2] != 1):
                        # if MSFS_OT_vertex_color_white_Data.vertex_color_attribute_isfound(obj):
                            # nodes = mat.node_tree.nodes
                            # links = mat.node_tree.links
                            # for n in nodes:
                                # #print("node",n, n.label)
                                # if (n.label == MSFS_ShaderNodes.vertexBaseColorMul.value):
                                    # basecolorsocket = n.outputs[0]
                                    # if not(basecolorsocket.is_linked):
                                        # #print("No BasecolorMul link!")
                                        # return True
        # return False


    @staticmethod
    def vertex_color_attribute_isfound(obj):
        for ca in obj.data.color_attributes:
            if len(obj.data.color_attributes) > 0:
                return True
        return False

# could be an issue with vertex color - application - but bad for aircraft.
    def execute(self, context):
        # Ensure the mesh has vertex_color_white attribute
        mat = context.active_object.active_material
        obj = context.active_object
        try:
            for n in mat.node_tree.nodes:
                if n.label == MSFS_ShaderNodes.baseColorTex.value and n.image:
                    if not self.vertex_color_attribute_isfound(obj):
                        set_vertex_color_white(mat, obj)
                if n.label == MSFS_ShaderNodes.detailColorTex.value and n.image:
                    if not self.vertex_color_attribute_isfound(obj):
                        set_vertex_color_white(mat, obj)
                if n.label == MSFS_ShaderNodes.baseColorRGB.value:
                    #print("mat, obj", mat, obj)
                    #color = n.outputs[0].default_value
                    #print("color", color, color[0], color[1], color[2])
                    #if (color[0] != 1 or color[1] != 1 or color[2] != 1):
                    if not self.vertex_color_attribute_isfound(obj):
                        # for this need to reset the links Base Color to BSDF to base color to Vertex Base Color Mul
                        # reset the links
                        #print("set vertex color white")
                        set_vertex_color_white(mat, obj)
                        #reset_base_color_links(mat, obj)
        except:
            print("*** MSFS Warning *** vertex color white attribute error")
        return {"FINISHED"}


class MSFS_OT_glTfSettingsMaterialData(bpy.types.Operator):
    """This addon changes some of the internal property names. glTf Settings will be updated for ALL materials."""

    bl_idname = "msfs.gltfsetttings_material_data"
    bl_label = "Reset glTf Settings Material Data"


    @staticmethod
    def gltf_settings_with_dot_present():
        # Ensure the material has a shader node tree
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    # Check if the node is a group node with a name "glTF Settings new"
                    if node.type == 'GROUP' and node.node_tree and ( 'glTF Settings.' in node.node_tree.name)  :
                        return True
        return False

    def execute(self, context):
        # Ensure the material has a shader node tree
        for material in bpy.data.materials:
            if material.use_nodes:
                for node in material.node_tree.nodes:
                    # Check if the node is a group node with a name "glTF Settings new"
                    if node.type == 'GROUP' and node.node_tree and ( 'glTF Settings.' in node.node_tree.name)  :
                        # Reassign the proper node group
                        proper_occlusion_node_tree = bpy.data.node_groups.get("glTF Settings")
                        node.node_tree = proper_occlusion_node_tree
                        print(f"Reassigned 'glTF Settings.xxx' to 'glTF Settings' in material  '{material.name}'",  node.node_tree.name)
        return {"FINISHED"}


class MSFS_OT_MigrateColorFixData(bpy.types.Operator): # TODO: Remove eventually
    """This addon changes the color nodes, metallic, roughness values to the BSDF color if there is no link input"""

    bl_idname = "msfs.migrate_colorfix_data"
    bl_label = "Pre-Migrate Legacy Data"


    @staticmethod
    def old_material_values_diff(mat):
        #print("Called")
        index1 = 1
        index_B4 = 1 # index for Blender v4
        if(bpy.app.version < (3, 4, 0)):
            index1 = 0
        if(bpy.app.version < (4, 0, 0)):
            index_B4 = 0

        outputs0 = MSFS_MixNodeOutputs.outputs[index1][0]
        inputs0 = MSFS_MixNodeInputs.inputs[index1][0]
        inputs1 = MSFS_MixNodeInputs.inputs[index1][1]
        inputs2 = MSFS_MixNodeInputs.inputs[index1][2]
        bsdfinputs6 = MSFS_BSDFNodeInputs.inputs[index_B4][0]
        bsdfinputs9 = MSFS_BSDFNodeInputs.inputs[index_B4][1]
        bsdfinputs20 = MSFS_BSDFNodeInputs.inputs[index_B4][2]
        bsdfinputs21 = MSFS_BSDFNodeInputs.inputs[index_B4][3]
        bsdfinputs19 = MSFS_BSDFNodeInputs.inputs[index_B4][4]

        # To Do: check if new material type and Base Color and Base Color A nodes present then just assume good
        try:
            if mat.msfs_material_type != "NONE" and mat.node_tree.nodes["Base Color RGB"] is not None and mat.node_tree.nodes["Base Color A"] is not None:
                return False
        except:
            pass
        finally:
            pass

        found_diff = False
        found_diff = Is_it_FBW_Material(mat) and mat.msfs_material_mode == "NONE"
        #print("old_albedo_tint_color_diff - diff", found_diff)
        # there could be a chance that there are msfs values and BSDF non default values
        try:
            nodes = mat.node_tree.nodes
            bsdfnodes = [n for n in nodes 
                    if isinstance(n, bpy.types.ShaderNodeBsdfPrincipled)]
            temp_alpha = 1.0
            if mat.msfs_material_mode == "NONE" and mat.msfs_material_type == "NONE":
                base_color_default = [0.8,0.8,0.8,1.0]
                try:
                    for principled in bsdfnodes:
                        if not principled.inputs[0].links:
                            # check base color not default
                            # get BSDF base Color value
                            BSDF_Base_Color = principled.inputs[0].default_value
                            #print(BSDF_Base_Color[0], base_color_default[0], BSDF_Base_Color[1], base_color_default[1], BSDF_Base_Color[2], base_color_default[2], BSDF_Base_Color[3], base_color_default[3])
                            if not equality_check(BSDF_Base_Color, base_color_default, len(BSDF_Base_Color), len(base_color_default)):
                                found_diff = True
                        if found_diff:
                            return found_diff
                except:
                    print("*** MSFS Warning *** vertex color white attribute error")

                return found_diff
        except:
            print("*** MSFS Warning *** old material values error")

        # some devs potentially set the material, but destroy the nodes - and the system thinks that a proper MSFS material is there
        # check to see if a common node is there (albedo_tint or Base color). - if none there, then check BSDF values
        bad_material_setup = True
        #print("old_albedo_tint_color_diff - START check nodes - type, mode", mat, mat.msfs_material_type, mat.msfs_material_mode)
        try:
            if mat.msfs_material_mode != "NONE" and mat.node_tree.nodes["albedo_tint"] is not None:
                bad_material_setup = False
                #print("checked mode")
        except:
            pass
        finally:
            try:
                if mat.msfs_material_type != "NONE" and mat.node_tree.nodes["Base Color RGB"] is not None:
                    bad_material_setup = False
                    #print("checked type")
            except:
                pass
            finally:
                pass
        if bad_material_setup and mat.msfs_material_mode != "NONE":
            bad_material_setup = False

        #print("old_albedo_tint_color_diff - nodes checked and check if is bad", mat, mat.msfs_material_type, mat.msfs_material_mode, bad_material_setup )
        if ((bad_material_setup and mat.msfs_material_type != "NONE") or (mat.msfs_material_mode == "NONE" and mat.msfs_material_type != "NONE") or (not bad_material_setup and mat.msfs_material_mode != "NONE")
                    or (bad_material_setup and mat.msfs_material_type == "NONE" and mat.msfs_material_mode == "NONE")):
            #print("old_albedo_tint_color_diff - looking mat, type, mode, and is bad", mat, mat.msfs_material_type, mat.msfs_material_mode, bad_material_setup)
            try:
                for principled in bsdfnodes:
                    if not principled.inputs[0].links:
                        # now get albedo_tint node and check color same as Base Color on BSDF
                        # get albedo_tint node
                        #print("old_albedo_tint_color_diff - mat", mat, found_diff)
                        try:
                            if mat.node_tree.nodes["albedo_tint"] is not None:
                                # get alpha for later input 21 alpha check
                                temp_alpha = mat.node_tree.nodes["albedo_tint"].outputs[0].default_value[3]
                                # get color
                                albedo_tint_checkval = mat.node_tree.nodes["albedo_tint"].outputs[0].default_value
                                #print("old_albedo_tint_color_diff - albedo tint color", albedo_tint_checkval, temp_alpha)
                                # get BSDF base Color value
                                BSDF_Base_Color = principled.inputs["Base Color"].default_value
                                #print("old_albedo_tint_color_diff - diff BSDF to albedo tint color", found_diff, BSDF_Base_Color[0], albedo_tint_checkval[0], BSDF_Base_Color[1], albedo_tint_checkval[1], BSDF_Base_Color[2], albedo_tint_checkval[2], BSDF_Base_Color[3], albedo_tint_checkval[3])
                                if not equality_check(BSDF_Base_Color, albedo_tint_checkval, len(BSDF_Base_Color), len(albedo_tint_checkval)):
                                    found_diff = True
                                #print("old_albedo_tint_color_diff - diff now alphas", found_diff, principled.inputs[bsdfinputs21].default_value, temp_alpha, mat.node_tree.nodes["albedo_tint"].outputs[0].default_value[3])
                                # check the alphas - if an input to alpha then use node alpha - if no inputs use BSDF alpha - won't get here if no albedo_tint
                                if not principled.inputs[0].links and not principled.inputs[bsdfinputs21].links and principled.inputs[bsdfinputs21].default_value != temp_alpha:
                                    found_diff = True
                                #print("old_albedo_tint_color_diff - alpha diff", found_diff)
                                if found_diff:
                                    return found_diff
                            else:
                                if mat.msfs_material_type != "NONE":
                                    #print("old_albedo_tint_color_diff - Base Color")
                                    BSDF_Base_Color = principled.inputs["Base Color"].default_value
                                    #print("old_albedo_tint_color_diff - BSDF to MSFS base color", BSDF_Base_Color[0], mat.msfs_base_color_factor[0], BSDF_Base_Color[1], mat.msfs_base_color_factor[1], BSDF_Base_Color[2], mat.msfs_base_color_factor[2], BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                                    # determine alpha
                                    temp_alpha = BSDF_Base_Color[3]
                                    if not equality_check(BSDF_Base_Color, mat.msfs_base_color_factor, len(BSDF_Base_Color), len(mat.msfs_base_color_factor)):
                                        found_diff = True
                                    # make Base Color alpha value BSDF - there is no albedo_tint here
                                    if not principled.inputs[0].links and not principled.inputs[bsdfinputs21].links and principled.inputs[bsdfinputs21].default_value != temp_alpha:
                                        found_diff = True
                                    #print("old_albedo_tint_color_diff - Base Color Alpha Done")
                                    if found_diff:
                                        return found_diff
                                
                        except:
                            try:
                                if mat.msfs_material_type != "NONE":
                                    temp_alpha = BSDF_Base_Color[3]
                                    #print("old_albedo_tint_color_diff - BSDF to MSFS base color", BSDF_Base_Color[0], mat.msfs_base_color_factor[0], BSDF_Base_Color[1], mat.msfs_base_color_factor[1], BSDF_Base_Color[2], mat.msfs_base_color_factor[2], BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                                    BSDF_Base_Color = principled.inputs["Base Color"].default_value
                                    if not equality_check(BSDF_Base_Color, mat.msfs_base_color_factor, len(BSDF_Base_Color), len(mat.msfs_base_color_factor)):
                                        found_diff = True
                                    if not principled.inputs[0].links and not principled.inputs[bsdfinputs21].links and principled.inputs[bsdfinputs21].default_value != temp_alpha:
                                        found_diff = True
                                    #print("old_albedo_tint_color_diff - alpha diff", found_diff)
                                    if found_diff:
                                        return found_diff
                            except:
                                pass

                        finally:
                            pass

                        # put Emissive color stuff here

                        try:
                            if mat.node_tree.nodes["emissive_tint"] is not None:
                                # get color
                                BSDF_Emission = principled.inputs[bsdfinputs19].default_value[0:3]
                                emissive_tint_checkval = mat.node_tree.nodes["emissive_tint"].outputs[0].default_value
                                print("old_emissive_tint_color_diff - BSDF emission", BSDF_Emission[0], emissive_tint_checkval[0], BSDF_Emission[1], emissive_tint_checkval[1], BSDF_Emission[2], emissive_tint_checkval[2], BSDF_Emission[3], emissive_tint_checkval[3])
                                if not equality_check(BSDF_Emission, emissive_tint_checkval, len(BSDF_Emission), len(emissive_tint_checkval)):
                                    found_diff = True
                                print("old_emissive_tint_color_diff - alpha diff", found_diff)
                                #    found_diff = True
                                if found_diff:
                                    return found_diff
                            else:
                                if mat.msfs_material_type != "NONE":
                                    print("old_emissive_tint_color_diff - Emission")
                                    BSDF_Emission = principled.inputs[bsdfinputs19].default_value[0:3]
                                    print("old_emissive_tint_color_diff - BSDF to MSFS base color", BSDF_Emission[0], mat.msfs_emissive_factor[0], BSDF_Emission[1], mat.msfs_emissive_factor[1], BSDF_Emission[2], mat.msfs_emissive_factor[2], BSDF_Emission[3], mat.msfs_emissive_factor[3])
                                    if not equality_check(BSDF_Emission, mat.msfs_emissive_factor, len(BSDF_Emission), len(mat.msfs_emissive_factor)):
                                        found_diff = True
                                    print("old_emissive_tint_color_diff - Base Color Alpha Done")
                                    if found_diff:
                                        return found_diff
                        except:
                            try:
                                if mat.msfs_material_type != "NONE":
                                    print("old_emissive_tint_color_diff - BSDF to MSFS emissive", BSDF_Emission[0], mat.msfs_emissive_factor[0], BSDF_Emission[1], mat.msfs_emissive_factor[1], BSDF_Emission[2], mat.msfs_emissive_factor[2], BSDF_Emission[3], mat.msfs_emissive_factor[3])
                                    BSDF_Emission = principled.inputs[bsdfinputs19].default_value[0:3]
                                    if not equality_check(BSDF_Emission, mat.msfs_emissive_factor, len(BSDF_Emission), len(mat.msfs_emissive_factor)):
                                        found_diff = True
                                    if found_diff:
                                        return found_diff
                            except:
                                if principled.name != MSFS_ShaderNodes.principledBSDFFake:
                                    print("old_emissive_tint_color_diff - old_properties - Error - BSDF properties found skipping", found_diff. principled.name, MSFS_ShaderNodes.principledBSDFFake)

                        finally:
                            pass

                    print("old_albedo_tint_color_diff - after node - diff", found_diff, bad_material_setup)
                    if mat.msfs_material_type == "NONE" or bad_material_setup or (mat.msfs_material_mode != "NONE" and not bad_material_setup):
                        print("old_albedo_tint_color_diff - values", principled.inputs[bsdfinputs6].default_value, principled.inputs[bsdfinputs9].default_value, principled.inputs[bsdfinputs20].default_value, principled.inputs[bsdfinputs21].default_value)
                        # input 6 Metallic
                        if not principled.inputs[bsdfinputs6].links and principled.inputs[bsdfinputs6].default_value != mat.msfs_metallic_factor:
                            found_diff = True
                        print("after met", found_diff, mat.msfs_metallic_factor, principled.inputs[bsdfinputs6].default_value)
                        # input 9 Roughness
                        if not principled.inputs[bsdfinputs9].links and principled.inputs[bsdfinputs9].default_value != mat.msfs_roughness_factor:
                            found_diff = True
                        print("after rough", found_diff)
                        # input 20 Emissive Strength/Scale
                        if not principled.inputs[bsdfinputs20].links and principled.inputs[bsdfinputs20].default_value != mat.msfs_emissive_scale and principled.inputs[bsdfinputs20].default_value > 0.0:
                            found_diff = True
                        print("after emissive - diff", found_diff, principled.inputs[bsdfinputs6].default_value, principled.inputs[bsdfinputs9].default_value, principled.inputs[bsdfinputs20].default_value, principled.inputs[bsdfinputs21].default_value)
            except:
                print("*** MSFS Warning *** old material values error")

        #print("on return - diff", found_diff)
        return found_diff


    def execute(self, context):
        index1 = 1
        index_B4 = 1 # index for Blender v4
        if(bpy.app.version < (3, 4, 0)):
            index1 = 0
        if(bpy.app.version < (4, 0, 0)):
            index_B4 = 0

        outputs0 = MSFS_MixNodeOutputs.outputs[index1][0]
        inputs0 = MSFS_MixNodeInputs.inputs[index1][0]
        inputs1 = MSFS_MixNodeInputs.inputs[index1][1]
        inputs2 = MSFS_MixNodeInputs.inputs[index1][2]
        bsdfinputs6 = MSFS_BSDFNodeInputs.inputs[index_B4][0]
        bsdfinputs9 = MSFS_BSDFNodeInputs.inputs[index_B4][1]
        bsdfinputs20 = MSFS_BSDFNodeInputs.inputs[index_B4][2]
        bsdfinputs21 = MSFS_BSDFNodeInputs.inputs[index_B4][3]
        bsdfinputs19 = MSFS_BSDFNodeInputs.inputs[index_B4][4]

        mat = context.active_object.active_material
        if Is_it_FBW_Material(mat):
            #mat.msfs_material_mode = mat.msfs_material_type
            print("msfs_material_mode - type", mat.get("msfs_material_mode"), mat.get("msfs_material_type"))
            old_material_older = [  # Assuming the user uninstalled the old plugin, the index of the value will be stored instead of the name of the current material. Replicate the order here
                "NONE",
                "msfs_standard",
                "msfs_decal",
                "msfs_windshield",
                "msfs_porthole",
                "msfs_glass",  
                "msfs_geo_decal",
                "msfs_clearcoat",  
                "msfs_parallax",
                "msfs_anisotropic",  
                "msfs_hair",
                "msfs_sss",
                "msfs_invisible",
                "msfs_fake_terrain",  
                "msfs_fresnel",
                "msfs_env_occluder",
            ]
            mat.msfs_material_fbw = old_material_older[mat["msfs_material_type"]]
            mat.msfs_material_mode = old_material_older[mat["msfs_material_type"]]


        nodes = mat.node_tree.nodes
        bsdfnodes = [n for n in nodes 
                if isinstance(n, bpy.types.ShaderNodeBsdfPrincipled)]
        temp_alpha = 1.0
        for principled in bsdfnodes:
            print("old_albedo_tint_color_diff - execute - principled", principled)
            #if not principled.inputs[0].links:
            # now get albedo_tint node and check color same as Base Color on BSDF
            # get albedo_tint node
            try:
                print("old_albedo_tint_color_diff - execute - TRY")
                if mat.node_tree.nodes["albedo_tint"] is not None:
                    print("old_albedo_tint_color_diff - execute - albedo_tint")
                    # get alpha for later input 21 alpha check
                    temp_alpha = mat.node_tree.nodes["albedo_tint"].outputs[0].default_value[3]
                    # get color
                    albedo_tint_checkval = mat.node_tree.nodes["albedo_tint"].outputs[0].default_value
                    # get BSDF base Color value
                    BSDF_Base_Color = principled.inputs["Base Color"].default_value
                    print("old_albedo_tint_color_diff - execute - BSDF color", BSDF_Base_Color)
                    if not equality_check(BSDF_Base_Color, albedo_tint_checkval, len(BSDF_Base_Color), len(albedo_tint_checkval)):
                        mat.node_tree.nodes["albedo_tint"].outputs[0].default_value = BSDF_Base_Color
                        mat.msfs_base_color_factor = BSDF_Base_Color
                    # input 21 Alpha
                    # check the alphas - if an input to alpha then use node alpha - if no inputs use BSDF alpha - won't get here if no albedo_tint
                    if not principled.inputs[0].links and not principled.inputs[bsdfinputs21].links and principled.inputs[bsdfinputs21].default_value != temp_alpha:
                        print("old_albedo_tint_color_diff - execute - Alpha", mat.node_tree.nodes["albedo_tint"].outputs[0].default_value[3], principled.inputs[bsdfinputs21].default_value)
                        # make alpha value from BSDF input(bsdfinputs21)
                        mat.node_tree.nodes["albedo_tint"].outputs[0].default_value[3] = principled.inputs[bsdfinputs21].default_value
                        principled.inputs["Base Color"].default_value[3] = principled.inputs[bsdfinputs21].default_value
                        print("old_albedo_tint_color_diff - execute - Alpha out", mat.node_tree.nodes["albedo_tint"].outputs[0].default_value[3], principled.inputs[bsdfinputs21].default_value)
                        mat.msfs_color_alpha_mix = principled.inputs[bsdfinputs21].default_value
                    elif principled.inputs[bsdfinputs21].links:
                        # another alpha from somewhere - Alpha Factor
                        print("old_albedo_tint_color_diff - execute - Alpha other", mat.node_tree.nodes["Alpha Factor"].outputs[0].default_value)
                        mat.msfs_color_alpha_mix = mat.node_tree.nodes["Alpha Factor"].outputs[0].default_value
            except:
                print("old_albedo_tint_color_diff - execute - Error - TRY - albedo_tint skipping")
                try:
                    if mat.msfs_material_type != "NONE":
                        print("old_albedo_tint_color_diff - execute - Base Color")
                        BSDF_Base_Color = principled.inputs["Base Color"].default_value
                        ###print("old_albedo_tint_color_diff - execute - BSDF to MSFS base color", BSDF_Base_Color[0], mat.msfs_base_color_factor[0], BSDF_Base_Color[1], mat.msfs_base_color_factor[1], BSDF_Base_Color[2], mat.msfs_base_color_factor[2], BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                        # set default in case not there.
                        #try:
                        print("old_albedo_tint_color_diff - execute - msfs_base_color_factor")
                        if not mat.msfs_base_color_factor:
                            mat.msfs_base_color_factor = mat.msfs_base_color_factor.default
                        # determine alpha
                        temp_alpha = BSDF_Base_Color[3]
                        if not equality_check(BSDF_Base_Color, mat.msfs_base_color_factor, len(BSDF_Base_Color), len(mat.msfs_base_color_factor)):
                            print("1")
                            mat.msfs_base_color_factor = BSDF_Base_Color
                            print("2")
                        # make Base Color alpha value BSDF - there is no albedo_tint here
                        if not principled.inputs[0].links and not principled.inputs[bsdfinputs21].links and principled.inputs[bsdfinputs21].default_value != temp_alpha:
                            print("3")
                            principled.inputs["Base Color"].default_value[3] = principled.inputs[bsdfinputs21].default_value
                            mat.msfs_base_color_factor[3] = principled.inputs[bsdfinputs21].default_value
                            #mat.msfs_color_alpha_mix = principled.inputs[bsdfinputs21].default_value
                            print("4")
                        else:
                            print("old_albedo_tint_color_diff - execute - Found Alpha Factor")
                            link = principled.inputs[bsdfinputs21].links[0]
                            print("4.5")
                            mat.msfs_base_color_factor[3] = link.from_node.inputs[1].default_value
                            
                        print("old_albedo_tint_color_diff - execute - Base Color Alpha Done")
                    elif mat.msfs_material_type == "NONE" and mat.msfs_material_mode == "NONE":
                        # SPECIAL now if you have had msfs properties values - assume msfs_standard - make a wild guess because there was data here from before.
                        try:
                            print("old_albedo_tint_color_diff - execute - simple values BSDF to msfs_*")
                            print("5")
                            mat.msfs_base_color_factor = principled.inputs["Base Color"].default_value
                            mat.msfs_metallic_factor = principled.inputs[bsdfinputs6].default_value
                            mat.msfs_roughness_factor = principled.inputs[bsdfinputs9].default_value
                            print("6")
                        except:
                            print("old_albedo_tint_color_diff - execute - old_properties - Error - BSDF properties found skipping")

                except:
                    print("old_albedo_tint_color_diff - execute - Error - Base Color skipping")
                    #pass

            finally:
                pass

            # put Emissive color stuff here

            print("old_emissive_tint_color_diff - execute - mat", mat)
            try:
                if mat.node_tree.nodes["emissive_tint"] is not None:
                    # get color
                    emissive_tint_checkval = mat.node_tree.nodes["emissive_tint"].outputs[0].default_value
                    # get BSDF base Color value
                    BSDF_Emission = principled.inputs[bsdfinputs19].default_value[0:3]
                    #print("old_emissive_tint_color_diff execute - BSDF Emission", BSDF_Emission)
                    if not equality_check(BSDF_Emission, emissive_tint_checkval, len(BSDF_Emission), len(emissive_tint_checkval)):
                        mat.node_tree.nodes["emissive_tint"].outputs[0].default_value = BSDF_Emission
                        mat.msfs_emissive_factor = BSDF_Emission
                       # should add like too to make button go away
            except:
                print("old_emissive_tint_color_diff - execute - Error - TRY - emissive_tint skipping")
                try:
                    if mat.msfs_material_type != "NONE":
                        print("old_emissive_tint_color_diff - execute - Emissive")
                        BSDF_Emission = principled.inputs[bsdfinputs19].default_value[0:3]
                        ###print("old_emissive_tint_color_diff - execute - BSDF to MSFS emissive", BSDF_Emission[0], mat.msfs_emissive_factor[0], BSDF_Emission[1], mat.msfs_emissive_factor[1], BSDF_Emission[2], mat.msfs_emissive_factor[2], BSDF_Emission[3], mat.msfs_emissive_factor[3])
                        # set default in case not there.
                        #try:
                        print("old_emissive_tint_color_diff - execute - msfs_emissive_factor")
                        if not mat.msfs_emissive_factor:
                            mat.msfs_emissive_factor = mat.msfs_emissive_factor.default
                        if not equality_check(BSDF_Emission, mat.msfs_emissive_factor, len(BSDF_Emission), len(mat.msfs_emissive_factor)):
                            print("1")
                            mat.msfs_emissive_factor = BSDF_Emission
                            print("2")
                        #else:
                        #    mat.msfs_emissive_factor = BSDF_Emissive
                        print("old_emissive_tint_color_diff - execute - Emissive Done")
                    elif mat.msfs_material_type == "NONE" and mat.msfs_material_mode == "NONE":
                        # SPECIAL now if you have had msfs properties values - assume msfs_standard - make a wild guess because there was data here from before.
                        try:
                            print("old_emissive_tint_color_diff - execute - simple values BSDF to msfs_*")
                            mat.msfs_emissive_factor = principled.inputs[bsdfinputs19].default_value
                        except:
                            print("old_emissive_tint_color_diff - execute - old_properties - Error - BSDF to msfs_ skipping")
                except:
                    print("old_emissive_tint_color_diff - execute - old_properties - Error - msfs_emissive_factor skipping")
            finally:
                pass

            # input 6 Metallic
            print("7")
            if not principled.inputs[bsdfinputs6].links and principled.inputs[bsdfinputs6].default_value != mat.msfs_metallic_factor:
                mat.msfs_metallic_factor = principled.inputs[bsdfinputs6].default_value
                print("7- metallic_factor",mat.msfs_metallic_factor)
            # input 9 Roughness
            if not principled.inputs[bsdfinputs9].links and principled.inputs[bsdfinputs9].default_value != mat.msfs_roughness_factor:
                mat.msfs_roughness_factor = principled.inputs[bsdfinputs9].default_value
                print("7- roughness_factor",mat.msfs_roughness_factor)
            # input 20 Emissive Scale
            if not principled.inputs[bsdfinputs20].links and principled.inputs[bsdfinputs20].default_value != mat.msfs_emissive_scale and principled.inputs[bsdfinputs20].default_value > 0.0:
                mat.msfs_emissive_scale = principled.inputs[bsdfinputs20].default_value
                print("7- emissive_scale",mat.msfs_emissive_scale)
            print("8")
        return {"FINISHED"}


class MSFS_OT_MigrateMaterialData(bpy.types.Operator): # TODO: Remove eventually
    """This addon changes some of the internal property names. This current material has older properties, and is able to be migrated.\nWARNING: This removes all the old properties from the material"""

    bl_idname = "msfs.migrate_material_data"
    bl_label = "Migrate Material Data"

    # old order matters as the really old legacy checked first can be overridden by new legacy
    old_property_to_new_mapping = {
        "msfs_decal_blend_factor_color": "msfs_decal_color_blend_factor",
        "msfs_decal_blend_factor_roughness": "msfs_roughness_blend_factor",
        "msfs_decal_blend_factor_metal": "msfs_metallic_blend_factor",
        "msfs_decal_blend_factor_occlusion": "msfs_occlusion_blend_factor",
        "msfs_decal_blend_factor_normal": "msfs_normal_blend_factor",
        "msfs_decal_blend_factor_emissive": "msfs_emissive_blend_factor",
        "windshield": "msfs_windshield",
        "geo_decal": "msfs_base_color_blend_factor",
        "msfs_color_sss": "msfs_sss_color",
        "msfs_use_pearl_effect ": "msfs_use_pearl",
        "msfs_decal_color_blend_factor": "msfs_base_color_blend_factor",
        "msfs_decal_metal_blend_factor": "msfs_metallic_blend_factor",
        "msfs_decal_normal_blend_factor": "msfs_normal_blend_factor",
        "msfs_decal_roughness_blend_factor": "msfs_roughness_blend_factor",
        "msfs_decal_occlusion_blend_factor": "msfs_occlusion_blend_factor",
        "msfs_decal_emissive_blend_factor": "msfs_emissive_blend_factor",
        "msfs_fresnel_opacity_bias": "msfs_fresnel_opacity_offset",
        "msfs_parallax_room_number": "msfs_parallax_room_number_xy",
        "msfs_geo_decal_blend_factor_color": "msfs_base_color_blend_factor",
        "msfs_geo_decal_blend_factor_metal": "msfs_metallic_blend_factor",
        "msfs_geo_decal_blend_factor_normal": "msfs_normal_blend_factor",
        "msfs_geo_decal_blend_factor_roughness": "msfs_roughness_blend_factor",
        "msfs_geo_decal_blend_factor_blast_sys": "msfs_occlusion_blend_factor",
        "msfs_geo_decal_blend_factor_melt_sys": "msfs_emissive_blend_factor",
        "msfs_draw_order": "msfs_draw_order_offset",
        "msfs_road_material": "msfs_road_collision_material",
        "msfs_uv_clamp_x": "msfs_clamp_uv_x",
        "msfs_uv_clamp_y": "msfs_clamp_uv_y",
        "msfs_uv_clamp_z": "msfs_clamp_uv_z",
        "msfs_roughness_scale": "msfs_roughness_factor",
        "msfs_metallic_scale": "msfs_metallic_factor",
        "msfs_detail_uv_offset_x": "msfs_detail_uv_offset_u",
        "msfs_detail_uv_offset_y": "msfs_detail_uv_offset_v",
        "msfs_blend_threshold": "msfs_detail_blend_threshold",
        "msfs_height_map_texture": "msfs_normal_texture",
        "msfs_behind_glass_texture": "msfs_detail_color_texture",
        "msfs_albedo_texture": "msfs_base_color_texture",
        "msfs_comp_texture": "msfs_occlusion_metallic_roughness_texture",
        "msfs_metallic_texture": "msfs_occlusion_metallic_roughness_texture",
        "msfs_detail_albedo_texture": "msfs_detail_color_texture",
        "msfs_detail_comp_texture": "msfs_detail_occlusion_metallic_roughness_texture",
        "msfs_detail_metallic_texture": "msfs_detail_occlusion_metallic_roughness_texture",
        "msfs_anisotropic_direction_texture": "msfs_extra_slot1_texture",
        "msfs_clearcoat_texture": "msfs_dirt_texture",
    }

    @staticmethod
    def old_properties_present(mat):
        if len(mat.keys()) > 0: # Don't unnecessarily loop if we have no properties on the material
            for old_property in MSFS_OT_MigrateMaterialData.old_property_to_new_mapping:
                if mat.get(old_property) is not None:
                    return True
        return False

    def execute(self, context):
        mat = context.active_object.active_material
        # ToDo: FBW msfs_material_type mapping
        Is_thereFBW_material = Is_it_FBW_Material(mat)
        base_color = [1.0, 1.0, 1.0, 1.0]
        alpha = 1.0
        emissive_color = [0.0, 0.0, 0.0]
        print("MSFS_OT_MigrateMaterialData - execute - msfs_material_mode and Is_thereFBW_material", mat.get("msfs_material_mode"), Is_thereFBW_material)
        for (
            old_property,
            new_property,
        ) in MSFS_OT_MigrateMaterialData.old_property_to_new_mapping.items():
            print("execute - list properties", old_property, new_property, mat.get(new_property))
            if mat.get(old_property) is not None:
                print("execute - found old properties", old_property, new_property)
                # msfs_behind_glass_texture and msfs_detail_albedo_texture are special cases as they are they write to the same property
                if mat.get("msfs_material_mode") == "msfs_windshield" and old_property == "msfs_behind_glass_texture":
                    del mat[old_property]
                    continue
                if mat.get("msfs_material_mode") == "msfs_parallax" and old_property == "msfs_detail_albedo_texture":
                    del mat[old_property]
                    continue
                if mat.get(new_property) is not None:
                    print("prop", mat.get(new_property), mat.get(old_property))
                    try:
                        print("names", mat.get(new_property).name, mat.get(old_property).name, mat.get(old_property).id_data)
                        mat.get(new_property).name = mat.get(old_property).name
                    except:
                        print("execute - new property test fail")
                        pass
                try:
                    print("execute - make change to property - old new", old_property, mat.get(old_property), new_property, mat.get(new_property))
                    mat[new_property] = mat[old_property]
                    print("execute - after make change old new", mat[old_property], mat[new_property])
                except:
                    print("execute - ERROR did not carry over", mat, old_property, mat.get(old_property), new_property, mat.get(new_property))
                del mat[old_property]
        print("execute - make change to property - old new DONE")
        # Base Color is a special case - can only have 3 values, we need 4
        if mat.get("msfs_color_alpha_mix"):
            alpha = mat.get("msfs_color_alpha_mix")
        elif mat.get("msfs_color_base_mix"):
            alpha = mat.get("msfs_color_base_mix")
        else:
            print("execute - no msfs_color_alpha_mix Base Color", mat)
            try:
                n = mat.node_tree.nodes["albedo_tint"]
                print("albedo_tint nodes", n, n.outputs[0], n.outputs[0].default_value)
                alpha = n.outputs[0].default_value[3]
                print("current alpha", alpha)
            except:
                print("execute - Base Color Alpha - Exception - albedo_tint not found skipping")
                try:
                    nodes = mat.node_tree.nodes
                    bsdfnodes = [n for n in nodes 
                            if isinstance(n, bpy.types.ShaderNodeBsdfPrincipled)]
                    for principled in bsdfnodes:
                        BSDF_Base_Color = principled.inputs["Base Color"].default_value
                        print("execute - BSDF to MSFS base color alpha", BSDF_Base_Color[0], mat.msfs_base_color_factor[0], BSDF_Base_Color[1], mat.msfs_base_color_factor[1], BSDF_Base_Color[2], mat.msfs_base_color_factor[2], BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                        alpha = BSDF_Base_Color[3]
                        if BSDF_Base_Color[3] != mat.msfs_base_color_factor[3]:
                            print("alpha diff", BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                            if BSDF_Base_Color[3] == 1.0:
                                print("alpha diff", BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                                alpha = mat.msfs_base_color_factor[3]
                            else:
                                print("alpha diff - base", BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                                alpha = principled.inputs["Base Color"].default_value[3]
                except:
                    print("execute - Base Color Alpha - Exception - BSDF Base Color not found skipping")
            finally:
                pass

        print("msfs_color_albedo_mix")
        # Base Color factor is also a special case
        if mat.get("msfs_color_albedo_mix"):
            base_color = list(mat.get("msfs_color_albedo_mix"))
            print("execute - msfs_color_albedo_mix list", base_color)
        else:
            print("execute - no msfs_color_albedo_mix Base Color Factor", mat)
            try:
                print("execute - albedo_tint nodes")
                n = mat.node_tree.nodes["albedo_tint"]
                print("execute - albedo_tint nodes", n, n.outputs[0], n.outputs[0].default_value)
                base_color[0] = n.outputs[0].default_value[0]
                base_color[1] = n.outputs[0].default_value[1]
                base_color[2] = n.outputs[0].default_value[2]
                print("current albedo base_color", base_color)
            except:
                print("execute - Base Color Factor - Exception - albedo_tint not found skipping")
                try:
                    print("bsdf color")
                    nodes = mat.node_tree.nodes
                    bsdfnodes = [n for n in nodes 
                            if isinstance(n, bpy.types.ShaderNodeBsdfPrincipled)]
                    for principled in bsdfnodes:
                        BSDF_Base_Color = principled.inputs["Base Color"].default_value
                        print("execute - BSDF to MSFS base color", BSDF_Base_Color[0], mat.msfs_base_color_factor[0], BSDF_Base_Color[1], mat.msfs_base_color_factor[1], BSDF_Base_Color[2], mat.msfs_base_color_factor[2], BSDF_Base_Color[3], mat.msfs_base_color_factor[3])
                        # if BSDF_Base_Color[0] != 0 and BSDF_Base_Color[1] != 0 and BSDF_Base_Color[2] != 0: 
                            # base_color = BSDF_Base_Color
                        # else:
                        base_color = mat.msfs_base_color_factor
                    print("current bsdf base_color", base_color)
                except:
                    print("execute - Base Color - Exception - BSDF Base Color not found skipping")
                    pass
            finally:
                pass
        # add in alpha found previously
        if len(base_color) == 3:
            base_color.append(alpha)
        else:
            base_color[3] = alpha
        print("final base_color", base_color)

        # save and do at end when new material is made
        #mat.msfs_base_color_factor = base_color

        # Emissive factor is also a special case - old material system had 4 floats, we only need 3
        print("execute - Emissive START", mat)
        if mat.get("msfs_color_emissive_mix"):
            emissive_color = mat.get("msfs_color_emissive_mix")[0:3]
            print("execute - msfs_color_emissive_mix - Done", emissive_color)
        else:
            try:
                print("execute - no msfs_color_emissive_mix", mat)
                n = mat.node_tree.nodes["emissive_tint"]
                print("execute - emissive_tint node list", n, n.outputs[0], n.outputs[0].default_value)
                emissive_color = n.outputs[0].default_value[0:3]
                print(emissive_color)
            except:
                print("execute - Emissive Color - Error - emissive_tint not found skipping")
                try:
                    nodes = mat.node_tree.nodes
                    bsdfnodes = [n for n in nodes if isinstance(n, bpy.types.ShaderNodeBsdfPrincipled)]
                    print("bsdf emissive")
                    for principled in bsdfnodes:
                        BSDF_Emissive = principled.inputs["Emission Color"].default_value[0:3]
                        print("execute - BSDF to MSFS emissive", BSDF_Emissive[0], mat.msfs_emissive_factor[0], BSDF_Emissive[1], mat.msfs_emissive_factor[1], BSDF_Emissive[2], mat.msfs_emissive_factor[2])
                        if not equality_check(BSDF_Emissive, mat.msfs_emissive_factor, len(BSDF_Emissive), len(mat.msfs_emissive_factor)):
                            print("1M")
                            emissive_color = mat.msfs_emissive_factor
                            print("2M")
                        else:
                            emissive_color = BSDF_Emissive
                except:
                    print("execute - emissive BSDF Exception", bsdfnodes)
                    pass
            finally:
                pass
        # save and do at end when new material is made
        #mat.msfs_emissive_factor = emissive_color[0:3]

        # Do our enums manually as only their index of the value are stored - not the string
        if mat.get("msfs_blend_mode"):
            old_alpha_order = [
                "OPAQUE",
                "MASK",  # Changed from old version - matches new name
                "BLEND",
                "DITHER",
            ]
            # save and do at end when new material is made
            mat.msfs_alpha_mode = old_alpha_order[mat["msfs_blend_mode"]]

            del mat["msfs_blend_mode"]

        # ToDo: could be FBW order - need to determine
        # FBW importer has a custom Property of is_import
        if mat.get("msfs_material_mode"):
            old_material_older = [  # Assuming the user uninstalled the old plugin, the index of the value will be stored instead of the name of the current material. Replicate the order here
                "NONE",
                "msfs_standard",
                "msfs_anisotropic",
                "msfs_sss",
                "msfs_glass",
                "msfs_geo_decal",  # Changed from old version - matches new name
                "msfs_clearcoat",
                "msfs_environment_occluder",  # Changed from old version - matches new name
                "msfs_fake_terrain",
                "msfs_fresnel_fade",  # Changed from old version - matches new name
                "msfs_windshield",
                "msfs_porthole",
                "msfs_parallax",
                "msfs_geo_decal_frosted",  # Changed from old version - matches new name
                "msfs_hair",
                "msfs_invisible",
                "msfs_ghost",  # added because my legacy mod has it????
            ]
            # save and do at end when new material is made
            mat.msfs_material_type = old_material_older[mat["msfs_material_mode"]]

            del mat["msfs_material_mode"]
            try:
                if mat["msfs_material_fbw"] != "NONE":
                    del mat["msfs_material_fbw"]
            except:
                pass

        #do at end when new material is made




        if base_color is not None and mat.msfs_base_color_factor is not None:
            #print("execute - base color before final", base_color[0], mat.msfs_base_color_factor[0], base_color[1], mat.msfs_base_color_factor[1], base_color[2], mat.msfs_base_color_factor[2], base_color[3], mat.msfs_base_color_factor[3])
            print("execute - base color before final", mat.msfs_base_color_factor[0], mat.msfs_base_color_factor[1], mat.msfs_base_color_factor[2], mat.msfs_base_color_factor[3])
            print(base_color)
            mat.msfs_base_color_factor = base_color
            # mat.msfs_base_color_factor[1].default_value = base_color[1]
            # mat.msfs_base_color_factor[2].default_value = base_color[2]
            # mat.msfs_base_color_factor[3].default_value = base_color[3]
        if emissive_color is not None and mat.msfs_emissive_factor is not None:
            #print("execute - emissive before final", emissive_color[0], mat.msfs_emissive_factor[0], emissive_color[1], mat.msfs_emissive_factor[1], emissive_color[2], mat.msfs_emissive_factor[2])
            print(emissive_color)
            mat.msfs_emissive_factor = emissive_color[0:3]
            # mat.msfs_emissive_factor[1] = emissive_color[1]
            # mat.msfs_emissive_factor[2] = emissive_color[2]
        MSFS_Material_Property_Update.update_msfs_material_type(mat, context)

        print("Migrate material - Done")
        return {"FINISHED"}


class MSFS_PT_Material(bpy.types.Panel):
    bl_label = "MSFS Material Params"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def draw_prop(self, layout, mat, prop, enabled=True, visible=True, text=""):
        if visible:
            column = layout.column()
            if text:
                column.prop(mat, prop, text=text)
            else:
                column.prop(mat, prop)

            column.enabled = enabled

    def draw_texture_prop(self, layout, mat, prop, enabled=True, visible=True, text=""):
        if visible:
            column = layout.column()
            if text:
                column.label(text=text)

            column.template_ID(mat, prop, new="image.new", open="image.open")
            column.enabled = enabled

    def draw(self, context):
        layout = self.layout
        # Disabled animation UI until material animations are properly implemented
        # layout.use_property_split = True
        # layout.use_property_decorate = True

        mat = context.active_object.active_material
        obj = context.active_object
        # this seems to be the only place I can check if the addon prefs match the 
        # the multi export settings that in clude all the addon settings
        addonpreferences = get_prefs()
        if mat:
            # test if project needs vertex colors
            if addonpreferences.export_vertexcolor_project and MSFS_OT_vertex_color_white_Data.vertex_color_white_attribute_is_required(mat, obj):
                layout.operator(MSFS_OT_vertex_color_white_Data.bl_idname)

            if MSFS_OT_glTfSettingsMaterialData.gltf_settings_with_dot_present():
                layout.operator(MSFS_OT_glTfSettingsMaterialData.bl_idname)

            if MSFS_OT_MigrateColorFixData.old_material_values_diff(mat):
                layout.operator(MSFS_OT_MigrateColorFixData.bl_idname)

            if MSFS_OT_MigrateMaterialData.old_properties_present(mat):
                layout.operator(MSFS_OT_MigrateMaterialData.bl_idname)
            self.draw_prop(layout, mat, "msfs_material_type", enabled=mat.msfs_material_fbw == "NONE")

            if mat.msfs_material_mode != "NONE":
                self.draw_prop(layout, mat, "msfs_material_mode", enabled=False)

            if mat.msfs_material_fbw != "NONE":
                self.draw_prop(layout, mat, "msfs_material_fbw", enabled=False)

            if mat.msfs_material_type != "NONE" or mat.msfs_material_mode != "NONE":
                self.draw_prop(layout, mat, "msfs_base_color_factor")
                self.draw_prop(
                    layout,
                    mat,
                    "msfs_emissive_factor",
                    enabled=(
                        mat.msfs_material_type
                        not in ["msfs_invisible", "msfs_environment_occluder"]
                    ),
                )

                # Alpha mode
                box = layout.box()
                box.label(text="Alpha Mode")
                box.enabled = mat.msfs_material_type in [
                    "msfs_standard",
                    "msfs_anisotropic",
                    "msfs_hair",
                    "msfs_sss",
                    "msfs_fresnel_fade",
                    "msfs_clearcoat",
                ]
                self.draw_prop(box, mat, "msfs_alpha_mode")

                # Render params
                box = layout.box()
                box.label(text="Render Parameters")
                box.enabled = mat.msfs_material_type not in [
                    "msfs_invisible",
                    "msfs_environment_occluder",
                ]
                self.draw_prop(box, mat, "msfs_draw_order_offset")
                self.draw_prop(
                    box,
                    mat,
                    "msfs_no_cast_shadow",
                    enabled=(mat.msfs_material_type != "msfs_ghost"),
                )
                self.draw_prop(box, mat, "msfs_double_sided")
                self.draw_prop(
                    box,
                    mat,
                    "msfs_day_night_cycle",
                    enabled=(mat.msfs_material_type == "msfs_standard"),
                )
                self.draw_prop(box, mat, "msfs_disable_motion_blur")

                # Gameplay params
                box = layout.box()
                box.label(text="Gameplay Parameters")
                box.enabled = mat.msfs_material_type != "msfs_environment_occluder"
                self.draw_prop(box, mat, "msfs_collision_material")
                self.draw_prop(box, mat, "msfs_road_collision_material")

                # UV options
                box = layout.box()
                box.label(text="UV Options")
                box.enabled = mat.msfs_material_type not in [
                    "msfs_invisible",
                    "msfs_environment_occluder",
                ]
                self.draw_prop(box, mat, "msfs_uv_offset_u")
                self.draw_prop(box, mat, "msfs_uv_offset_v")
                self.draw_prop(box, mat, "msfs_uv_tiling_u")
                self.draw_prop(box, mat, "msfs_uv_tiling_v")
                self.draw_prop(box, mat, "msfs_uv_rotation")

                # UV clamp
                box = layout.box()
                box.label(text="UV Clamp")
                box.enabled = mat.msfs_material_type != "msfs_environment_occluder"
                self.draw_prop(box, mat, "msfs_clamp_uv_x")
                self.draw_prop(box, mat, "msfs_clamp_uv_y")

                # General params
                box = layout.box()
                box.label(text="General Parameters")
                box.enabled = mat.msfs_material_type not in [
                    "msfs_invisible",
                    "msfs_environment_occluder",
                ]
                self.draw_prop(box, mat, "msfs_metallic_factor")
                self.draw_prop(box, mat, "msfs_roughness_factor")
                self.draw_prop(box, mat, "msfs_normal_scale")
                self.draw_prop(
                    box,
                    mat,
                    "msfs_alpha_cutoff",
                    enabled=(
                        mat.msfs_material_type
                        in [
                            "msfs_standard",
                            "msfs_anisotropic",
                            "msfs_hair",
                            "msfs_sss",
                            "msfs_fresnel_fade",
                            "msfs_clearcoat",
                        ]
                        and mat.msfs_alpha_mode == "MASK"
                    ),
                )
                self.draw_prop(
                    box,
                    mat,
                    "msfs_detail_uv_scale",
                    enabled=(
                        mat.msfs_material_type
                        not in ["msfs_parallax", "msfs_fresnel_fade", "msfs_sss"]
                    ),
                )
                self.draw_prop(
                    box,
                    mat,
                    "msfs_detail_uv_offset_u",
                    enabled=(
                        mat.msfs_material_type
                        not in ["msfs_parallax", "msfs_fresnel_fade", "msfs_sss"]
                    ),
                )
                self.draw_prop(
                    box,
                    mat,
                    "msfs_detail_uv_offset_v",
                    enabled=(
                        mat.msfs_material_type
                        not in ["msfs_parallax", "msfs_fresnel_fade", "msfs_sss"]
                    ),
                )
                self.draw_prop(
                    box,
                    mat,
                    "msfs_detail_normal_scale",
                    enabled=(
                        mat.msfs_material_type
                        not in ["msfs_parallax", "msfs_fresnel_fade", "msfs_sss"]
                    ),
                )
                self.draw_prop(
                    box,
                    mat,
                    "msfs_detail_blend_threshold",
                    enabled=(
                        mat.msfs_material_type not in ["msfs_fresnel_fade", "msfs_sss"]
                        and mat.msfs_blend_mask_texture is not None
                    ),
                )
                self.draw_prop(
                    box,
                    mat,
                    "msfs_emissive_scale",
                    enabled=(
                        mat.msfs_material_type
                        not in ["msfs_invisible", "msfs_environment_occluder"]
                    ),
                )
                # check if project need vertex colors
                self.draw_prop(
                    box,
                    mat,
                    "msfs_vertexcolor_scale",
                    enabled=(
                        mat.msfs_material_type
                        not in ["msfs_invisible", "msfs_environment_occluder"]
                    ),
                )

                # Decal params
                if mat.msfs_material_type in [
                    "msfs_geo_decal",
                    "msfs_geo_decal_frosted",
                ]:
                    box = layout.box()
                    box.label(text="Decal Blend Factors")
                    box.enabled = mat.msfs_material_type in [
                        "msfs_geo_decal",
                        "msfs_geo_decal_frosted",
                    ]
                    self.draw_prop(box, mat, "msfs_base_color_blend_factor")
                    self.draw_prop(box, mat, "msfs_roughness_blend_factor")
                    self.draw_prop(box, mat, "msfs_metallic_blend_factor")
                    self.draw_prop(
                        box,
                        mat,
                        "msfs_occlusion_blend_factor",
                        text="Blast Sys Blend Factor"
                        if mat.msfs_material_type == "msfs_geo_decal_frosted"
                        else "",
                    )
                    self.draw_prop(box, mat, "msfs_normal_blend_factor")
                    self.draw_prop(
                        box,
                        mat,
                        "msfs_emissive_blend_factor",
                        text="Melt Sys Blend Factor"
                        if mat.msfs_material_type == "msfs_geo_decal_frosted"
                        else "",
                    )

                # SSS params - enabled
                if mat.msfs_material_type in ["msfs_sss", "msfs_hair"]:
                    box = layout.box()
                    box.label(text="SSS Parameters")
                    box.enabled = (mat.msfs_material_type  == "msfs_sss") or (mat.msfs_material_type == "msfs_hair")
                    self.draw_prop(
                        box, mat, "msfs_sss_color", enabled=True
                    )

                # Glass params
                if mat.msfs_material_type == "msfs_glass":
                    box = layout.box()
                    box.label(text="Glass Parameters")
                    box.enabled = mat.msfs_material_type == "msfs_glass"
                    self.draw_prop(box, mat, "msfs_glass_reflection_mask_factor")
                    self.draw_prop(box, mat, "msfs_glass_deformation_factor")

                # Parallax params
                if mat.msfs_material_type == "msfs_parallax":
                    box = layout.box()
                    box.label(text="Parallax Parameters")
                    box.enabled = mat.msfs_material_type == "msfs_parallax"
                    self.draw_prop(box, mat, "msfs_parallax_scale")
                    self.draw_prop(box, mat, "msfs_parallax_room_size_x")
                    self.draw_prop(box, mat, "msfs_parallax_room_size_y")
                    self.draw_prop(box, mat, "msfs_parallax_room_number_xy")
                    self.draw_prop(box, mat, "msfs_parallax_corridor")

                # Fresnel params
                if mat.msfs_material_type == "msfs_fresnel_fade":
                    box = layout.box()
                    box.label(text="Fresnel Parameters")
                    box.enabled = mat.msfs_material_type == "msfs_fresnel_fade"
                    self.draw_prop(box, mat, "msfs_fresnel_factor")
                    self.draw_prop(box, mat, "msfs_fresnel_opacity_offset")

                # Ghost params
                if mat.msfs_material_type == "msfs_ghost":
                    box = layout.box()
                    box.label(text="Ghost Parameters")
                    box.enabled = mat.msfs_material_type == "msfs_ghost"
                    self.draw_prop(box, mat, "msfs_ghost_bias")
                    self.draw_prop(box, mat, "msfs_ghost_power")
                    self.draw_prop(box, mat, "msfs_ghost_scale")

                # Windshield params
                if mat.msfs_material_type == "msfs_windshield":
                    box = layout.box()
                    box.label(text="Windshield Parameters")
                    box.enabled = mat.msfs_material_type == "msfs_windshield"
                    self.draw_prop(box, mat, "msfs_rain_drop_scale")
                    self.draw_prop(box, mat, "msfs_wiper_1_state")
                    self.draw_prop(box, mat, "msfs_wiper_2_state")
                    self.draw_prop(box, mat, "msfs_wiper_3_state", visible=False)
                    self.draw_prop(box, mat, "msfs_wiper_4_state", visible=False)

                # Pearl params
                if mat.msfs_material_type == "msfs_standard":
                    box = layout.box()
                    box.label(text="Pearl Parameters")
                    box.enabled = mat.msfs_material_type == "msfs_standard"
                    self.draw_prop(box, mat, "msfs_use_pearl")
                    self.draw_prop(box, mat, "msfs_pearl_shift")
                    self.draw_prop(box, mat, "msfs_pearl_range")
                    self.draw_prop(box, mat, "msfs_pearl_brightness")

                # Textures
                if mat.msfs_material_type not in [
                    "msfs_invisible",
                    "msfs_environment_occluder",
                ]:
                    box = layout.box()
                    box.label(text="Textures")

                    # In the 3DS Max exporter, the textures have different display names depending on material type and other properties used. We replicate that process here
                    base_color_tex_name = "Base Color"
                    occlusion_metallic_roughness_texture_name = (
                        "Occlusion (R), Roughness (G), Metallic (B)"
                    )
                    normal_texture_name = "Normal"
                    blend_mask_texture_name = "Blend Mask"
                    dirt_texture_name = "Clearcoat amount (R), Clearcoat rough (G)"
                    extra_slot1_texture = "Extra Slot 1"
                    emissive_texture_name = "Emissive"
                    detail_color_texture_name = "Secondary Color (RGB), Alpha (A)"
                    detail_occlusion_metallic_roughness_texture_name = (
                        "Secondary Occ (R), Rough (G), Metal (B)"
                    )
                    detail_normal_texture_name = "Secondary Normal"

                    if mat.msfs_blend_mask_texture is None:
                        detail_color_texture_name = "Detail Color (RGB), Alpha (A)"
                        detail_normal_texture_name = "Detail Normal"
                        detail_occlusion_metallic_roughness_texture_name = (
                            "Detail Occlusion (R), Roughness (G), Metallic (B)"
                        )

                    if mat.msfs_material_type == "msfs_windshield":
                        emissive_texture_name = "Secondary Details (Dirt)(A)"
                        extra_slot1_texture = "Wiper Mask (RG)"
                        detail_color_texture_name = (
                            "Details Scratch(R), Icing Mask(G), Fingerprints(B)"
                        )
                        detail_normal_texture_name = "Icing Normal (use DetailMap UV)"
                    elif mat.msfs_material_type == "msfs_geo_decal_frosted":
                        detail_occlusion_metallic_roughness_texture_name = (
                            "Melt pattern (R), Roughness (G), Metallic (B)"
                        )
                    elif mat.msfs_material_type == "msfs_parallax":
                        base_color_tex_name = "Front Glass Color"
                        normal_texture_name = "Front Glass Normal"
                        detail_color_texture_name = (
                            "Behind Glass Color (RGB), Alpha (A)"
                        )
                        emissive_texture_name = (
                            "Emissive Ins Window (RGB), offset Time (A)"
                        )
                    elif mat.msfs_material_type in ["msfs_anisotropic", "msfs_hair"]:
                        extra_slot1_texture = "Anisotropic direction (RG)"

                    self.draw_texture_prop(
                        box, mat, "msfs_base_color_texture", text=base_color_tex_name
                    )
                    self.draw_texture_prop(
                        box,
                        mat,
                        "msfs_occlusion_metallic_roughness_texture",
                        text=occlusion_metallic_roughness_texture_name,
                    )
                    self.draw_texture_prop(
                        box, mat, "msfs_normal_texture", text=normal_texture_name
                    )
                    self.draw_texture_prop(
                        box, mat, "msfs_emissive_texture", text=emissive_texture_name
                    )

                    if mat.msfs_material_type not in [
                        "msfs_hair",
                        "msfs_sss",
                        "msfs_fresnel_fade",
                    ]:
                        self.draw_texture_prop(
                            box,
                            mat,
                            "msfs_detail_color_texture",
                            text=detail_color_texture_name,
                        )
                    if mat.msfs_material_type not in [
                        "msfs_parallax",
                        "msfs_hair",
                        "msfs_sss",
                        "msfs_fresnel_fade",
                    ]:
                        self.draw_texture_prop(
                            box,
                            mat,
                            "msfs_detail_normal_texture",
                            text=detail_normal_texture_name,
                        )
                        self.draw_texture_prop(
                            box,
                            mat,
                            "msfs_detail_occlusion_metallic_roughness_texture",
                            text=detail_occlusion_metallic_roughness_texture_name,
                        )
                    if mat.msfs_material_type not in [
                        "msfs_geo_decal_frosted",
                        "msfs_parallax",
                        "msfs_hair",
                        "msfs_sss",
                        "msfs_fresnel_fade",
                        "msfs_ghost",
                    ]:
                        self.draw_texture_prop(
                            box,
                            mat,
                            "msfs_blend_mask_texture",
                            text=blend_mask_texture_name,
                        )
                    if mat.msfs_material_type in [
                        "msfs_winshield",
                        "msfs_anisotropic",
                        "msfs_hair",
                    ]:
                        self.draw_texture_prop(
                            box,
                            mat,
                            "msfs_extra_slot1_texture",
                            text=extra_slot1_texture,
                        )
                    if mat.msfs_material_type == "msfs_clearcoat":
                        self.draw_texture_prop(
                            box, mat, "msfs_dirt_texture", text=dirt_texture_name
                        )
