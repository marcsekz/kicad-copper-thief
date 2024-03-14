# copper_thief
Kicad Copper Thief Pattern Generator

This is a repo for a KiCad Plugin which converts a filled copper zone into an
array of circular dots.  This is a technique used to balance the chemical
plating process. More detail [here](https://electronics.stackexchange.com/questions/85633/what-is-copper-thieving-and-why-use-it)

## Installation:

**Updated for KiCAD 8**
Clone the repository into your local plugin folder
`~/.local/share/kicad/8.0/scripting/plugins/`

*If you are using KiCAD 7, place the plugin here: ~/.local/share/kicad/7.0/scripting/plugins/*


## Usage:

* Draw a zone and leave it unconnected to any net. (This allows the zone to
    create unconnected copper fills). **For now only single-layer zones are supported**
* Set the zone name to "thieving".
* Select the zone
* Click on the Copper Thief icon
* Set the separation and dot diameter parameters, the thieving pattern, and if the zone you created can be deleted by the script
* Go!

## WARNING:
**Currently only single-layer zones are supported, script will crash for multi-layer zones. Draw separate zones for each layer where you want to add dots**


~~Note: Due to [This Bug](https://gitlab.com/kicad/code/kicad/-/issues/7065#note_521206112)
The resultant dots are not shown until the board is saved and the board reloaded.~~ - Fixed in KiCAD 7
