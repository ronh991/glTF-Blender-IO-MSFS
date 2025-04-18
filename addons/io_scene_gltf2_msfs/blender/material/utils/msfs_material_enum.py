from enum import Enum


class MSFS_MaterialProperties(Enum):
    baseColor = 0, "Base Color"
    emissive = 1, "Emissive"
    metallic = 2, "Metallic"
    roughness = 3, "Roughness"
    alphaCutoff = 4, "Alpha Cutoff"
    normalScale = 5, "Normal Scale"
    detailUVScale = 6, "Detail UV Scale"
    detailUVOffsetU = 7, "Detail UV Offset U"
    detailUVOffsetV = 8, "Detail UV Offset V"
    detailNormalScale = 9, "Detail Normal Scale"
    blendThreshold = 10, "Blend Threshold"
    emissiveMutliplier = 11, "Emissive Mutliplier"
    alphaMode = 12, "Alpha Mode"
    drawOrder = 13, "Draw Order"
    dontCastShadows = 14, "Don't cast shadows"
    doubleSided = 15, "Double Sided"
    dayNightCycle = 16, "Day Night Cycle"
    collisionMaterial = 17, "Collision Material"
    roadCollisionMaterial = 18, "Road Collision Material"
    uvOffsetU = 19, "UV Offset U"
    uvOffsetV = 20, "UV Offset V"
    uvTilingU = 21, "UV Tiling U"
    uvTilingV = 22, "UV Tiling V"
    uvClampU = 23, "UV Clamp U"
    uvClampV = 24, "UV Clamp V"
    usePearlEffect = 25, "Use Pearl Effect"
    pearlColorShift = 26, "Color Shift"
    pearlColorRange = 27, "Color Range"
    pearlColorBrightness = 28, "Color Brightness"
    baseColorTex = 29, "Base Color Texture"
    occlRoughMetalTex = 30, "Occlusion(R) Roughness(G) Metallic(B) Texture"
    normalTex = 31, "Normal Texture"
    emissiveTex = 32, "Emissive Texture"
    detailColorAlphaTex = 33, "Detail Color (RGB) Alpha(A) Texture"
    detailOcclRoughMetalTex = 34, "Detail Occlusion(R) Roughness(G) Metallic(B) Texture"
    detailNormalTex = 35, "Detail Normal Texture"
    blendMaskTex = 36, "Blend Mask Texture"

    def index(self):
        return self.value[0]

    def name(self):
        return self.value[1]

class MSFS_ShaderNodesTypes(Enum):
    shaderNodeGroup = "ShaderNodeGroup"
    shaderNodeTree = "ShaderNodeTree"
    shaderNodeOutputMaterial = "ShaderNodeOutputMaterial"
    nodeFrame = "NodeFrame"
    shaderNodeMix = "ShaderNodeMix" 
    shaderNodeMixRGB = "ShaderNodeMixRGB" 
    nodeGroupOutput = "NodeGroupOutput"
    nodeGroupInput = "NodeGroupInput"
    shadeNodeBsdfPrincipled = "ShaderNodeBsdfPrincipled"
    shaderNodeTexImage = "ShaderNodeTexImage"
    shaderNodeVertexColor = "ShaderNodeVertexColor"
    shaderNodeMath = "ShaderNodeMath"
    shaderNodeUVMap = "ShaderNodeUVMap"
    shaderNodeCombineXYZ = "ShaderNodeCombineXYZ"
    shaderNodeVectorMath = "ShaderNodeVectorMath"
    shaderNodeSeparateRGB = "ShaderNodeSeparateRGB"
    shaderNodeSeparateColor = "ShaderNodeSeparateColor"
    shaderNodeNormalMap = "ShaderNodeNormalMap"
    shaderNodeRGB = "ShaderNodeRGB"
    shaderNodeValue = "ShaderNodeValue"
    shaderNodeRGBCurve = "ShaderNodeRGBCurve"
    shaderNodeMapRange = "ShaderNodeMapRange"
    shaderNodeCombineColor = "ShaderNodeCombineColor"

class MSFS_FrameNodes(Enum):
    baseColorFrame = "Base Color Frame"
    texturesFrame = "Textures Frame"
    uvFrame = "UVs Frame"
    omrFrame = "Occlusion Metallic Roughness Frame"
    emissiveFrame = "Emissive Frame"
    normalFrame = "Normal Frame"
    anisotropicFrame = "Anisotropic Frame"
    parallaxFrame = "Parallax Frame"
    clearcoatFrame = "Clearcoat Frame"
    vertexFrame = "Vertex Color and Alpha Painting"
    detailBaseColorFrame = "DetailBaseColor Frame"

class MSFS_ShaderNodes(Enum):
    glTFSettings = "glTF Settings"
    baseColorTex = "Base Color Texture"
    baseColorRGB = "Base Color RGB"
    baseColorA = "Base Color A"
    alphaCutoff = "Alpha Cutoff"
    baseColorMulRGB = "Base Color Multiplier RGB"
    baseColorMulA = "Base Color Multiplier A"
    normalTex = "Normal Texture"
    compTex = "Occlusion(R) Roughness(G) Metallic(B)"
    compSeparate = "SplitOcclMetalRough"
    roughnessScale = "Roughness Scale"
    metallicScale = "Metallic Scale"
    occlusionMul = "Occlusion Multiplier"
    roughnessMul = "Roughness Multiplier"
    metallicMul = "Metallic Multiplier"
    detailOMRMul = "Multiply detail OcclMetalRough"
    detailOMRSubtract = "Subtract detail OcclMetalRough"
    detailOMRClamp = "Clamp detail OcclMetalRough"
    emissiveTex = "Emissive Texture"
    emissiveColor = "Emissive RGB"
    emissiveScale = "Emissive Scale"
    emissiveMulScale = "Emissive Multiplier Scale"
    RGBCurves = "RGB Curves"
    emissiveMul = "Emissive Multiplier"
    normalScale = "Normal Scale"
    normalMapSampler = "Normal Map Sampler"
    detailColorTex = "Detail Color(RGBA)"
    detailCompTex = "Detail Occlusion(R) Roughness(G) Metallic(B)"
    detailNormalTex = "Detail Normal"
    blendMaskTex = "Blend Mask"
    detailNormalScale = "Detail Normal Scale"
    detailUVScale = "Detail UV Scale"
    detailUVOffsetU = "Detail UV Offset U"
    detailUVOffsetV = "Detail UV Offset V"
    uvMap = "UV Map"
    combineUVScale = "Combine UV Scale"
    combineUVOffset = "Combine UV Offset"
    mulUVScale = "Multiply UV Scale"
    addUVOffset = "Add UV Offset"
    detailNormalMapSampler = "Detail Normal Map Sampler"
    blendNormalMap = "Blend Normal Map"
    blendColorMap = "Blend Color Map"
    blendAlphaMap = "Blend Alpha Map"
    blendCompMap = "Add Occlusion(R) Roughness(G) Metallic(B)"
    vertexColor = "Vertex Color"
    albedoDetailMix = "Albedo Detail Mix"
    behindGlassTex = "Behind Glass"
    clearcoatTex = "Clearcoat"
    clearcoatSeparate = "Clearcoat Separate"
    ShaderOutputMaterial = "Shader Output Material"
    principledBSDF = "Principled BSDF"
    vertexBaseColorMul = "Vertex Base Color Mul"
    principledBSDFVertex = "Principled BSDF Vertex"
    vertexcolorSeparate = "SplitVertexColor"
    vertexalphaSeparate = "SplitVertexAlpha"
    vertexcolorCombine = "CombineVertexColor"
    vertexalphaCombine = "CombineVertexAlpha"
    vertexcolorScale = "Vertex Color Scale"
    biasRDetailColor = "Bias R Detail Color"
    biasGDetailColor = "Bias G Detail Color"
    biasBDetailColor = "Bias B Detail Color"
    DetailBColorSeparate = "Separate Detail and Base Color"
    DetailBColorCombine = "Combine Detail and Base Color"

class MSFS_GroupNodes(Enum):
    combineBColorDBColor = "Combine BaseColor with Detail Color"
    biasDBColorR = "Bias Detail Color R"
    biasDBColorG = "Bias Detail Color G"
    biasDBColorB = "Bias Detail Color B"

class MSFS_AnisotropicNodes(Enum):
    anisotropicTex = "Anisotropic Texture"
    separateAnisotropic = "Separate Anisotropic"

# Blender 4.0 has changed these names
# fix with enum tuples https://jwodder.github.io/kbits/posts/multi-value-enum/
class MSFS_PrincipledBSDFInputs(Enum):
    baseColor = "Base Color"
    subsurfaceColor = "Subsurface Color" # Blender 4 new name
    metallic = "Metallic"
    roughness = "Roughness"
    anisotropic = "Anisotropic"
    anisotropicRotation = "Anisotropic Rotation"
    clearcoat = "Coat Weight" # need new name for blender 4.0
    clearcoatRoughness = "Coat Roughness" # need new name for blender 4.0
    clearcoatNormal = "Coat Normal" # need new name for blender 4.0
    emission = "Emission Color"
    emissionStrength = "Emission Strength"
    alpha = "Alpha"
    normal = "Normal"

class MSFS_MixNodeInputs:
    inputs = [[0, 1, 2], [0, 6, 7]]

class MSFS_MixNodeOutputs:
    outputs = [[0], [2]]

# metallic factor, roughness factor, emissive strength, Alpha - Blender v 4.0+
class MSFS_BSDFNodeInputs:
    inputs = [[6, 9, 20, 21, 19], [1, 2, 27, 4, 26]]
