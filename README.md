## double-letters

Blender generator script for 3D-printable decorative letters.  
One double-letter (.blend and .stl) is made from the intersection of two letters with one of them turned 90°.  
There's a base(board) to set the double-letters down on. The double-letters are true to the font and some are not balanced well and cannot stand on their own.

### Usage

- You need Blender 3+ installed. See [blender.org](https://www.blender.org/)
- Clone this repo, and open the directory in a terminal.
- On Windows, you need to use the full path to the `blender.exe` executable file.
   On Linux, just use `blender`.

**Examples**

|                       Option                       | Syntax |                              Example                               |
| -------------------------------------------------- | ------ | ------------------------------------------------------------------ |
| Font to use                              | -f     | `blender -b -P double-letters.py -- -w LOOK,WALK -f Hack-Bold.ttf` |
| Export .stl files                                  | -e     | `blender -b -P double-letters.py -- -w LOOK,WALK -e`               |
| Size. Default is 50. Let's do small ones in size 15 | -s     | `blender -b -P double-letters.py -- -w LOOK,WALK -s 15`            |

Use `blender -b -P double-letters.py -- -h` for help.

**Output**


- letters_*yourwords*.blend
- letters_*yourwordsletters*.stl (multiple)

Using the export option (-e) will create .stl files. One for the base and one for each double-letter.

The blender file is useful for viewing and post-processing.

### Notes regarding slicing

Since every double-letter comes as a .stl it should be easy to turn them in a way
that is conducive to nice, supports-free, 3D printing.  
For some double-letters supports are still necessary.  
Size 15 and lower models should use brims for proper bed adhesion.
