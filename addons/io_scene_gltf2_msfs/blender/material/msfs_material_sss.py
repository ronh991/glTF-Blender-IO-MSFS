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
from ..msfs_material_function import MSFS_Material
from .utils.msfs_material_enum import (MSFS_PrincipledBSDFInputs,
                                       MSFS_ShaderNodes)


class MSFS_SSS(MSFS_Material):
    def __init__(self, material, buildTree=False):
        super().__init__(material, buildTree)

    def customShaderTree(self):
        super(MSFS_SSS, self).defaultShadersTree()

    def setSSSColor(self, color):
        nodePrincipledBSDF = self.getNodeByName(MSFS_ShaderNodes.principledBSDF.value)  # does not seem to be implemented in Khronos core code - there is no sss or subsurface or sub-surface
        #nodePrincipledBSDF.inputs[MSFS_PrincipledBSDFInputs.subsurfaceColor.value].default_value = color  # seems there is no subsurface color in Blender 4.0+ Weight and radius
