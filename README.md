## double-letters

Generator using Blender for 3D printable decorative letters. One model (.blend and .stl) is made of the intersection of two letters, the second turned 90°

### Usage

You need Blender 3+ installed.
Clone the repo, and open the directory in a terminal.
On Windows, you need to use the full path to the `blender.exe` executable file.
On Linux, just use `blender`.

#### Examples
+----------------------------------------------------+--------------------------------------------------------------------+
| Option                                             | Syntax                                                             |
+----------------------------------------------------+--------------------------------------------------------------------+
| Export .stl files                                  | `blender -b -P double-letters.py -- -w LOOK,WALK -e`               |
| Specify a font to use                              | `blender -b -P double-letters.py -- -w LOOK,WALK -f Hack-Bold.ttf` |
| Default size is 50. Let's do small ones in size 15 | `blender -b -P double-letters.py -- -w LOOK,WALK -s 15`            |
+----------------------------------------------------+--------------------------------------------------------------------+

Use `blender -b -P double-letters.py -- -h` for help.

#### Output

letters_<yourwords>.blend
letters_<yourwordsletters>.stl

The blender file is useful for viewing and post-processing.
Using the export option (-e) will create .stl files. One for the base and one for each double-letter.

### Notes for slicing
Since every double-letter comes as a .stl it should be easy to turn them in a way
that is conducive to easy and nice 3D printing. Sometimes support is still necessary.
Size 15 and lower double-letter models should use brims for proper bed adhesion.
