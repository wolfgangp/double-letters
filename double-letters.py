# This script is an example of how you can run blender from the command line
# (in background mode with no interface) to automate tasks, in this example it
# creates a letter cube objects and a light, then saves them.
# This example also shows how you can parse command line options to scripts.
#
# Example usage
#  blender --background --factory-startup --python $HOME/background_job.py -- \
#          --text="Hello World" \
#          --render="/tmp/hello" \
#          --save="/tmp/hello.blend"
#
# Notice:
# '--factory-startup' is used to avoid the user default settings from
#                     interfering with automated scene generation.
#
# '--' causes blender to ignore all following arguments so python can use them.
#
# See blender --help for details.

import argparse  # to parse options for us and print a nice help message
import sys  # to get command line args
from math import pi, radians, sqrt
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector


def difference_with_offset(ob1, ob2, offset=0.6):
    # based on https://blender.stackexchange.com/questions/143741/boolean-difference-with-offset
    # which is useful in live editing with UI, too.
    bpy.ops.object.select_all(action="DESELECT")
    ob2_copy = ob2.copy()
    ob2_copy.data = ob2.data.copy()
    ob2_copy.name = ob2.name + " foot"
    bpy.context.scene.collection.objects.link(ob2_copy)
    bpy.context.view_layer.objects.active = ob2_copy
    footfinder = ob2_copy.modifiers.new(type="DISPLACE", name="footfinder")
    footfinder.strength = (
        1 + offset / ob2_copy.dimensions.x + 1 + offset / ob2_copy.dimensions.y + 1
    ) / 3
    bpy.ops.object.modifier_apply(modifier=footfinder.name)
    differencer = ob1.modifiers.new(type="BOOLEAN", name="differencer")
    differencer.operand_type = "OBJECT"
    differencer.object = ob2_copy
    differencer.operation = "DIFFERENCE"
    differencer.use_hole_tolerant = True
    bpy.context.view_layer.objects.active = ob1
    bpy.ops.object.modifier_apply(modifier=differencer.name)
    bpy.context.view_layer.objects.active = None
    bpy.data.objects.remove(ob2_copy, do_unlink=True)


def letter_letters(word1, word2, size=50, font_path=None, export_stls=False, depth=0.6):
    # Clear existing objects.
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if font_path.exists():
        font = bpy.data.fonts.load(str(font_path))
    else:
        font = None

    scene = bpy.context.scene
    letters = bpy.data.collections.new("letters")
    scene.collection.children.link(letters)

    bpy.ops.preferences.addon_enable(module="object_print3d_utils")

    num_letters = min(len(word1), len(word2))
    for i in range(num_letters):
        letter1 = word1[i]
        letter2 = word2[i]

        # letter 1
        txt_data = bpy.data.curves.new(name="Letter", type="FONT")
        # Text Object
        txt_ob = bpy.data.objects.new(
            name=f"letters_{letter1}_{letter2}", object_data=txt_data
        )
        # This is necessary to be able select the objects programmatically; for them to be in View Layer "ViewLayer"
        letters.objects.link(txt_ob)  # add the data to the scene as an object
        # txt_ob.parent = structure
        if font:
            txt_data.font = font
        txt_data.size = size
        txt_data.body = letter1  # the body text to the command line arg given
        txt_data.align_x = "CENTER"  # center text
        txt_data.align_y = "CENTER"  # center text

        solid = txt_ob.modifiers.new(type="SOLIDIFY", name="solidtext")
        solid.thickness = size  # extrude to this thickness
        txt_ob.location.y -= size / 2
        txt_ob.rotation_euler.x += pi / 2  # 90°

        txt_ob.select_set(True)
        bpy.context.view_layer.objects.active = txt_ob
        bpy.ops.object.convert(target="MESH")
        # txt_ob.select_set(False)

        # letter 2
        txt_data2 = bpy.data.curves.new(name="Letter", type="FONT")
        txt_ob2 = bpy.data.objects.new(name=f"Letter {letter2}", object_data=txt_data2)
        letters.objects.link(txt_ob2)  # add the data to the scene as an object
        if font:
            txt_data2.font = font
        txt_data2.size = size
        txt_data2.body = letter2  # the body text to the command line arg given
        txt_data2.align_x = "CENTER"  # center text
        txt_data2.align_y = "CENTER"  # center text

        solid = txt_ob2.modifiers.new(type="SOLIDIFY", name="solidtext")
        solid.thickness = size
        txt_ob2.location.x += size / 2
        txt_ob2.rotation_euler.x += pi / 2
        txt_ob2.rotation_euler.z += pi / 2

        txt_ob2.select_set(True)
        bpy.context.view_layer.objects.active = txt_ob2
        bpy.ops.object.convert(target="MESH")

        # intersect
        intersector = txt_ob.modifiers.new(type="BOOLEAN", name="intersector")
        intersector.object = txt_ob2
        intersector.operation = "INTERSECT"
        intersector.use_hole_tolerant = True
        bpy.context.view_layer.objects.active = txt_ob
        bpy.ops.object.modifier_apply(modifier=intersector.name)

        # remove and arrange
        bpy.data.objects.remove(txt_ob2, do_unlink=True)
        txt_ob.location.x += size / 2 * i
        txt_ob.location.y += size / 2 * i

    # construct a base
    bpy.ops.preferences.addon_enable(module="object_print3d_utils")
    base_name = f"lettersbase_{word1}_{word2}"
    base = bpy.data.meshes.new("letters base")
    base_ob = bpy.data.objects.new(name=base_name, object_data=base)
    scene.collection.objects.link(base_ob)

    length = (sqrt(size**2 / 2) * num_letters) / 2
    width = Vector((txt_ob.dimensions.x, txt_ob.dimensions.y, 0)).length / 2
    width *= 1.08

    bm = bmesh.new()
    # bmesh.ops.create_cube(bm, size=base_size)
    bmesh.ops.create_grid(
        bm,
        x_segments=num_letters,
        y_segments=1,
        size=length,
        # matrix=Matrix.Rotation(radians(45), 4, "Z"),
    )
    bmesh.ops.scale(bm, vec=(1.0, width / length, 1.0), verts=bm.verts)
    bmesh.ops.rotate(bm, matrix=Matrix.Rotation(radians(45), 4, "Z"), verts=bm.verts)
    xlettersize = sum(l.dimensions.x for l in letters.objects) / num_letters
    letters_global_verts = [
        o.matrix_world @ v.co for o in letters.objects for v in o.data.vertices
    ]
    zmin = min(letters_global_verts, key=lambda v: v.z)
    mv = (length - xlettersize) / sqrt(2)  # hypotenuse = side * sqrt(2)
    bmesh.ops.translate(bm, vec=(mv, mv, zmin.z), verts=bm.verts)
    bm.to_mesh(base)
    bm.free()
    # make base object active
    bpy.context.view_layer.objects.active = base_ob
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
    # solidify
    solid = base_ob.modifiers.new(type="SOLIDIFY", name="solidbase")
    solid.thickness = size / 15
    solid.offset = 0  # go up and down in equal measure
    solid.use_even_offset = True
    bpy.ops.object.modifier_apply(modifier=solid.name)
    # bevel this
    bevel = base_ob.modifiers.new(type="BEVEL", name="ironingboardbevel")
    bevel.segments = 11
    bevel.offset_type = "PERCENT"
    bevel.width_pct = 16
    bevel.affect = "EDGES"
    # bpy.context.view_layer.objects.active = base_ob
    bpy.ops.object.modifier_apply(modifier=bevel.name)

    for l in letters.objects:
        difference_with_offset(base_ob, l, depth)
        bpy.context.view_layer.objects.active = l
        bpy.ops.mesh.print3d_clean_non_manifold()

    bpy.context.view_layer.objects.active = base_ob
    bpy.ops.mesh.print3d_clean_non_manifold()
    bpy.context.view_layer.objects.active = None

    # Light
    light_data = bpy.data.lights.new("MyLight", "SPOT")
    light_ob = bpy.data.objects.new(name="MySpotLight", object_data=light_data)
    scene.collection.objects.link(light_ob)
    light_data.energy = size * 1000  # size kW light power
    light_data.spot_size = pi / 2
    # light_ob.location = 0.5, -0.5, 0.2  # positive x, negative y
    light_ob.location = length, 0, 0  # positive x, negative y
    aimer = light_ob.constraints.new(type="TRACK_TO")
    aimer.target = letters.objects[len(letters.objects) // 2]
    aimer.track_axis = "TRACK_NEGATIVE_Z"
    aimer.up_axis = "UP_Y"

    """
    # Camera
    cam_data = bpy.data.cameras.new("MyCam")
    cam_ob = bpy.data.objects.new(name="MyCam", object_data=cam_data)
    scene.collection.objects.link(cam_ob)  # instance the camera object in the scene
    scene.camera = cam_ob       # set the active camera
    cam_ob.location = 0.0, 0.0, 10.0
    """

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(
        filepath=str(Path(f"letters_{word1}{word2}.blend").absolute())
    )

    if export_stls:
        print("Exporting .stl's")
        # all together now
        bpy.ops.object.select_all(action="DESELECT")
        for l in letters.objects:
            l.select_set(True)
        bpy.context.scene.collection.objects.get(base_name).select_set(True)

        bpy.ops.export_mesh.stl(
            # filepath=str(Path(f"{l.name}.stl").absolute()),
            filter_glob=str(Path(f"*.stl").absolute()),
            use_selection=True,
            use_mesh_modifiers=True,
            batch_mode="OBJECT",
        )
        bpy.ops.object.select_all(action="DESELECT")


def letter_cubes(
    word1,
    word2,
    size=50,
    font_path=None,
    export_stls=False,
    wall_thickness=0.003,
    letter_thickness=0.003,
):
    # Clear existing objects.
    bpy.ops.wm.read_factory_settings(use_empty=True)

    cube_size = size / 1000

    if font_path.exists():
        font = bpy.data.fonts.load(str(font_path))
    else:
        font = None
    # font_size = cube_size / 1.618
    font_size = (
        cube_size * 1.1
    )  # any bigger and the low strokes of "g" will be outside the cube face.

    scene = bpy.context.scene
    cubes = bpy.data.collections.new("letter cubes")
    scene.collection.children.link(cubes)
    letters = bpy.data.collections.new("letters")
    cubes.children.link(letters)

    num_cubes = min(len(word1), len(word2))
    for i in range(num_cubes):
        letter1 = word1[i]
        letter2 = word2[i]

        # create, cut, then distribute the cubes
        # cube_ob = bpy.ops.mesh.primitive_cube_add(size=0.06)
        cube = bpy.data.meshes.new("letter cube")
        cube_ob = bpy.data.objects.new(name=f"{letter1}_{letter2}", object_data=cube)
        cubes.objects.link(cube_ob)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=cube_size)
        # remove face facing towards -X
        bmesh.ops.delete(
            bm,
            geom=[f for f in bm.faces if all(v.co.x < 1e-6 for v in f.verts)],
            context="FACES",
        )
        bm.to_mesh(cube)
        bm.free()

        bwaller = cube_ob.modifiers.new(type="SOLIDIFY", name="wallthicknesser")
        bwaller.thickness = wall_thickness
        bwaller.use_even_offset = True

        # letter 1 is sticking out
        txt_data = bpy.data.curves.new(name="Letter", type="FONT")
        # Text Object
        txt_ob = bpy.data.objects.new(name=f"Letter {letter1}", object_data=txt_data)
        # Since we may want to move the cubes, it's useful to parent the letter objects to their cube.
        txt_ob.parent = cube_ob
        # This is necessary to be able select the objects programmatically; for them to be in View Layer "ViewLayer"
        letters.objects.link(txt_ob)  # add the data to the scene as an object
        if font:
            txt_data.font = font
        txt_data.size = font_size
        txt_data.body = letter1  # the body text to the command line arg given
        txt_data.align_x = "CENTER"  # center text
        txt_data.align_y = "CENTER"  # center text
        # print(f"{font_size} font size")

        solid = txt_ob.modifiers.new(type="SOLIDIFY", name="solidtext")
        solid.thickness = letter_thickness  # extrude to this thickness
        txt_ob.location.y -= cube_size / 2 + solid.thickness - 1e-6
        txt_ob.rotation_euler.x += pi / 2  # 90°

        # txt_data = txt_ob.to_mesh()
        txt_ob.select_set(True)
        bpy.context.view_layer.objects.active = txt_ob
        bpy.ops.object.convert(target="MESH")

        # booler = bpy.types.BooleanModifier
        b1 = cube_ob.modifiers.new(type="BOOLEAN", name="embossed")
        b1.object = txt_ob
        b1.operation = "UNION"
        # txt_ob.hide_set(True)

        # letter 2 is cut out from the side one over from the embossed side (+90° around Z) of the cube
        # we will use the Convex hull of the letter to make a gaping, (maybe) 3D printable, material-saving,
        # hole behind the immediate surface of the side.

        txt_data = bpy.data.curves.new(name="Letter", type="FONT")
        txt_ob2 = bpy.data.objects.new(name=f"Letter {letter2}", object_data=txt_data)
        txt_ob2.parent = cube_ob
        letters.objects.link(txt_ob2)  # add the data to the scene as an object
        if font:
            txt_data.font = font
        txt_data.size = font_size
        txt_data.body = letter2  # the body text to the command line arg given
        txt_data.align_x = "CENTER"  # center text
        txt_data.align_y = "CENTER"  # center text

        solid = txt_ob2.modifiers.new(type="SOLIDIFY", name="solidtext")
        solid.thickness = cube_size + 1e-5  # hole depth = all the way through
        txt_ob2.location.x += cube_size / 2 + 1e-6
        txt_ob2.rotation_euler.x += pi / 2
        txt_ob2.rotation_euler.z += pi / 2

        txt_ob2.select_set(True)
        bpy.context.view_layer.objects.active = txt_ob2
        bpy.ops.object.convert(target="MESH")

        b2 = cube_ob.modifiers.new(type="BOOLEAN", name="letterhole")
        b2.object = txt_ob2
        b2.use_hole_tolerant = True
        b2.operation = "DIFFERENCE"
        # txt_ob2.hide_set(True)

        cube_ob.location.x += cube_size * i
        cube_ob.location.y += cube_size * i

    letters.hide_viewport = True  # works, but radical

    # Light
    light_data = bpy.data.lights.new("MyLight", "SPOT")
    light_ob = bpy.data.objects.new(name="MyLight", object_data=light_data)
    scene.collection.objects.link(light_ob)
    light_ob.location = 0.5, -0.5, 0.2  # positive x, negative y
    aimer = light_ob.constraints.new(type="TRACK_TO")
    aimer.target = cubes.objects[len(cubes.objects) // 2]
    aimer.track_axis = "TRACK_NEGATIVE_Z"
    aimer.up_axis = "UP_Y"

    """
    # Camera
    cam_data = bpy.data.cameras.new("MyCam")
    cam_ob = bpy.data.objects.new(name="MyCam", object_data=cam_data)
    scene.collection.objects.link(cam_ob)  # instance the camera object in the scene
    scene.camera = cam_ob       # set the active camera
    cam_ob.location = 0.0, 0.0, 10.0
    """
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(
        filepath=str(Path(f"lettercubes_{word1}{word2}.blend").absolute())
    )

    if export_stls:
        print("Exporting .stl's")
        bpy.ops.object.select_all(action="DESELECT")
        for cube in cubes.objects:
            cube.select_set(True)
            bpy.ops.export_mesh.stl(
                filepath=str(Path(f"lettercube_{cube.name}.stl").absolute()),
                use_selection=True,
                use_mesh_modifiers=True,
                batch_mode="OFF",
            )
            cube.select_set(False)


def main():
    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1 :]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
        "Run blender in background mode with this script:"
        "  blender --background --python " + __file__ + " -- [options]\n"
        "try: blender --background --python letters.py -- -w glance,chance\n"
        "try: blender -b -P letters.py -- -f C:\WINDOWS\Fonts\Font.ttf -w g,c"
    )

    parser = argparse.ArgumentParser(description=usage_text)

    # Example utility, add some text and renders or saves it (with options)
    # Possible types are: string, int, long, choice, float and complex.
    parser.add_argument(
        "-w",
        "--words",
        dest="words",
        type=str,
        required=True,
        help="These two words' letters will be used in magnificent intersections. For instance: -w chance,glance",
    )
    parser.add_argument(
        "-s",
        "--size",
        dest="size",
        type=int,
        default=50,
        help="Font size (or cube size in mm if used with --cubes)",
    )
    parser.add_argument(
        "-f",
        "--font",
        dest="font_path",
        type=Path,
        default=Path("Hack-Bold.ttf"),
        help="Font path. A .ttf file should be safe.",
    )
    parser.add_argument(
        "-e",
        "--export",
        dest="export_stls",
        action=argparse.BooleanOptionalAction,
        help="Export .stl files",
    )
    parser.add_argument(
        "-c",
        "--cubes",
        dest="use_cubes",
        action=argparse.BooleanOptionalAction,
        help="Create cubes with letters sticking out and leaving a hole. Instead of this pure letter intersection business.",
    )
    # parser.add_argument(
    #     "-r",
    #     "--render",
    #     dest="render_path",
    #     metavar="FILE",
    #     help="Render an image to the specified path",
    # )

    args = parser.parse_args(argv)  # In this example we won't use the args

    if not argv:
        parser.print_help()
        return

    if not args.words:
        print('Error: --words="word1,word2" argument not given, aborting.')
        parser.print_help()
        return

    word1, word2 = args.words.split(",")
    # Run the appropriate function
    func = letter_cubes if args.use_cubes else letter_letters
    func(
        word1,
        word2,
        size=args.size,
        font_path=args.font_path,
        export_stls=args.export_stls,
    )
    print("letter job finished, exiting")


if __name__ == "__main__":
    main()
