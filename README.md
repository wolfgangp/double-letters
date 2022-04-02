## double-letters

Generator for 3D printable decorative letters. One model (.blend and .stl) is made of the intersection of two letters, the second turned 90°

### Usage

Examples
    - Export .stl files for letters and base to put them on (along with the .blend file) `blender -b -P double-letters.py -- -e -w GLANCE,CHANCE`
    - Default size is 50. Let's do small ones in size 15:  `blender -b -P double-letters.py -- -w GLANCE,CHANCE -s 15`

### Notes for slicing
Size 15 and lower double-letter models should use brims for proper bed adhesion.
