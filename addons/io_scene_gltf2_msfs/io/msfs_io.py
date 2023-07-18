# SPDX-License-Identifier: Apache-2.0
# Copyright 2018-2021 The glTF-Blender-IO authors.

# NOTE: Generated from latest glTF 2.0 JSON Scheme specs using quicktype (https://github.com/quicktype/quicktype)
# command used:
# quicktype --src glTF.schema.json --src-lang schema -t gltf --lang python --python-version 3.5

# TODO: add __slots__ to all classes by extending the generator

# TODO: REMOVE traceback import

# NOTE: this file is modified for addonExtension use. See
# https://github.com/KhronosGroup/glTF-Blender-IO/commit/62ff119d8ffeab48f66e9d2699741407d532fe0f

import sys
import traceback

from io_scene_gltf2.io.com import gltf2_io_debug


def from_int(x):
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_none(x):
    assert x is None
    return x


def from_union(fs, x):
    tracebacks = []
    for f in fs:
        try:
            return f(x)
        except AssertionError:
            _, _, tb = sys.exc_info()
            tracebacks.append(tb)
    for tb in tracebacks:
        traceback.print_tb(tb)  # Fixed format
        tb_info = traceback.extract_tb(tb)
        for tbi in tb_info:
            filename, line, func, text = tbi
            gltf2_io_debug.print_console('ERROR', 'An error occurred on line {} in statement {}'.format(line, text))
    assert False


def from_dict(f, x):
    assert isinstance(x, dict)
    return {k: f(v) for (k, v) in x.items()}


def to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()


def from_list(f, x):
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_float(x):
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_str(x):
    assert isinstance(x, str)
    return x


def from_bool(x):
    assert isinstance(x, bool)
    return x


def to_float(x):
    assert isinstance(x, float)
    return x


def extension_to_dict(obj):
    if hasattr(obj, 'to_list'):
        obj = obj.to_list()
    if hasattr(obj, 'to_dict'):
        obj = obj.to_dict()
    if isinstance(obj, list):
        return [extension_to_dict(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: extension_to_dict(v) for (k, v) in obj.items()}
    return obj

def from_extension(x):
    x = extension_to_dict(x)
    assert isinstance(x, dict)
    return x

def from_extra(x):
    return extension_to_dict(x)

# not needed as there are no properties to this ASOBO_PropertyAnimationChannel target.
class PropertyAnimationChannelTarget:
    """The index of the node and TRS property to target.

    The index of the node and TRS property that an animation channel targets.
    """

    def __init__(self, extensions, extras, node, path):
        self.extensions = extensions
        self.extras = extras
        self.path = path

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        extensions = from_union([lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                                obj.get("extensions"))
        extras = obj.get("extras")
        #node = from_union([from_int, from_none], obj.get("node"))
        path = from_str(obj.get("path"))
        #return AnimationChannelTarget(extensions, extras, node, path)
        return PropertyAnimationChannelTarget(extensions, extras, path)

    def to_dict(self):
        result = {}
        result["extensions"] = from_union([lambda x: from_dict(from_extension, x), from_none],
                                          self.extensions)
        result["extras"] = from_extra(self.extras)
        result["path"] = from_str(self.path)
        return result

# required because of change in target to a string that is a path to a material and sampler is an index.
class ASOBO_PropertyAnimationChannel:
    """Targets an animation's sampler at a node's property."""

    def __init__(self, extensions, extras, sampler, pa_target):
        self.extensions = extensions
        self.extras = extras
        self.sampler = sampler
        self.pa_target = pa_target

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        extensions = from_union([lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                                obj.get("extensions"))
        extras = obj.get("extras")
        sampler = from_int(obj.get("sampler"))
        #target = AnimationChannelTarget.from_dict(obj.get("target"))
        pa_target = from_str(obj.get("pa_target"))
        return PropertyAnimationChannel(extensions, extras, sampler, pa_target)

    def to_dict(self):
        result = {}
        result["extensions"] = from_union([lambda x: from_dict(from_extension, x), from_none],
                                          self.extensions)
        result["extras"] = from_extra(self.extras)
        result["sampler"] = from_int(self.sampler)
        #result["target"] = to_class(AnimationChannelTarget, self.target)
        result["pa_target"] = from_str(self.pa_target)
        return result


# not sure needed
class PropertyAnimationSampler:
    """Combines input and output accessors with an interpolation algorithm to define a keyframe
    graph (but not its target).
    """

    def __init__(self, extensions, extras, input, interpolation, output):
        self.extensions = extensions
        self.extras = extras
        self.input = input
        self.interpolation = interpolation
        self.output = output

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        extensions = from_union([lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                                obj.get("extensions"))
        extras = obj.get("extras")
        input = from_int(obj.get("input"))
        interpolation = from_union([from_str, from_none], obj.get("interpolation"))
        output = from_int(obj.get("output"))
        return PropertyAnimationSampler(extensions, extras, input, interpolation, output)

    def to_dict(self):
        result = {}
        result["extensions"] = from_union([lambda x: from_dict(from_extension, x), from_none],
                                          self.extensions)
        result["extras"] = from_extra(self.extras)
        result["input"] = from_int(self.input)
        result["interpolation"] = from_union([from_str, from_none], self.interpolation)
        result["output"] = from_int(self.output)
        return result

# not sure needed
class PropertyAnimation:
    """A keyframe animation."""

    def __init__(self, channels, extensions, extras, name, samplers):
        self.channels = channels
        self.extensions = extensions
        self.extras = extras
        self.name = name
        self.samplers = samplers

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        channels = from_list(AnimationChannel.from_dict, obj.get("channels"))
        extensions = from_union([lambda x: from_dict(lambda x: from_dict(lambda x: x, x), x), from_none],
                                obj.get("extensions"))
        extras = obj.get("extras")
        name = from_union([from_str, from_none], obj.get("name"))
        samplers = from_list(AnimationSampler.from_dict, obj.get("samplers"))
        return PropertyAnimation(channels, extensions, extras, name, samplers)

    def to_dict(self):
        result = {}
        result["channels"] = from_list(lambda x: to_class(AnimationChannel, x), self.channels)
        result["extensions"] = from_union([lambda x: from_dict(from_extension, x), from_none],
                                          self.extensions)
        result["extras"] = from_extra(self.extras)
        result["name"] = from_union([from_str, from_none], self.name)
        result["samplers"] = from_list(lambda x: to_class(AnimationSampler, x), self.samplers)
        return result
