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

from .material.utils.msfs_material_enum import (MSFS_AnisotropicNodes,
                                                MSFS_FrameNodes,
                                                MSFS_PrincipledBSDFInputs,
                                                MSFS_ShaderNodes,
                                                MSFS_ShaderNodesTypes,
                                                MSFS_MixNodeInputs,
                                                MSFS_MixNodeOutputs,
                                                MSFS_BSDFNodeInputs,
                                                MSFS_GroupNodes)
from .. import get_prefs


class MSFS_Material:
    bl_idname = "MSFS_ShaderNodeTree"
    bl_label = "MSFS Shader Node Tree"
    bl_icon = "SOUND"

    def __init__(self, material, buildTree=False):
        self.getInputOutputIndex()
        self.material = material
        if not material.use_nodes:
            material.use_nodes = True
        self.node_tree = self.material.node_tree
        self.nodes = self.material.node_tree.nodes
        self.links = material.node_tree.links
        if buildTree:
            self.__buildShaderTree()
            self.force_update_properties()

    def getInputOutputIndex(self):
        index1 = 1
        index_B4 = 1 # index for Blender v4
        if(bpy.app.version < (3, 4, 0)):
            index1 = 0
        if(bpy.app.version < (4, 0, 0)):
            index_B4 = 0

        self.outputs0 = MSFS_MixNodeOutputs.outputs[index1][0]
        self.inputs0 = MSFS_MixNodeInputs.inputs[index1][0]
        self.inputs1 = MSFS_MixNodeInputs.inputs[index1][1]
        self.inputs2 = MSFS_MixNodeInputs.inputs[index1][2]
        self.bsdfinputs6 = MSFS_BSDFNodeInputs.inputs[index_B4][0]
        self.bsdfinputs9 = MSFS_BSDFNodeInputs.inputs[index_B4][1]
        self.bsdfinputs20 = MSFS_BSDFNodeInputs.inputs[index_B4][2]
        self.bsdfinputs21 = MSFS_BSDFNodeInputs.inputs[index_B4][3]
        
    def revertToPBRShaderTree(self):
        self.cleanNodeTree()
        self.__createPBRTree()

    def __buildShaderTree(self):
        self.cleanNodeTree()
        self.createNodetree()

    def force_update_properties(self):
        from .msfs_material_prop_update import MSFS_Material_Property_Update

        MSFS_Material_Property_Update.update_base_color_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_comp_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_normal_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_emissive_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_detail_color_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_detail_comp_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_detail_normal_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_blend_mask_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_extra_slot1_texture(self.material, bpy.context)
        MSFS_Material_Property_Update.update_dirt_texture(self.material, bpy.context)
        # MSFS_Material_Property_Update.update_wiper_mask(self.material, bpy.context) -- Does not work in game for now
        MSFS_Material_Property_Update.update_alpha_mode(self.material, bpy.context)
        MSFS_Material_Property_Update.update_emissive_scale(self.material, bpy.context)
        MSFS_Material_Property_Update.update_normal_scale(self.material, bpy.context)
        MSFS_Material_Property_Update.update_color_sss(self.material, bpy.context)
        MSFS_Material_Property_Update.update_double_sided(self.material, bpy.context)
        MSFS_Material_Property_Update.update_alpha_cutoff(self.material, bpy.context)
        MSFS_Material_Property_Update.update_detail_uv(self.material, bpy.context)
        # Trigger setters
        MSFS_Material_Property_Update.update_base_color(self.material, bpy.context)
        MSFS_Material_Property_Update.update_emissive_color(self.material, bpy.context)
        MSFS_Material_Property_Update.update_metallic_scale(self.material, bpy.context)
        MSFS_Material_Property_Update.update_roughness_scale(self.material, bpy.context)

    def cleanNodeTree(self):
        nodes = self.material.node_tree.nodes
        for idx, node in enumerate(nodes):
            print("Deleting: %s | %s" % (node.name, node.type))
            nodes.remove(node)

    def __createPBRTree(self):
        nodeOutputMaterial = self.addNode(
            name = MSFS_ShaderNodes.ShaderOutputMaterial.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeOutputMaterial.value,
            location = (1200.0, 50.0),
            hidden = False
        )
        principledBSDF = self.addNode(
            name = MSFS_ShaderNodes.principledBSDF.value,
            typeNode = MSFS_ShaderNodesTypes.shadeNodeBsdfPrincipled.value,
            location = (1000.0, 0.0),
            hidden = False
        )
        self.link(principledBSDF.outputs[0], nodeOutputMaterial.inputs[0])
        self.makeOpaque()

    def createNodetree(self):
        nodeOutputMaterial = self.addNode(
            name = MSFS_ShaderNodes.ShaderOutputMaterial.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeOutputMaterial.value,
            location = (1500.0, 625.0),
            hidden = False
        )

        principledBSDF = self.addNode(
            name = MSFS_ShaderNodes.principledBSDF.value,
            typeNode = MSFS_ShaderNodesTypes.shadeNodeBsdfPrincipled.value,
            location = (1250.0, 600.0),
            hidden = False
        )

        if bpy.data.node_groups.get(MSFS_ShaderNodes.glTFSettings.value):
            gltfSettingsNodeTree = bpy.data.node_groups[MSFS_ShaderNodes.glTFSettings.value]
        else:
            gltfSettingsNodeTree = bpy.data.node_groups.new(MSFS_ShaderNodes.glTFSettings.value, MSFS_ShaderNodesTypes.shaderNodeTree.value)
            gltfSettingsNodeTree.nodes.new("NodeGroupInput")
            # 4.0+ now has NodeTreeInterface type no more inputs outputs https://docs.blender.org/api/4.0/bpy.types.NodeTreeInterface.html
            gltfSettingsNodeTree_socket = gltfSettingsNodeTree.interface.new_socket(name="Occlusion", description="", in_out='INPUT', socket_type="NodeSocketFloat")
            gltfSettingsNodeTree_socket.default_value = 1.000

        nodeglTFSettings = self.addNode(
            name = MSFS_ShaderNodes.glTFSettings.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeGroup.value,
            location = (1250.0, -100.0),
            hidden = False
        ) 

        nodeglTFSettings.node_tree = gltfSettingsNodeTree
        self.link(principledBSDF.outputs[0], nodeOutputMaterial.inputs[0])
        self.makeOpaque()
        self.customShaderTree()

    def createMathNode(self, theNodeTree, op, location, label = "Math", value = 0.5):
        node_math = theNodeTree.nodes.new('ShaderNodeMath')
        node_math.operation = op
        node_math.label = label
        node_math.location = location
        node_math.inputs[1].default_value = value
        return node_math

    def createcombineNodeTree(self, name, groupname, location, frame):

        # Combine 
        combineNodeTree = bpy.data.node_groups.new(name, MSFS_ShaderNodesTypes.shaderNodeTree.value)

        combineNodeTree_inputs = combineNodeTree.nodes.new("NodeGroupInput")
        combineNodeTree_inputs.location = (-900, 0)

        # 4.0+ now has NodeTreeInterface type no more inputs outputs https://docs.blender.org/api/4.0/bpy.types.NodeTreeInterface.html
        # does not work in 4.0+
        # combineNodeTree.inputs.new('NodeSocketFloat','in_to_Color')
        # combineNodeTree.inputs.new('NodeSocketFloat','in_to_R')
        # combineNodeTree.inputs.new('NodeSocketFloat','in_to_G')
        # combineNodeTree.inputs.new('NodeSocketFloat','in_to_B')
        combineNodeTree_socket = combineNodeTree.interface.new_socket(name="in_to_Color", description="", in_out='INPUT', socket_type="NodeSocketFloat")
        combineNodeTree_socket = combineNodeTree.interface.new_socket(name="in_to_R", description="", in_out='INPUT', socket_type="NodeSocketFloat")
        combineNodeTree_socket = combineNodeTree.interface.new_socket(name="in_to_G", description="", in_out='INPUT', socket_type="NodeSocketFloat")
        combineNodeTree_socket = combineNodeTree.interface.new_socket(name="in_to_B", description="", in_out='INPUT', socket_type="NodeSocketFloat")
        #combineNodeTree_socket.default_value = 1.000

        # create group output node
        # 4.0+ now has NodeTreeInterface type no more inputs outputs https://docs.blender.org/api/4.0/bpy.types.NodeTreeInterface.html
        # does not work in 4.0+
        combineNodeTreegroup_outputs = combineNodeTree.nodes.new('NodeGroupOutput')
        combineNodeTreegroup_outputs.location = (600, 0)

        # 4.0+ now has NodeTreeInterface type no more inputs outputs https://docs.blender.org/api/4.0/bpy.types.NodeTreeInterface.html
        # does not work in 4.0+
        #combineNodeTree.outputs.new('NodeSocketFloat','out_result')
        #combineNodeTree.outputs[0].default_value = 1.000
        combineNodeTree_socket = combineNodeTree.interface.new_socket(name="out_result", description="", in_out='OUTPUT', socket_type="NodeSocketFloat")
        combineNodeTree_socket.default_value = 1.000

        nodecombineBColorDBColor = self.addNode(
            name = groupname,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeGroup.value,
            location = location,
            frame = frame
        )

        # set the dropdown in the group node
        nodecombineBColorDBColor.node_tree = combineNodeTree

        splitcombineDetailBColorNode = combineNodeTree.nodes.new(MSFS_ShaderNodesTypes.shaderNodeSeparateColor.value)
        splitcombineDetailBColorNode.location = (-700, -200)

        node_mul_r = self.createMathNode(combineNodeTree, op = 'MULTIPLY', location = (100,200), label = 'mul r', value = 0.001)
        node_mul_g = self.createMathNode(combineNodeTree, op = 'MULTIPLY', location = (100,0), label = 'mul g', value = 0.001)
        node_mul_b = self.createMathNode(combineNodeTree, op = 'MULTIPLY', location = (100,-200), label = 'mul b', value = 0.001)

        combcombineDetailBColorNode = combineNodeTree.nodes.new(MSFS_ShaderNodesTypes.shaderNodeCombineColor.value)
        combcombineDetailBColorNode.location = (300, 0)

        # link nodes together
        combineNodeTree.links.new(splitcombineDetailBColorNode.outputs[0], node_mul_r.inputs[0])
        combineNodeTree.links.new(splitcombineDetailBColorNode.outputs[1], node_mul_g.inputs[0])
        combineNodeTree.links.new(splitcombineDetailBColorNode.outputs[2], node_mul_b.inputs[0])
        combineNodeTree.links.new(splitcombineDetailBColorNode.outputs[0], node_mul_r.inputs[1])
        combineNodeTree.links.new(splitcombineDetailBColorNode.outputs[1], node_mul_g.inputs[1])
        combineNodeTree.links.new(splitcombineDetailBColorNode.outputs[2], node_mul_b.inputs[1])
        combineNodeTree.links.new(node_mul_r.outputs[0], combcombineDetailBColorNode.inputs[0])
        combineNodeTree.links.new(node_mul_g.outputs[0], combcombineDetailBColorNode.inputs[1])
        combineNodeTree.links.new(node_mul_b.outputs[0], combcombineDetailBColorNode.inputs[2])

        # link inputs
        combineNodeTree.links.new(combineNodeTree_inputs.outputs['in_to_Color'], splitcombineDetailBColorNode.inputs[0])
        combineNodeTree.links.new(combineNodeTree_inputs.outputs['in_to_R'], node_mul_r.inputs[0])
        combineNodeTree.links.new(combineNodeTree_inputs.outputs['in_to_G'], node_mul_g.inputs[0])
        combineNodeTree.links.new(combineNodeTree_inputs.outputs['in_to_B'], node_mul_b.inputs[0])

        #link output
        combineNodeTree.links.new(combcombineDetailBColorNode.outputs[0], combineNodeTreegroup_outputs.inputs['out_result'])

        return nodecombineBColorDBColor

    def createbiasNodeTree(self, name, groupname, location, frame):
        # group node drop down name

        # Bias 
        biasNodeTree = bpy.data.node_groups.new(name, MSFS_ShaderNodesTypes.shaderNodeTree.value)

        # can I use add node for this group_inputs?
        # these are the nodes inside the group node
        # create group input node
        group_inputs = biasNodeTree.nodes.new("NodeGroupInput")
        group_inputs.location = (-900, 0)

        # 4.0+ now has NodeTreeInterface type no more inputs outputs https://docs.blender.org/api/4.0/bpy.types.NodeTreeInterface.html
        # does not work in 4.0+
        #biasNodeTree.nodetree.inputs.new('NodeSocketFloat','in_to_Value')
        group_inputs_socket = biasNodeTree.interface.new_socket(name="in_to_Value", description="", in_out='INPUT', socket_type="NodeSocketFloat")
        group_inputs_socket.default_value = 1.000   # may not be needed

        # create group output node
        group_outputs = biasNodeTree.nodes.new('NodeGroupOutput')
        group_outputs.location = (600, 0)
        # does not work in 4.0+
        #biasNodeTree.outputs.new('NodeSocketFloat','out_result')
        #biasNodeTree.outputs[0].default_value = 1.000
        group_outputs_socket = biasNodeTree.interface.new_socket(name="out_result", description="", in_out='OUTPUT', socket_type="NodeSocketFloat")
        group_outputs_socket.default_value = 1.000   # may not be needed

        # # create bias R group node
        nodebiasDBColor = self.addNode(
            name = groupname,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeGroup.value,
            location = location,
            frame = frame
        )

        # set the dropdown in the group node
        nodebiasDBColor.node_tree = biasNodeTree

        # make all the math nodes

        node_add_001 = self.createMathNode(biasNodeTree, op = 'ADD', location = (-700,200), label = 'add bias', value = 0.001)
        node_sub_001 = self.createMathNode(biasNodeTree, op = 'SUBTRACT', location = (-700,-200), label = 'sub bias', value = 0.001)
        node_greater = self.createMathNode(biasNodeTree, op = 'GREATER_THAN', location = (-500,400), label = 'greater', value = 0.5)
        node_less = self.createMathNode(biasNodeTree, op = 'LESS_THAN', location = (-500,-400), label = 'less', value = 0.5)
        node_sub_bias_g = self.createMathNode(biasNodeTree, op = 'SUBTRACT', location = (-500,200), label = 'sub bias_g', value = 0.5)
        node_sub_bias_l = self.createMathNode(biasNodeTree, op = 'SUBTRACT', location = (-500,-200), label = 'sub bias_l', value = 0.5)
        node_mul_bias_g = self.createMathNode(biasNodeTree, op = 'MULTIPLY', location = (-100,200), label = 'mul bias_g', value = 0.5)
        node_mul_bias_l = self.createMathNode(biasNodeTree, op = 'MULTIPLY', location = (-100,-200), label = 'mul bias_l', value = 0.5)
        node_add_bias_g = self.createMathNode(biasNodeTree, op = 'ADD', location = (100,200), label = 'add bias_g', value = 0.5)
        node_add_bias_l = self.createMathNode(biasNodeTree, op = 'ADD', location = (100,-200), label = 'add bias_l', value = 0.5)
        node_combadd_bias_l = self.createMathNode(biasNodeTree, op = 'ADD', location = (300,0), label = 'comb add bias', value = 0.5)

        # make all the links

        # link nodes together
        biasNodeTree.links.new(node_add_001.outputs[0], node_greater.inputs[0])
        biasNodeTree.links.new(node_sub_001.outputs[0], node_less.inputs[0])
        biasNodeTree.links.new(node_greater.outputs[0], node_mul_bias_g.inputs[0])
        biasNodeTree.links.new(node_less.outputs[0], node_mul_bias_l.inputs[0])
        biasNodeTree.links.new(node_sub_bias_g.outputs[0], node_mul_bias_g.inputs[1])
        biasNodeTree.links.new(node_sub_bias_l.outputs[0], node_mul_bias_l.inputs[1])
        biasNodeTree.links.new(node_mul_bias_g.outputs[0], node_add_bias_g.inputs[0])
        biasNodeTree.links.new(node_mul_bias_l.outputs[0], node_add_bias_l.inputs[0])
        biasNodeTree.links.new(node_greater.outputs[0], node_add_bias_g.inputs[1])
        biasNodeTree.links.new(node_less.outputs[0], node_add_bias_l.inputs[1])
        biasNodeTree.links.new(node_add_bias_g.outputs[0], node_combadd_bias_l.inputs[0])
        biasNodeTree.links.new(node_add_bias_l.outputs[0], node_combadd_bias_l.inputs[1])

        # link inputs
        biasNodeTree.links.new(group_inputs.outputs['in_to_Value'], node_add_001.inputs[0])
        biasNodeTree.links.new(group_inputs.outputs['in_to_Value'], node_sub_bias_g.inputs[0])
        biasNodeTree.links.new(group_inputs.outputs['in_to_Value'], node_sub_001.inputs[0])
        biasNodeTree.links.new(group_inputs.outputs['in_to_Value'], node_sub_bias_l.inputs[0])

        #link output
        biasNodeTree.links.new(node_combadd_bias_l.outputs[0], group_outputs.inputs['out_result'])

        return nodebiasDBColor


    def createDetailBaseColorFrame(self):
        ## DetailBaseColorFrame                
        detailbasecolorFrame = self.addNode(
            name = MSFS_FrameNodes.detailBaseColorFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.95, 0.25, 0.83)  # 9900B7 needs changing
        )

        # one outside Separate Color node
        splitDetailBColorNode = self.addNode(
            name = MSFS_ShaderNodes.DetailBColorSeparate.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeSeparateColor.value,
            location = (-500, 1100),
            width = 200.0,
            hidden = False,
            frame = detailbasecolorFrame
        )

        # Bias R
        nodeDBColorR = self.createbiasNodeTree(name = MSFS_ShaderNodes.biasRDetailColor.value, groupname = MSFS_GroupNodes.biasDBColorR.value, location = (-200, 1200), frame = detailbasecolorFrame)
        # Bias G
        nodeDBColorG = self.createbiasNodeTree(name = MSFS_ShaderNodes.biasGDetailColor.value, groupname = MSFS_GroupNodes.biasDBColorG.value, location = (-200, 1100), frame = detailbasecolorFrame)
        # Bias B
        nodeDBColorB = self.createbiasNodeTree(name = MSFS_ShaderNodes.biasBDetailColor.value, groupname = MSFS_GroupNodes.biasDBColorB.value, location = (-200, 1000), frame = detailbasecolorFrame)
        # Combiner nodes
        nodecombineBColorDBColor = self.createcombineNodeTree(name = MSFS_ShaderNodes.DetailBColorCombine.value, groupname = MSFS_GroupNodes.combineBColorDBColor.value, location = (200, 1000), frame = detailbasecolorFrame)

        # links for frame
        self.link(splitDetailBColorNode.outputs[0], nodeDBColorR.inputs[0])
        self.link(splitDetailBColorNode.outputs[1], nodeDBColorG.inputs[0])
        self.link(splitDetailBColorNode.outputs[2], nodeDBColorB.inputs[0])
        self.link(nodeDBColorR.outputs[0], nodecombineBColorDBColor.inputs[1])
        self.link(nodeDBColorG.outputs[0], nodecombineBColorDBColor.inputs[2])
        self.link(nodeDBColorB.outputs[0], nodecombineBColorDBColor.inputs[3])
        # get the detailbasecolor texture node - output to nodecombineBColorDBColor input 0
        nodeBaseColorTex = self.getNodeByName(MSFS_ShaderNodes.baseColorTex.value)
        self.link(nodeBaseColorTex.outputs[0], nodecombineBColorDBColor.inputs[0])
        nodeDetailColor = self.getNodeByName(MSFS_ShaderNodes.detailColorTex.value)
        self.link(nodeDetailColor.outputs[0], splitDetailBColorNode.inputs[0])

    def createVertexFrame(self, All = False):
        ## Vertex Frame                
        vertexFrame = self.addNode(
            name = MSFS_FrameNodes.vertexFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.65, 0.0, 0.73)  # 9900B7 needs changing
        )

        # principledBSDFVertex = self.addNode(
            # name = MSFS_ShaderNodes.principledBSDFVertex.value,
            # typeNode = MSFS_ShaderNodesTypes.shadeNodeBsdfPrincipled.value,
            # location = (750.0, 1000.0),
            # hidden = False,
            # frame = vertexFrame
        # )

        if All:
            splitVertexColorNode = self.addNode(
                name = MSFS_ShaderNodes.vertexcolorSeparate.value,
                typeNode = MSFS_ShaderNodesTypes.shaderNodeSeparateColor.value,
                location = (200.0, 1000.0),
                width = 200.0,
                hidden = False,
                frame = vertexFrame
            )

        if All:
            combineVertexColorNode = self.addNode(
                name = MSFS_ShaderNodes.vertexcolorCombine.value,
                typeNode = MSFS_ShaderNodesTypes.shaderNodeCombineColor.value,
                location = (500.0, 1000.0),
                width = 200.0,
                hidden = False,
                frame = vertexFrame
            )

        combineVertexAlphaNode = self.addNode(
            name = MSFS_ShaderNodes.vertexalphaCombine.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeCombineColor.value,
            location = (500.0, 800.0) if All else (500.0, 1000.0),
            mode = "HSV",
            width = 200.0,
            hidden = False,
            frame = vertexFrame
        )

        vertexColorNode = self.getNodeByName(MSFS_ShaderNodes.vertexColor.value)

        if All:
            self.link(vertexColorNode.outputs[0], splitVertexColorNode.inputs[0])
        if All:
            self.link(splitVertexColorNode.outputs[0], combineVertexColorNode.inputs[0])
        #self.link(vertexColorNode.outputs[1], combineVertexAlphaNode.inputs[0])
        #self.link(vertexColorNode.outputs[1], combineVertexAlphaNode.inputs[1])
        self.link(vertexColorNode.outputs[1], combineVertexAlphaNode.inputs[2])
        # if All:
            # self.link(combineVertexColorNode.outputs[0], principledBSDFVertex.inputs[0])
        # else:
            # self.link(combineVertexAlphaNode.outputs[0], principledBSDFVertex.inputs[0])

    def customShaderTree(self):
        raise NotImplementedError()

    def defaultShadersTree(self):
        principledBSDFNode = self.getNodesByClassName(MSFS_ShaderNodesTypes.shadeNodeBsdfPrincipled.value)[0]
        ################## Textures
        ## Texture Frame                
        textureFrame = self.addNode(
            name = MSFS_FrameNodes.texturesFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.4, 0.5, 0.1)
        )
        ## Base Color Texture 
        # Out[0] : Blend Color Map -> In[1] 
        # Out[1] : Blend Alpha Map -> In[0]
        baseColorTexNode = self.addNode(
            name = MSFS_ShaderNodes.baseColorTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000, 500),
            width = 300.0,
            frame = textureFrame
        )
    
        ## Detail Color Texture
        # In[0] : Multiply UV Offset -> Out[2]
        # Out[0] : Blend Color Map -> In[2] 
        # Out[1] : Blend Alpha Map -> In[1]
        detailColorTexNode = self.addNode(
            name = MSFS_ShaderNodes.detailColorTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000, 450),
            width = 300.0,
            frame = textureFrame
        )
        
        ## Comp Texture
        # Out[0] : Blend Comp Occlusion Metallic Roughness -> In[1]
        compTexNode = self.addNode(
            name = MSFS_ShaderNodes.compTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000, 400),
            width = 300.0,
            frame = textureFrame
        )
        
        ## Detail Comp Texture
        # In[0] : Multiply UV Offset
        # Out[0] : Blend Occlusion
        detailCompTexNode = self.addNode(
            name = MSFS_ShaderNodes.detailCompTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000, 350),
            width = 300.0,
            frame = textureFrame
        )
        
        ## Emissive Texture
        # Out[0] : Emissive Multiplier -> In[1]
        emissiveTexNode = self.addNode(
            name = MSFS_ShaderNodes.emissiveTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000, 300),
            width = 300.0,
            frame = textureFrame
        )
        
        ## Normal Texture
        # Out[0] : Normal Map Sampler -> In[1]
        normalTexNode = self.addNode(
            name = MSFS_ShaderNodes.normalTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000,250),
            width = 300.0,
            frame = textureFrame
        )
        
        ## Detail Normal Texture
        # Out[0] : Detail Normal Map Sampler -> In[1]
        # In[0] : Add UV Offset -> Out[0]
        detailNormalTexNode = self.addNode(
            name = MSFS_ShaderNodes.detailNormalTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000, 200),
            width = 300.0,
            frame = textureFrame
        )
        
        ## Blend Mask
        blendMaskTexNode = self.addNode(
            name = MSFS_ShaderNodes.blendMaskTex.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeTexImage.value,
            location = (-1000, 150),
            width = 300.0,
            frame = textureFrame
        )
        
        ####################################################################
        #### Vertex color
        # Out : Blend Color Map / Blend Occlusion(R) / Blend Normal Map
        vertexColorNode = self.addNode(
            name = MSFS_ShaderNodes.vertexColor.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeVertexColor.value,
            location = (-800.0, 800.0)
        )

        ##### Base Color
        ## Base color frame
        baseColorFrame = self.addNode(
            name = MSFS_FrameNodes.baseColorFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.5, 0.1, 0.0)
        )
        
        ## Blend color map 
        # In: Vertex Color / Base Color Texture / Detail color (RGBA)
        # Out: Base Color Multiplier
        blendColorMapNode = self.addNode(
            name = MSFS_ShaderNodes.blendColorMap.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMixRGB.value if bpy.app.version < (3, 4, 0) else MSFS_ShaderNodesTypes.shaderNodeMix.value,
            data_type = "RGBA",
            blend_type = "MULTIPLY",
            location = (-200, 450.0),
            width = 200.0,
            frame = baseColorFrame
        )
        #Input Factor
        blendColorMapNode.inputs[self.inputs0].default_value = 1.0
        
        # links
        self.link(blendColorMapNode.inputs[self.inputs0], vertexColorNode.outputs[1])
        self.link(blendColorMapNode.inputs[self.inputs1], baseColorTexNode.outputs[0])
        self.link(blendColorMapNode.inputs[self.inputs2], detailColorTexNode.outputs[0])

        ## Base color RGB
        # Out[0] : Base Color Multiplier -> In[0]
        # Out[0] : PrincipledBSDF -> In[0]
        baseColorRGBNode = self.addNode(
            name = MSFS_ShaderNodes.baseColorRGB.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeRGB.value,
            location = (-200.0, 500.0),
            width = 200.0,
            frame = baseColorFrame
        )

        ## Base color A
        # Out[0] : Base Color Multiplier A
        baseColorANode = self.addNode(
            name = MSFS_ShaderNodes.baseColorA.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-200.0, 350.0),
            width = 200.0,
            frame = baseColorFrame
        )
        baseColorANode.outputs[0].default_value = 1
        
        ## Base Color Multiplier
        # In[0] : Vertex Color -> Out[1]
        # In[1] : Base Color RGB
        # In[2] : Blend Color Map
        mulBaseColorRGBNode = self.addNode(
            name = MSFS_ShaderNodes.baseColorMulRGB.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMixRGB.value if bpy.app.version < (3, 4, 0) else MSFS_ShaderNodesTypes.shaderNodeMix.value,
            data_type = "RGBA",
            blend_type = "MULTIPLY",
            location = (50.0, 450.0),
            width = 200.0,
            frame = baseColorFrame
        )
        #Input Factor
        mulBaseColorRGBNode.inputs[self.inputs0].default_value = 1.0
        
        ## Links
        self.link(mulBaseColorRGBNode.inputs[self.inputs0], vertexColorNode.outputs[1])
        self.link(mulBaseColorRGBNode.inputs[self.inputs1], baseColorRGBNode.outputs[0])
        self.link(mulBaseColorRGBNode.inputs[self.inputs2], blendColorMapNode.outputs[0])
        
        ## Blend Alpha Map (Detail alpha operator)
        # In[0] : Alpha Base Color Texture
        # In[1] : Alpha Detail color (RGBA) Texture
        blendAlphaMapNode = self.addNode(
            name = MSFS_ShaderNodes.blendAlphaMap.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMath.value,
            location = (50.0, 400.0),
            width = 200.0,
            frame = baseColorFrame
        )
        #Input Factor
        blendAlphaMapNode.inputs[0].default_value = 1.0
        
        ## Links
        self.link(blendAlphaMapNode.inputs[0], baseColorTexNode.outputs[1])
        self.link(blendAlphaMapNode.inputs[1], detailColorTexNode.outputs[1])
        
        ## Base Color Multiplier A
        # In[1]: Base Color Alpha -> GroupInput[2]
        mulBaseColorANode = self.addNode(
            name = MSFS_ShaderNodes.baseColorMulA.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMath.value,
            operation = "MULTIPLY",
            location = (50.0, 350.0),
            width = 200.0,
            frame = baseColorFrame
        )
        
        ## Links
        self.link(mulBaseColorANode.inputs[0], baseColorANode.outputs[0])
        
        ## Vertex Color Base Color Multiplier
        # In[0] : Free
        # In[1] : Vertex Color -> Out[1]
        # In[2] : Blend Color Map
        VertexColorBaseColorMulNode = self.addNode(
            name = MSFS_ShaderNodes.vertexBaseColorMul.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMixRGB.value if bpy.app.version < (3, 4, 0) else MSFS_ShaderNodesTypes.shaderNodeMix.value,
            data_type = "RGBA",
            blend_type = "MULTIPLY",
            location = (350.0, 450.0),
            width = 220.0,
            frame = baseColorFrame
        )
        #Input Factor
        VertexColorBaseColorMulNode.inputs[self.inputs0].default_value = 0.5

        ## Vertex Color scale
        # Out[0] : Vertex Base Color Multiplier -> In[0] 
        vertexcolorScaleNode = self.addNode(
            name = MSFS_ShaderNodes.vertexcolorScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (50.0, 550.0), 
            frame = baseColorFrame
        )
        vertexcolorScaleNode.outputs[0].default_value = 0.5
        ## Links and default vertex scale
        self.link(VertexColorBaseColorMulNode.inputs[self.inputs0], vertexcolorScaleNode.outputs[0])
        self.link(VertexColorBaseColorMulNode.inputs[self.inputs1], vertexColorNode.outputs[0])

        #### UV MAPS
        ## UV Frame
        uvFrame = self.addNode(
            name = MSFS_FrameNodes.uvFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.3, 0.3, 0.5)
        )
        
        ## UV Map
        # Out[0] : Multiply UV Scale -> In[0]
        uvMapNode = self.addNode(
            name = MSFS_ShaderNodes.uvMap.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeUVMap.value,
            location = (-2000.0, 500.0),
            frame = uvFrame
        )

        ## Detail UV scale
        # Out[0] : Combine UV Scale -> In[0][1][2]
        detailUVScaleNode = self.addNode(
            name = MSFS_ShaderNodes.detailUVScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-2000.0, 400.0),
            frame = uvFrame
        )
        
        ## Detail UV Offset U
        # Out[0] : Combine UV offset -> In[0]
        detailUVOffsetUNode = self.addNode(
            name = MSFS_ShaderNodes.detailUVOffsetU.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-2000.0, 300.0),
            frame = uvFrame
        )
        
        ## Detail UV Offset V
        # Out[0] : Combine UV offset -> In[1]
        detailUVOffsetVNode = self.addNode(
            name = MSFS_ShaderNodes.detailUVOffsetV.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-2000.0, 250.0),
            frame = uvFrame
        )

        ## Combine UV Scale
        # In[0] : Detail UV Scale -> Out[0]
        # In[1] : Detail UV Scale -> Out[0]
        # In[2] : Detail UV Scale -> Out[0]
        combineUVScaleNode = self.addNode(
            name = MSFS_ShaderNodes.combineUVScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeCombineXYZ.value,
            location = (-1750.0, 400.0),
            frame = uvFrame
        )
        
        ## Links
        self.link(combineUVScaleNode.inputs[0], detailUVScaleNode.outputs[0])
        self.link(combineUVScaleNode.inputs[1], detailUVScaleNode.outputs[0])
        self.link(combineUVScaleNode.inputs[2], detailUVScaleNode.outputs[0])
        
        ## Combine UV offset
        # In[0] : Detail UV Offset U -> Out[0]
        # In[1] : Detail UV Offset V -> Out[0]
        combineUVOffsetNode = self.addNode(
            name = MSFS_ShaderNodes.combineUVOffset.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeCombineXYZ.value,
            location = (-1750.0, 300.0),
            frame = uvFrame
        )
        
        ## Links
        self.link(combineUVOffsetNode.inputs[0], detailUVOffsetUNode.outputs[0])
        self.link(combineUVOffsetNode.inputs[1], detailUVOffsetVNode.outputs[0])
        
        ## Multiply UV Scale
        # In[0] : UV Map -> Out[0]
        # In[1] : Combine UV Offset -> Out[0]
        mulUVScaleNode = self.addNode(
            name = MSFS_ShaderNodes.mulUVScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeVectorMath.value,
            operation = "MULTIPLY",
            location = (-1500.0, 400.0),
            frame = uvFrame
        )

        ## Links
        self.link(mulUVScaleNode.inputs[0], uvMapNode.outputs[0])
        self.link(mulUVScaleNode.inputs[1], combineUVScaleNode.outputs[0])
        
        ## Add UV Offset
        # In[0] : Multiply UV Scale -> Out[0]
        # In[1] : Combine UV Offset -> Out[0]
        addUVOffsetNode = self.addNode(
            name = MSFS_ShaderNodes.addUVOffset.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeVectorMath.value,
            operation = "ADD",
            location = (-1250.0, 300.0),
            frame = uvFrame
        )

        ## Links
        self.link(addUVOffsetNode.inputs[0], mulUVScaleNode.outputs[0])
        self.link(addUVOffsetNode.inputs[1], combineUVOffsetNode.outputs[0])
        self.link(detailCompTexNode.inputs[0], addUVOffsetNode.outputs[0])
        self.link(detailColorTexNode.inputs[0], addUVOffsetNode.outputs[0])
        self.link(detailNormalTexNode.inputs[0], addUVOffsetNode.outputs[0])

        ################## 
        ## OMR Frame
        omrFrame = self.addNode(
            name = MSFS_FrameNodes.omrFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.1, 0.4, 0.6)
        )

        ## Multiply Detail OMR
        # In[0] : Detail OMR texture
        # Out[0] : Substract Detail OMR
        multiplyDetailOMR = self.addNode(
            name = MSFS_ShaderNodes.detailOMRMul.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeVectorMath.value,
            operation = "MULTIPLY",
            location = (-500.0, 200.0),
            width = 200.0,
            frame = omrFrame
        )
        multiplyDetailOMR.inputs[1].default_value = (2.0, 2.0, 2.0)

        ## Links
        self.link(detailCompTexNode.outputs[0], multiplyDetailOMR.inputs[0])

        ## Substract Detail OMR
        # In[0] : Multiply Detail OMR
        # Out[0] : Clamp Detail OMR
        subtractDetailOMR = self.addNode(
            name = MSFS_ShaderNodes.detailOMRSubtract.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeVectorMath.value,
            operation = "SUBTRACT",
            location = (-500.0, 150.0),
            width = 200.0,
            frame = omrFrame
        )
        subtractDetailOMR.inputs[1].default_value = (1.0, 1.0, 1.0)

        ## Links
        self.link(multiplyDetailOMR.outputs[0], subtractDetailOMR.inputs[0])

        ## Map to clamp detail OMR
        # In[0] : Substract Detail OMR
        # Out[0] : Add Detail comp
        clampDetailOMR = self.addNode(
            name = MSFS_ShaderNodes.detailOMRClamp.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMapRange.value,
            location = (-500.0, 100.0),
            width = 200.0,
            frame = omrFrame
        )
        clampDetailOMR.data_type = "FLOAT_VECTOR"
        clampDetailOMR.interpolation_type = "LINEAR"

        ## Links
        self.link(subtractDetailOMR.outputs[0], clampDetailOMR.inputs[6]) ## input[6] == "Vector"

        ## Metallic scale
        # Out[0] : Metallic Multiplier -> In[0] 
        # Out[0] : PrincipledBSDF -> In["Metallic"] 
        metallicScaleNode = self.addNode(
            name = MSFS_ShaderNodes.metallicScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-150.0, 100.0),
            frame = omrFrame
        )

        ## Roughness scale
        # Out[0] : Roughness Multiplier -> In[0] 
        # Out[0] : PrincipledBSDF -> In["Roughness"] 
        roughnessScaleNode = self.addNode(
            name = MSFS_ShaderNodes.roughnessScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-150.0, 150.0), 
            frame = omrFrame
        )
        
        ## Blend Detail Operations (OccMetalRough)
        # Add Detail comp 
        # In[0] : Vertex Color -> Out[1]
        # In[1] : Comp Texture -> Out[0]
        # In[2] : Detail Comp Texture -> Out[0]
        blendCompMapNode = self.addNode(
            name = MSFS_ShaderNodes.blendCompMap.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeVectorMath.value,
            operation = "ADD",
            location = (-150.0, 200.0),
            width = 300.0,
            frame = omrFrame
        )
        
        ## Links
        self.link(compTexNode.outputs[0], blendCompMapNode.inputs[0])
        self.link(clampDetailOMR.outputs[1], blendCompMapNode.inputs[1])

        ## Split Occlusion Metallic Roughness
        # In[0] : Blend Comp Map -> Out[0]
        # Out[0] : Occlusion Multiplier -> In[1]
        # Out[1] : Roughness Multiplier -> In[1]
        # Out[2] : Metallic Multiplier -> In[1]
        if(bpy.app.version < (3, 3, 0)):
            splitOccMetalRoughNode = self.addNode(
                name = MSFS_ShaderNodes.compSeparate.value,
                typeNode = MSFS_ShaderNodesTypes.shaderNodeSeparateRGB.value,
                location = (200.0, 200.0),
                width = 200.0,
                frame = omrFrame
            )
        else:
            splitOccMetalRoughNode = self.addNode(
                name = MSFS_ShaderNodes.compSeparate.value,
                typeNode = MSFS_ShaderNodesTypes.shaderNodeSeparateColor.value,
                location = (200.0, 200.0),
                width = 200.0,
                frame = omrFrame
            )
        
        ## Links
        self.link(splitOccMetalRoughNode.inputs[0], blendCompMapNode.outputs[0])
        
        ## Roughness Multiplier
        # In[1] : Split Occ Metal Rough -> Out[1]
        roughnessMulNode = self.addNode(
            name = MSFS_ShaderNodes.roughnessMul.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMath.value,
            operation = "MULTIPLY",
            location = (500.0, 150.0),
            width = 200.0,
            frame = omrFrame
        )
        roughnessMulNode.inputs[0].default_value = 1.0
        
        ## Links
        self.link(roughnessMulNode.inputs[1], splitOccMetalRoughNode.outputs[1])
        
        ## Metallic Multiplier
        # In[1] : Split Occ Metal Rough -> Out[1]
        metallicMulNode = self.addNode(
            name = MSFS_ShaderNodes.metallicMul.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMath.value,
            operation = "MULTIPLY",
            location = (500.0, 100.0),
            width = 200.0,
            frame = omrFrame
        )
        metallicMulNode.inputs[0].default_value = 1.0
        
        ## Links
        self.link(metallicMulNode.inputs[1], splitOccMetalRoughNode.outputs[2])
        
        ################## 
        ## Emissive Frame
        emissiveFrame = self.addNode(
            name = MSFS_FrameNodes.emissiveFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.1, 0.5, 0.3)
        )
        
        ## Emissive Multiplier
        # In[1] : Emissive Texture -> Out[0]
        # In[2] : Emissive Color -> Out[0]
        # Out[0] : Emissive Multiplier Scale -> In[0]
        emissiveMulNode = self.addNode(
            name = MSFS_ShaderNodes.emissiveMul.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMixRGB.value if bpy.app.version < (3, 4, 0) else MSFS_ShaderNodesTypes.shaderNodeMix.value,
            data_type = "RGBA",
            blend_type = "MULTIPLY",
            location = (250.0, -50.0),
            frame = emissiveFrame
        )
        # Factor input
        emissiveMulNode.inputs[self.inputs0].default_value = 1.0

        ## Emissive Color
        emissiveColorNode = self.addNode(
            name = MSFS_ShaderNodes.emissiveColor.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeRGB.value,
            location = (0.0, -50.0),
            frame = emissiveFrame
        )

        ## Emissive Scale
        emissiveScaleNode = self.addNode(
            name = MSFS_ShaderNodes.emissiveScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (0.0, -100.0),
            frame = emissiveFrame
        )
        
        # Links
        self.link(emissiveTexNode.outputs[0], emissiveMulNode.inputs[self.inputs1])
        self.link(emissiveColorNode.outputs[0], principledBSDFNode.inputs[MSFS_PrincipledBSDFInputs.emission.value])
        self.link(emissiveScaleNode.outputs[0], principledBSDFNode.inputs[MSFS_PrincipledBSDFInputs.emissionStrength.value])
        # Input Factor
        emissiveMulNode.inputs[self.inputs0].default_value = 1.0

        ################## 
        ## Normal Frame
        normalFrame = self.addNode(
            name = MSFS_FrameNodes.normalFrame.value,
            typeNode = MSFS_ShaderNodesTypes.nodeFrame.value,
            color = (0.5, 0.25, 0.25)
        )
        
        ## Normal scale
        # Out[0] : Normap Map Sampler -> In[0]
        normalScaleNode = self.addNode(
            name = MSFS_ShaderNodes.normalScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-300.0, -350.0),
            frame = normalFrame
        )
        #Input Factor
        normalScaleNode.outputs[0].default_value = 1.0

        # Fix the normal view by reversing the green channel
        # since blender can only render openGL normal textures
        # make the blue channel = 1.0 in all values - per rhumbaflappy - fsdeveloper.com
        RGBCurvesNode = self.addNode(
            name = MSFS_ShaderNodes.RGBCurves.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeRGBCurve.value,
            location = (-300.0, -400.0),
            frame = normalFrame
        )
        # Green invert
        curveMapping = RGBCurvesNode.mapping.curves[1]
        curveMapping.points[0].location = (0.0, 1.0)
        curveMapping.points[1].location = (1.0, 0.0)
        # Blue 1.0 to 1.0
        curveMapping = RGBCurvesNode.mapping.curves[2]
        curveMapping.points[0].location = (0.0, 1.0)
        curveMapping.points[1].location = (1.0, 1.0)

        ## Normal Map Sampler
        # In[1] : Normal Texture -> Out[0]
        # Out[0] : Blend Normal Map -> In[1]
        normalMapSamplerNode = self.addNode(
            name = MSFS_ShaderNodes.normalMapSampler.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeNormalMap.value,
            location = (0.0, -400.0),
            frame = normalFrame
        )
        
        # Links
        self.link(normalMapSamplerNode.inputs[0], normalScaleNode.outputs[0])
        self.link(normalMapSamplerNode.inputs[1], normalTexNode.outputs[0])
        
        ## Detail Normal Map Sampler
        # In[0] : Detail Normal Scale -> Out[0]
        # In[1] : Detail Normal Texture -> Out[0]
        # Out[0] : Blend Normal Map -> In[2]
        detailNormalMapSamplerNode = self.addNode(
            name = MSFS_ShaderNodes.detailNormalMapSampler.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeNormalMap.value,
            location = (0.0, -450.0),
            frame = normalFrame
        )

        ## Detail Normal Scale
        detailNormalScaleNode = self.addNode(
            name = MSFS_ShaderNodes.detailNormalScale.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeValue.value,
            location = (-300.0, -450.0),
            frame = normalFrame
        )
        
        self.link(detailNormalScaleNode.outputs[0], detailNormalMapSamplerNode.inputs[0])
        self.link(detailNormalTexNode.outputs[0], detailNormalMapSamplerNode.inputs[1])
        
        
        ## Blend Normal Map
        # In[0] : Vertex Color -> Out[1]
        # In[1] : Normal Map Sampler -> Out[0]
        # In[2] : Detail Normal Map Sampler -> Out[0]
        blendNormalMapNode = self.addNode(
            name = MSFS_ShaderNodes.blendNormalMap.value,
            typeNode = MSFS_ShaderNodesTypes.shaderNodeMixRGB.value if bpy.app.version < (3, 4, 0) else MSFS_ShaderNodesTypes.shaderNodeMix.value,
            data_type = "RGBA",
            blend_type = "ADD",
            location = (200.0, -400.0),
            frame = normalFrame
        )
        # Input Factor
        blendNormalMapNode.inputs[self.inputs0].default_value = 1.0
        
        # Links
        self.link(blendNormalMapNode.inputs[self.inputs0], vertexColorNode.outputs[1])
        self.link(blendNormalMapNode.inputs[self.inputs1], normalMapSamplerNode.outputs[0])
        self.link(blendNormalMapNode.inputs[self.inputs2], detailNormalMapSamplerNode.outputs[0])
        
        ## Update links
        self.toggleVertexBlendMapMask(self.material.msfs_blend_mask_texture is None)

        self.updateColorLinks()
        self.updateNormalLinks()
        self.updateCompLinks()
        self.updateEmissiveLinks()

    def setAnisotropicTex(self, tex):
        nodeAnisotropicTex = self.getNodeByName(MSFS_AnisotropicNodes.anisotropicTex.value)
        nodeAnisotropicTex.image = tex

        nodeSeparateAnisotropic = self.getNodeByName(MSFS_AnisotropicNodes.separateAnisotropic.value)
        nodePrincipledBSDF = self.getNodeByName(MSFS_ShaderNodes.principledBSDF.value)

        if nodeAnisotropicTex.image:
            self.link(nodeSeparateAnisotropic.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.anisotropic.value])
            self.link(nodeSeparateAnisotropic.outputs[2], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.anisotropicRotation.value])
        else:
            self.unLinkNodeInput(nodePrincipledBSDF, MSFS_PrincipledBSDFInputs.anisotropic.value)
            self.unLinkNodeInput(nodePrincipledBSDF, MSFS_PrincipledBSDFInputs.anisotropicRotation.value)

    def setBaseColor(self, color):
        nodeBaseColorRGB = self.getNodeByName(MSFS_ShaderNodes.baseColorRGB.value)
        nodeBaseColorA = self.getNodeByName(MSFS_ShaderNodes.baseColorA.value)

        if nodeBaseColorRGB is not None:
            nodeBaseColorRGB.outputs[0].default_value[0] = color[0]
            nodeBaseColorRGB.outputs[0].default_value[1] = color[1]
            nodeBaseColorRGB.outputs[0].default_value[2] = color[2]
            nodeBaseColorRGB.outputs[0].default_value[3] = color[3] # added for Blender 4.0+
            nodeBaseColorA.outputs[0].default_value = color[3]
            self.updateColorLinks()

    def setBaseColorTex(self, tex):
        nodeBaseColorTex = self.getNodeByName(MSFS_ShaderNodes.baseColorTex.value)
        nodeBaseColorTex.image = tex
        self.updateColorLinks()

    def setDetailColorTex(self, tex):
        nodeDetailColor = self.getNodeByName(MSFS_ShaderNodes.detailColorTex.value)
        nodeDetailColor.image = tex
        self.updateColorLinks()

    def setCompTex(self, tex):
        nodeCompTex = self.getNodeByName(MSFS_ShaderNodes.compTex.value)
        nodeCompTex.image = tex
        if tex is not None:
            nodeCompTex.image.colorspace_settings.name = "Non-Color"
        self.updateCompLinks()

    def setDetailCompTex(self, tex):
        nodeDetailCompTex = self.getNodeByName(MSFS_ShaderNodes.detailCompTex.value)
        nodeDetailCompTex.image = tex
        if tex is not None:
            nodeDetailCompTex.image.colorspace_settings.name = "Non-Color"
        self.updateCompLinks()

    def setRoughnessScale(self, scale):
        nodeRoughnessScale = self.getNodeByName(MSFS_ShaderNodes.roughnessScale.value)
        if nodeRoughnessScale is not None:
            nodeRoughnessScale.outputs[0].default_value = scale
            self.updateCompLinks()

    def setMetallicScale(self, scale):
        nodeMetallicScale = self.getNodeByName(MSFS_ShaderNodes.metallicScale.value)
        if nodeMetallicScale is not None:
            nodeMetallicScale.outputs[0].default_value = scale
            self.updateCompLinks()

    def setEmissiveTexture(self, tex):
        nodeEmissiveTex = self.getNodeByName(MSFS_ShaderNodes.emissiveTex.value)
        nodeEmissiveTex.image = tex
        if tex is not None:
            nodeEmissiveTex.image.colorspace_settings.name = "Non-Color"
        self.updateEmissiveLinks()

    def setEmissiveScale(self, scale):
        nodeEmissiveScale = self.getNodeByName(MSFS_ShaderNodes.emissiveScale.value)
        if nodeEmissiveScale is not None:
            nodeEmissiveScale.outputs[0].default_value = scale
            self.updateEmissiveLinks()

    def setVertexColorScale(self, scale):
        nodeVertexColorScale = self.getNodeByName(MSFS_ShaderNodes.vertexcolorScale.value)
        if nodeVertexColorScale is not None:
            nodeVertexColorScale.outputs[0].default_value = scale
            self.updateColorLinks()

    def setEmissiveColor(self, color):
        nodeEmissiveColor = self.getNodeByName(MSFS_ShaderNodes.emissiveColor.value)
        if nodeEmissiveColor is not None:
            emissiveValue = nodeEmissiveColor.outputs[0].default_value
            emissiveValue[0] = color[0]
            emissiveValue[1] = color[1]
            emissiveValue[2] = color[2]
            nodeEmissiveColor.outputs[0].default_value = emissiveValue
            self.updateEmissiveLinks()

    def setNormalScale(self, scale):
        nodeNormalScale = self.getNodeByName(MSFS_ShaderNodes.normalScale.value)
        nodeNormalScale.outputs[0].default_value = scale
        self.updateNormalLinks()

    def setDetailNormalTex(self, tex):
        nodeDetailNormalTex = self.getNodeByName(MSFS_ShaderNodes.detailNormalTex.value)
        nodeDetailNormalTex.image = tex
        if tex is not None:
            nodeDetailNormalTex.image.colorspace_settings.name = "Non-Color"
        self.updateNormalLinks()

    def setNormalTex(self, tex):
        nodeNormalTex = self.getNodeByName(MSFS_ShaderNodes.normalTex.value)
        nodeNormalTex.image = tex
        if tex is not None:
            nodeNormalTex.image.colorspace_settings.name = "Non-Color"
        self.updateNormalLinks()

    def setBlendMaskTex(self, tex):
        nodeBlendMaskTex = self.getNodeByName(MSFS_ShaderNodes.blendMaskTex.value)
        nodeBlendMaskTex.image = tex

    def setUV(self, uvScale, offset_u, offset_v, normalScale):
        nodeDetailUvScale = self.getNodeByName(MSFS_ShaderNodes.detailUVScale.value)
        nodeDetailUvOffsetU = self.getNodeByName(MSFS_ShaderNodes.detailUVOffsetU.value)
        nodeDetailUvOffsetV = self.getNodeByName(MSFS_ShaderNodes.detailUVOffsetV.value)
        nodeDetailNormalScale = self.getNodeByName(MSFS_ShaderNodes.detailNormalScale.value)

        if (nodeDetailUvScale
            and nodeDetailUvOffsetU
            and nodeDetailUvOffsetV
            and nodeDetailNormalScale):

            nodeDetailNormalScale.outputs[0].default_value = normalScale
            nodeDetailUvScale.outputs[0].default_value = uvScale
            nodeDetailUvOffsetU.outputs[0].default_value = offset_u
            nodeDetailUvOffsetV.outputs[0].default_value = offset_v
    
    ##############################################
    def updateColorLinks(self):
        settings = get_prefs()
        # relink nodes
        nodeBaseColorRGB = self.getNodeByName(MSFS_ShaderNodes.baseColorRGB.value)
        nodeBaseColorA = self.getNodeByName(MSFS_ShaderNodes.baseColorA.value)
        nodeBaseColorTex = self.getNodeByName(MSFS_ShaderNodes.baseColorTex.value)
        nodeDetailColorTex = self.getNodeByName(MSFS_ShaderNodes.detailColorTex.value)
        nodeMulBaseColorRGB = self.getNodeByName(MSFS_ShaderNodes.baseColorMulRGB.value)
        nodeMulBaseColorA = self.getNodeByName(MSFS_ShaderNodes.baseColorMulA.value)
        nodeBlendColorMap = self.getNodeByName(MSFS_ShaderNodes.blendColorMap.value)
        nodeBlendAlphaMap = self.getNodeByName(MSFS_ShaderNodes.blendAlphaMap.value)
        nodePrincipledBSDF = self.getNodeByName(MSFS_ShaderNodes.principledBSDF.value)
        # vertex color nodes - extra
        nodeVertexColorBaseColorRGB = self.getNodeByName(MSFS_ShaderNodes.vertexBaseColorMul.value)
        nodeVertexColor = self.getNodeByName(MSFS_ShaderNodes.vertexColor.value)

        # !!!! input index orders matters for the exporter here
        # textures according to blender docs - https://docs.blender.org/manual/en/3.3/render/shader_nodes/color/mix.html
        self.link(nodeBaseColorTex.outputs[0], nodeBlendColorMap.inputs[self.inputs1])
        self.link(nodeDetailColorTex.outputs[0], nodeBlendColorMap.inputs[self.inputs2])
        self.link(nodeBlendColorMap.outputs[self.outputs0], nodeMulBaseColorRGB.inputs[self.inputs2])
        self.link(nodeBaseColorTex.outputs[1], nodeBlendAlphaMap.inputs[0])
        self.link(nodeDetailColorTex.outputs[1], nodeBlendAlphaMap.inputs[1])
        self.link(nodeBaseColorA.outputs[0], nodeMulBaseColorA.inputs[1])
        self.link(nodeBaseColorRGB.outputs[0], nodeMulBaseColorRGB.inputs[self.inputs1])
        # vertex color nodes - extra
        if nodeVertexColorBaseColorRGB is not None and settings.export_vertexcolor_project:
            self.link(nodeVertexColor.outputs[0], nodeVertexColorBaseColorRGB.inputs[self.inputs2])
            self.link(nodeVertexColorBaseColorRGB.outputs[self.outputs0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])

        # no tex
        if not nodeBaseColorTex.image and not nodeDetailColorTex.image:
            # vertex color nodes - extra
            if nodeVertexColorBaseColorRGB is not None and settings.export_vertexcolor_project:
                self.link(nodeBaseColorRGB.outputs[0], nodeVertexColorBaseColorRGB.inputs[self.inputs1])
            else:
                self.link(nodeBaseColorRGB.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])
            self.link(nodeBaseColorA.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.alpha.value])

        # has basecolor - no detailColor
        elif nodeBaseColorTex.image and not nodeDetailColorTex.image:
            nodeBlendColorMap.blend_type = "ADD"
            # moved to if below
            #self.link(nodeMulBaseColorRGB.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])
            self.link(nodeBaseColorTex.outputs[1], nodeMulBaseColorA.inputs[0])
            self.link(nodeMulBaseColorA.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.alpha.value])
            if nodeVertexColorBaseColorRGB is not None and settings.export_vertexcolor_project:
                self.link(nodeVertexColorBaseColorRGB.inputs[self.inputs1], nodeMulBaseColorRGB.outputs[self.outputs0])
            else:
                self.link(nodeMulBaseColorRGB.outputs[self.outputs0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])
            # for some reason PBR Painter texture that are baked will set the node image to Linear.Rec709 and channelpacked alpha_mode B4.2+
            nodeBaseColorTex.image.alpha_mode = "STRAIGHT"
            nodeBaseColorTex.image.colorspace_settings.name = "sRGB"

        # no basecolor - has detailColor - Is this a thing????
        # Blender 4.0+ issue with finding a texture here on alpha channel - puts DetailColor in BaseColor slot also along with ASOBO extension
        elif not nodeBaseColorTex.image and nodeDetailColorTex.image:
            nodeBlendColorMap.blend_type = "ADD"
            # moved to if below
            #self.link(nodeMulBaseColorRGB.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])
            # Alpha links
            self.link(nodeDetailColorTex.outputs[1],nodeMulBaseColorA.inputs[0])
            self.link(nodeMulBaseColorA.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.alpha.value])
            if nodeVertexColorBaseColorRGB is not None and settings.export_vertexcolor_project:
                self.link(nodeVertexColorBaseColorRGB.inputs[self.inputs1], nodeMulBaseColorRGB.outputs[self.outputs0])
            else:
                self.link(nodeMulBaseColorRGB.outputs[self.outputs0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])
            nodeDetailColorTex.image.alpha_mode = "STRAIGHT"
            nodeDetailColorTex.image.colorspace_settings.name = "sRGB"

        # has both tex
        else:
            nodeBlendColorMap.blend_type = "MULTIPLY"
            # moved to if below
            #self.link(nodeMulBaseColorRGB.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])
            nodeMulBaseColorRGB.blend_type = "MULTIPLY"
            self.link(nodeBlendAlphaMap.outputs[0], nodeMulBaseColorA.inputs[0])
            if nodeVertexColorBaseColorRGB is not None and settings.export_vertexcolor_project:
                self.link(nodeVertexColorBaseColorRGB.inputs[self.inputs1], nodeMulBaseColorRGB.outputs[self.outputs0])
            else:
                self.link(nodeMulBaseColorRGB.outputs[self.outputs0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.baseColor.value])
            nodeBaseColorTex.image.alpha_mode = "STRAIGHT"
            nodeDetailColorTex.image.alpha_mode = "STRAIGHT"
            nodeBaseColorTex.image.colorspace_settings.name = "sRGB"
            nodeDetailColorTex.image.colorspace_settings.name = "sRGB"

    def updateNormalLinks(self):
        nodeNormalTex = self.getNodeByName(MSFS_ShaderNodes.normalTex.value)
        nodeDetailNormalTex = self.getNodeByName(MSFS_ShaderNodes.detailNormalTex.value)
        nodeNormalMapSampler = self.getNodeByName(MSFS_ShaderNodes.normalMapSampler.value)
        nodeRGBCurves = self.getNodeByName(MSFS_ShaderNodes.RGBCurves.value)
        nodeDetailNormalMapSampler = self.getNodeByName(MSFS_ShaderNodes.detailNormalMapSampler.value)
        nodeBlendNormalMap = self.getNodeByName(MSFS_ShaderNodes.blendNormalMap.value)
        nodeDetailNormalScale = self.getNodeByName(MSFS_ShaderNodes.detailNormalScale.value)
        nodePrincipledBSDF = self.getNodeByName(MSFS_ShaderNodes.principledBSDF.value)

        # Normal
        self.link(nodeNormalTex.outputs[0], nodeRGBCurves.inputs[1])
        self.link(nodeRGBCurves.outputs[0], nodeNormalMapSampler.inputs[1])
        self.link(nodeNormalMapSampler.outputs[0], nodeBlendNormalMap.inputs[self.inputs1])
        self.link(nodeDetailNormalMapSampler.outputs[0], nodeBlendNormalMap.inputs[self.inputs2])
        self.link(nodeDetailNormalScale.outputs[0], nodeDetailNormalMapSampler.inputs[0])
        self.link(nodeDetailNormalTex.outputs[0], nodeDetailNormalMapSampler.inputs[1])

        if nodeNormalTex.image and not nodeDetailNormalTex.image:
            self.link(nodeNormalMapSampler.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.normal.value])
        elif nodeNormalTex.image and nodeDetailNormalTex.image:
            self.link(nodeBlendNormalMap.outputs[self.outputs0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.normal.value])
        elif not nodeNormalTex.image and nodeDetailNormalTex.image:
            # added by ron - discussion with ASOBO says that a Normal texture is needed with the icing normal - but default aircraft not the case.
            self.link(nodeBlendNormalMap.outputs[self.outputs0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.normal.value])
        else:
            self.unLinkNodeInput(nodePrincipledBSDF, MSFS_PrincipledBSDFInputs.normal.value)

    def updateEmissiveLinks(self):
        nodeEmissiveTex = self.getNodeByName(MSFS_ShaderNodes.emissiveTex.value)
        nodeEmissiveScale = self.getNodeByName(MSFS_ShaderNodes.emissiveScale.value)
        nodeEmissiveColor = self.getNodeByName(MSFS_ShaderNodes.emissiveColor.value)
        nodeMulEmissive = self.getNodeByName(MSFS_ShaderNodes.emissiveMul.value)
        nodePrincipledBSDF = self.getNodeByName(MSFS_ShaderNodes.principledBSDF.value)

        # emissive
        if nodeEmissiveTex.image:
            self.link(nodeEmissiveScale.outputs[0], nodeMulEmissive.inputs[0])
            # was inputs2 then 1 chenged to agree with ASOBO
            self.link(nodeEmissiveColor.outputs[0], nodeMulEmissive.inputs[self.inputs1])
            self.link(nodeEmissiveTex.outputs[0], nodeMulEmissive.inputs[self.inputs2])
            self.link(nodeMulEmissive.outputs[self.outputs0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.emission.value])
        else:
            self.link(nodeEmissiveColor.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.emission.value])
            self.unLinkNodeInput(nodeMulEmissive, 0)
            self.unLinkNodeInput(nodeMulEmissive, 1)

        self.link(nodeEmissiveScale.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.emissionStrength.value])

    def updateCompLinks(self):
        nodeCompTex = self.getNodeByName(MSFS_ShaderNodes.compTex.value)
        nodeDetailCompTex = self.getNodeByName(MSFS_ShaderNodes.detailCompTex.value)
        nodeRoughnessScale = self.getNodeByName(MSFS_ShaderNodes.roughnessScale.value)
        nodeMetallicScale = self.getNodeByName(MSFS_ShaderNodes.metallicScale.value)
        nodeBlendCompMap = self.getNodeByName(MSFS_ShaderNodes.blendCompMap.value)
        nodeSeparateComp = self.getNodeByName(MSFS_ShaderNodes.compSeparate.value)
        nodeMulMetallic = self.getNodeByName(MSFS_ShaderNodes.metallicMul.value)
        nodeMulRoughness = self.getNodeByName(MSFS_ShaderNodes.roughnessMul.value)
        nodeGltfSettings = self.getNodeByName(MSFS_ShaderNodes.glTFSettings.value)
        nodePrincipledBSDF = self.getNodeByName(MSFS_ShaderNodes.principledBSDF.value)

        # occlMetalRough
        self.link(nodeBlendCompMap.outputs[0], nodeSeparateComp.inputs[0])
        self.link(nodeMetallicScale.outputs[0], nodeMulMetallic.inputs[0])
        self.link(nodeRoughnessScale.outputs[0], nodeMulRoughness.inputs[0])
        self.link(nodeSeparateComp.outputs[1], nodeMulRoughness.inputs[1])
        self.link(nodeSeparateComp.outputs[2], nodeMulMetallic.inputs[1])

        if not nodeCompTex.image and not nodeDetailCompTex.image:
            self.link(nodeRoughnessScale.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.roughness.value])
            self.link(nodeMetallicScale.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.metallic.value])

            self.unLinkNodeInput(nodeGltfSettings, 0)
        #elif nodeCompTex.image and not nodeDetailCompTex.image:
        #    self.link(nodeSeparateComp.inputs[0], nodeCompTex.outputs[0])
        #    self.link(nodeSeparateComp.outputs[0], nodeGltfSettings.inputs[0])
        #    self.link(nodeMulRoughness.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.roughness.value])
        #    self.link(nodeMulMetallic.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.metallic.value])
        else: # nodeCompTex.image or nodeDetailCompTex.image (if we have both images or only one of them)
        #    self.link(nodeBlendCompMap.inputs[0], nodeCompTex.outputs[0])
        #    self.link(nodeClampDetailOMR.outputs[1], nodeSeparateComp.inputs[0])
            self.link(nodeSeparateComp.outputs[0], nodeGltfSettings.inputs[0])
            self.link(nodeMulRoughness.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.roughness.value])
            self.link(nodeMulMetallic.outputs[0], nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.metallic.value])

    def setBlendMode(self, blendMode):
        if blendMode == "BLEND":
            self.makeAlphaBlend()
        elif blendMode == "MASK":
            self.makeMasked()
        elif blendMode == "DITHER":
            self.makeDither()
        else:
            self.makeOpaque()

    def toggleVertexBlendMapMask(self, useVertex=True):
        nodeVertexColor = self.getNodeByName(MSFS_ShaderNodes.vertexColor.value)
        nodeBlendColorMap = self.getNodeByName(MSFS_ShaderNodes.blendColorMap.value)
        nodeBlendNormalMap = self.getNodeByName(MSFS_ShaderNodes.blendNormalMap.value)
        nodeBlendMaskTex = self.getNodeByName(MSFS_ShaderNodes.blendMaskTex.value)
        # vertexcolor mask
        if useVertex:
            self.link(nodeVertexColor.outputs[1], nodeBlendColorMap.inputs[self.inputs0])
            self.link(nodeVertexColor.outputs[1], nodeBlendNormalMap.inputs[0])
        else:
            self.link(nodeBlendMaskTex.outputs[0], nodeBlendColorMap.inputs[self.inputs0])
            self.link(nodeBlendMaskTex.outputs[0], nodeBlendNormalMap.inputs[0])

    def makeOpaque(self):
        self.material.blend_method = "OPAQUE"

    def makeMasked(self):
        self.material.blend_method = "CLIP"

    def makeAlphaBlend(self):
        self.material.blend_method = "BLEND"

    def makeDither(self):
        # Since Eevee doesn't provide a dither mode, we'll just use alpha-blend instead.
        # It sucks, but what else is there to do?
        self.material.blend_method = "BLEND"

    #########################################################################
    def addNode(self, name = "", typeNode = "", location = (0.0, 0.0), hidden = True, width = 150.0, frame = None, color = (1.0, 1.0, 1.0), 
                  blend_type = "MIX", operation =  "ADD", data_type = "RGBA", mode = "RGB", clamp_factor = False, clamp_result = True):
        if(self.nodes is not None):
            try:
                node = self.nodes.new(typeNode)
                node.name = name
                node.label = name
                node.location = location
                node.hide = hidden
                node.width = width
                node.parent = frame
                if(typeNode == MSFS_ShaderNodesTypes.nodeFrame.value):
                    node.use_custom_color = True
                    node.color = color
                elif(typeNode == MSFS_ShaderNodesTypes.shaderNodeMixRGB.value or typeNode == MSFS_ShaderNodesTypes.shaderNodeMix.value):
                    node.blend_type = blend_type
                    if(typeNode == MSFS_ShaderNodesTypes.shaderNodeMix.value):
                        node.clamp_factor = clamp_factor
                        node.clamp_result = clamp_result
                        node.data_type = data_type
                elif(typeNode == MSFS_ShaderNodesTypes.shaderNodeMath.value or typeNode == MSFS_ShaderNodesTypes.shaderNodeVectorMath.value):
                    node.operation = operation
                elif(typeNode == MSFS_ShaderNodesTypes.shaderNodeCombineColor.value):
                    node.mode = mode
                return node
            except ValueError:
                print ("[ValueError] Type mismatch affectation.")
        return None
    
    def getNodeByName(self, nodename):
        if self.node_tree.nodes.find(nodename) > -1:
            return self.node_tree.nodes[nodename]
        return None

    def getNodesByClassName(self, className):
        res = []
        for n in  self.node_tree.nodes:
            if n.__class__.__name__ == className:
                res.append(n)
        return res

    def link(self, out_node, in_node):
        self.links.new(out_node, in_node)

    def unLinkNodeInput(self, node, inputIndex):
        for link in node.inputs[inputIndex].links:
            self.node_tree.links.remove(link)

    def set_vertex_color_white(self, mat, tex):
        # now adding a base color triggers vertex color links - they make object black in blender - show texture by making mesh color attribute white
        # add color attribute to mesh for mesh with this material
        # has to be an easier efficient way to get mesh object from material
        if tex is not None:
            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH':
                    for mat_slot in obj.material_slots:
                        if mat_slot.material is not None and mat_slot.material.name == mat.name:
                            if len(obj.data.color_attributes) > 0:
                            #for ca in obj.data.color_attributes:
                                #if ca.name == 'Vertex_Color_White':
                                print("update_base_color_texture - found color attribute - no update")
                                return
                            # None found - make new Vertex_Color_white and assing to mesh
                            # Create a new color attribute - seems to be white already ????
                            print("update_base_color_texture - found mesh object with material base color texture - update", obj, mat.name, mat.msfs_base_color_texture, mat.msfs_detail_color_texture)
                            color_attribute = obj.data.color_attributes.new(
                                                  name='Col',
                                                  #type='BYTE_COLOR',
                                                  type='FLOAT_COLOR',
                                                  domain='CORNER',
                                              )

    def free(self):
        if self.node_tree.users == 1:
            bpy.data.node_groups.remove(self.node_tree, do_unlink=True)

