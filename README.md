[![MSFS](misc/Logos/msfs_logo.png)](https://www.flightsimulator.com/)[![ASOBO](misc/Logos/asobo_logo.png)](https://www.asobostudio.com/)[![GS614](misc/Logos/gs614_logo.png)](https://www.gs614.ca/) <img src="misc/Logos/glTF_logo.png" width="180" height="90">

# Unofficial Microsoft Flight Simulator glTF 2.0 Importer and Exporter for Blender

## NOTE:

THIS WILL NOT Work with 4.1.x or earlier - Blender 4.2.x LTS is a large breaking change update.

If you use this unofficial version of the ASOBO exporter, be aware that you will need to or it is highly recommended that you migrate your MSFS materials. They will NOT display with the Migrate Data button.  However this exporter has a number of shader node, shader node link changes and default factor value changes.  These changes will only be utilized if you reselect the MSFS material.  That is, reselect the same MSFS material from the drop down - DO NOT SELECT DISABLED in the drop down.  Please make a backup of your original work before migration.

If you want to go back to using the ASOBO exporter, this may or may not be possible.  First if the blend file is a version higher than what ASOBO uses, there may be issues with animations or other blender data where you will be required to rebuild the object and/or animations.  If ASOBO has released a version that uses a Blender version equal to or higher than what you currently are using here, then it would be easier to migrate the material nodes to the new ASOBO version by re-selecting the MSFS Material Param type in the drop down

## Summary

This repository contains the current version of a non-official Microsoft Flight Simulator Blender Import/Export plugin. The flight sim community has already developed and forked the original project many times, and Asobo's intention is to fully support Blender with the help and contributions of all the developers that have already implemented features in the different unofficial Blender plugins.

:warning: This plugin is a fork of the ASOBO plugin version 1.3.3 - and has the following mods/fixes

v1.6.3.x (Blender 3.3.x and 3.6.x) 
v2.2.7 (Blender 4.2.x LTS Beta and later)

# ASOBO issues and enhancements

  #213 Emissive strength - mod and default values change - max 100

  #214 Parallax - mod bug fixes (should work)

  #220 Projected Mesh invisible in Simulator - not fixed

  #248 Multiple empty animations on export - you must manually checkboxes

  #252 Vertex Color Rainbow -  mod applied - fixed

  #266 Glass and standard render in sim differently - with same parameters. - not fixed

  #269 Comp textures are not being included from saved v292 .blend files - fbw migration added to help fix this

  #279 Addon defaults to a base color value of 0.8 - modified numerous default values.

  #280 Blender Exporting ERROR (Long Code) - core Khronos code issue - not fixed

  #281 Exporter doesn't take collections in account - not fixed

  #284 Current XML are being completely overwritten on export - not fixed

  #289 Color Attributes (Vertex Painting) wrong in shader - mod added

  #290 Add function - To delete all glTf Settings.xxx and reassign to Proper glTf Settings - mod added

  #291 Jetway wheel animation not working - not fixed

  #294 Enhancement - Change RGB Curves to show Blue channel as all 1's (white) - mod added

# Unofficial Version (this version) Issues

  #8 not export emission day night cycle extension - fixed bug introduced

  #11 Base Color not being used in export - fixed - bug introduced

  #12 Forced use of Vertex Color nodes - fixed - added an option in the add-on install - File Preferences 
  default is not checked and no Vertex color nodes will be linked in shader nodes. If checked then Vertex Color
  nodes will be used.

  #13 Vertex Color addon Preferences option - fixed issues

  #14 Unique id errors

  #16 FBW import issues - bad COMP and Emissive texture importing fixed

  #17 Neutral Bone is added by KHronos however their spec allows duplicate bone names, ASOBO extensions do not - code to re name Neutral bones

# Enhancements

  Blender 4.2 has had numerous changes and updates for the Beta - new extensions install for addons is required

  Some default values for Metallic, Roughness, Emissive, Base Color have been reset
  Max emissive strength now 100 (not the same a Emissive Factor)
  Vertex Color added to exported data and now shows in Blender - Shader nodes added with links
  Normal - Blue Channel set to default to 1 (White)

  Added more functionality to the migration of materials. If you import a glTF file using the fbw (Fly-By-Wire) importer, you will get material nodes that are not one for one in synch with the ASOBO exporter and a Pre-Migration will be required. The fbw materials will now carry over it's data to the new ASOBO shaders with better accuracy.  You will still need to monitor the migration of those materials.

>Asobo would especially like to thank the following people:
>Vitus of [Wing42](https://wing42.com/), [tml1024](https://github.com/tml1024), [ronh991](https://github.com/ronh991), [pepperoni505](https://github.com/pepperoni505) of [FlyByWire](https://flybywiresim.com/)

:warning: This plugin cannot import glTF files that have been built into a Microsoft Flight Simulator package through the Sim's Package Builder.

:warning: This plugin is NOT compatible with the legacy exporter developed for FSX and P3D and MSFS.  Remove these plugin (Prefered) or disabled these plugins.

:warning: The version 1.6.2.x is only compatible with Blender 3.3.x LTS up to 3.6.x LTS. Other versions are not supported.

:warning: The version 2.2.x is only compatible with Blender 4.2.x LTS. Other versions are not supported.

*******

# Table of Contents

- [How to Install the Add-on](#how-to-install-the-add-on)
  - [How to Install the ASOBO Blender MSFS Importer/Exporter using Blender:](#how-to-install-the-asobo-blender-msfs-importerexporter-using-blender)
  - [How to Install the ASOBO Blender MSFS exporter by Copy/Paste to AppData](#how-to-install-the-asobo-blender-msfs-exporter-by-copypaste-to-appdata)
- [How to remove the Add-on](#how-to-remove-the-add-on)
- [Documentation](#documentation)
- [Notes On Shadertree](#notes-on-shadertree)

*******

# How to Install the Add-on

There are two ways to install the MSFS Blender exporter. Either using the Edit Preferences Menu and Install tab, or copy/paste the addon files to your %APPDATA% folder. Installation steps are explained down bellow :

## How to Install the ASOBO Blender MSFS Importer/Exporter using Blender:

1. Go to the Releases section of the https://github.com/ronh991/glTF-Blender-IO-MSFS/releases repository. Then download the zip file `io_scene_gltf2_msfs_for36.zip` for Blender 3.6.x or the pre-release version `io_scene_gltf2_msfs_for40.zip` for Blender 4.0.x.

![Download Release](misc/Install/Download_rel.png)

2. Open Blender and go to : Edit > Preferences.

 ![Edit Preferences - Add](misc/Install/Edit_Pref.png)

3. Go to Add-ons and click on Install an add-on. This will bring up a file dialog, where you navigate to the folder where you have your `io_scene_gltf2_msfs.zip` downloaded file.

4. Select the `io_scene_gltf2_msfs.zip` file.  And click on the Install Add-on button.

 ![Edit Preferences - Install](misc/Install/Edit_Pref_install.png)

5. Enable the Add-on by clicking on the checkbox.

 ![Edit Preferences - Enable](misc/Install/Enable_checkbox_addon.png)

## How to Install the ASOBO Blender msfs exporter by Copy/Paste to AppData

1. Close Blender if you have it open.

2. Go to the Releases section of the https://github.com/ronh991/glTF-Blender-IO-MSFS/releases repository. Then download the zip file `io_scene_gltf2_msfs_for36.zip` for Blender 3.6.x or the pre-release version `io_scene_gltf2_msfs_for40.zip` for Blender 4.0.x.

3. Decompress the contents of the file to a temporary location.

4. Select the `io_scene_gltf2_msfs` folder then copy it to the clipboard (Ctrl + "C").

5. Now browse to the Blender `addons` folder, which - by default - can be found in the following locations:
   - **Windows**: This will usually be in `%AppData%\Blender Foundation\Blender\<blender-version>\scripts\addons\`.
   - **Mac OS X**: This will be in your Library (Press the *Option* key when in Finder's `Go` menu to open your Library folder): `\Users\<username>\Library\Application Support\Blender\<blender-version>\scripts\addons\`.

6. Paste the `io_scene_gltf2_msfs` into the Blender `addons` folder (Ctrl + V).

After completing the process outlined above, you will need to start Blender and then activate the plugin. Activation is done from Edit > Preferences, as shown in the image below:

**NOTE** : You may need to restart Blender again after activating the plugin for all the options to be visible in the IDE.

![Edit Preferences - Enable](misc/Install/Enable_checkbox_addon.png)

# How to remove the Add-on

1. If you previously installed the Microsoft Flight Simulator glTF Extensions Add-on, Remove/Delete the older version using the Blender Edit > Preferences Menu. 

![Edit Preferences](misc/Install/Edit_Pref.png)

2. Select the Add-ons tab. Search for the `Microsoft Flight Simulator glTF Extension` Importer/Exporter add-on in the search box. Delete the `Import-Export: Microsoft Flight Simulator gltf Extension` using the `Remove` button.
:warning: DO NOT DELETE THE `Import-Export: gltf 2.0 format` Add-on.

![Search Remove](misc/Install/Edit_Pref_search_rem.png)

3. You should now have only the `Import-Export: gltf 2.0 format` addon left.

4. Close the Blender program.

# Documentation
If you want to learn how to use this add-on you can refer to the documentation page here :
[Documentation for Microsoft Flight Simulator glTF 2.0 Importer and Exporter for Blender](./Documentation/Documentation.md)

You can also have a look at the SDK documentation of the plugin here : https://docs.flightsimulator.com/html/Asset_Creation/Blender_Plugin/The_Blender_Plugin.htm

# Notes On Shadertree

Shadertree modification directly impacts the result of the exporter. 
The properties of your material must only be modified through the `MSFS Material Panel` section.

:warning: If you work with an MSFS Material you should never modify the shader tree manually.
