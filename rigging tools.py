bl_info = {
    "name": "Rigging Tools",
    "description": "Rigging tools that are mostly aimed at rigging exported game rigs.",
    "author": "sauce",
    "version": (0, 0, 1),
    "blender": (2, 92, 0),
    "location": "3D View > RIG Tools",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):
    my_bool: BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default=False
    )

    my_link_bones: BoolProperty(
        name="Link Bones",
        description="Links original bones to new bones",
        default=True
    )

    my_use_deform: BoolProperty(
        name="Use Deform",
        description="Use deform on generated bones",
        default=False
    )

    my_add_ik_to_chain: BoolProperty(
        name="Add IK to Chain",
        description="Adds an IK constraint on the end of the chain",
        default=False
    )

    my_elongate_end_of_chain: BoolProperty(
        name="Elongate Bone",
        description="Elongates the bone at the end of the chain",
        default=False
    )

    my_int: IntProperty(
        name="Int Value",
        description="A integer property",
        default=23,
        min=10,
        max=100
    )

    my_float: FloatProperty(
        name="Float Value",
        description="A float property",
        default=23.7,
        min=0.01,
        max=30.0
    )

    my_elongate_value: FloatProperty(
        name="Elongate Value",
        description="How much to elongate the bone by",
        default=1.50,
        min=0.00,
        max=100.00
    )

    my_float_vector: FloatVectorProperty(
        name="Float Vector Value",
        description="Something",
        default=(0.0, 0.0, 0.0),
        min=0.0,  # float
        max=0.1
    )

    my_string: StringProperty(
        name="User Input",
        description=":",
        default="",
        maxlen=1024,
    )

    my_new_bone_prefix: StringProperty(
        name="Bone Prefix:",
        description="The prefix that gets added to the generated bones",
        default="CTRL-",
        maxlen=1024,
    )

    my_set_parent_value: StringProperty(
        name="Parent:",
        description="Set parent of selected bone",
        default="",
        maxlen=1024,
    )

    my_bone_list_path: StringProperty(
        name="Bone List:",
        description="Choose a directory:",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )

    my_enum: EnumProperty(
        name="Dropdown:",
        description="Apply Data to attribute.",
        items=[('OP1', "Option 1", ""),
               ('OP2', "Option 2", ""),
               ('OP3', "Option 3", ""),
               ]
    )

    my_parent_type: EnumProperty(
        name="Parent Type:",
        description="Parent Type for new Bones",
        items=[('parent_OFFSET', "Offset", ""),
               ('parent_CONNECTED', "Connected", ""),
               ]
    )

    my_link_type: EnumProperty(
        name="Link Type:",
        description="Links using parenting or constraints",
        items=[('link_CONSTRAINTS', "Constraints", ""),
               ('link_PARENTS', "Parenting", ""),
               ]
    )


# ------------------------------------------------------------------------
#    Fuctions
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WM_OT_DeleteListedBones(Operator):
    """Delete bones listed in a text file"""
    bl_label = "Delete Listed Bones"
    bl_idname = "wm.delete_listed_bones"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        selection_names = bpy.context.active_object
        bone_list_formatted = []

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')

        # get bones from list
        bone_file_path = mytool.my_bone_list_path
        opened_file = open(bone_file_path, "r")
        bone_list = opened_file.readlines()

        # removes \n
        for i in bone_list:
            bone_list_formatted.append(i.strip())

        # gets all bones
        bpy.ops.armature.select_all(action='SELECT')
        all_bones = [obj.name for obj in bpy.context.selected_bones]

        # compares all bones list to bone list and only keeps matching bones
        bone_list_compared = set(bone_list_formatted) & set(all_bones)
        bone_list_use_formatted = list(bone_list_compared)

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        # delete bones using list
        for i in bone_list_use_formatted:
            selection_names.data.bones[i].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.delete()

        # print the values to the console
        # print("Hello World")
        # print("bool state:", mytool.my_bool)
        # print("int value:", mytool.my_int)
        # print("float value:", mytool.my_float)
        # print("string value:", mytool.my_string)
        # print("enum state:", mytool.my_enum)
        # print("path value:", mytool.my_bone_list_path)

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}

class WM_OT_ConnectSelectedBones(Operator):
    """Generates and connects generated bones selected"""
    bl_label = "Connect Selected Bones"
    bl_idname = "wm.connect_selected_bones"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        selection_names = bpy.context.active_object

        # get prefix from input
        bone_prefix = mytool.my_new_bone_prefix

        bpy.ops.object.mode_set(mode='EDIT')

        # gets selected bones into list
        selected_bones = [obj.name for obj in bpy.context.selected_bones]
        bpy.ops.armature.select_all(action='DESELECT')

        # duplicates bones in list
        for i in selected_bones:
            bpy.ops.object.mode_set(mode='POSE')
            selection_names.data.bones[i].select = True

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.duplicate(do_flip_names=False)

            # removes .001 from dupped bones and adds prefix
            bpy.context.object.pose.bones.get(i + '.001').name = bone_prefix + i
            bpy.ops.armature.select_all(action='DESELECT')

        # connect bones
        for i, elem in enumerate(selected_bones):
            try:
                # set 3d cursor to head of next bone in list
                bpy.ops.object.mode_set(mode='POSE')
                selection_names.data.bones[str(selected_bones[i+1])].select_head = True
                bpy.ops.object.mode_set(mode='EDIT')

                # snaps current bone in list to 3d cusor
                bpy.ops.view3d.snap_cursor_to_selected()
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='POSE')
                selection_names.data.bones[bone_prefix + elem].select_tail = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
                bpy.ops.armature.select_all(action='DESELECT')
            except IndexError:
                pass

        # parent new bones
        for i, elem in enumerate(selected_bones):
            try:
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='EDIT')

                # parents next bone to this bone
                selection_names.data.edit_bones[bone_prefix + str(selected_bones[i + 1])].parent = \
                    selection_names.data.edit_bones[bone_prefix + elem]

                # make parents connected if user chooses
                if bpy.context.scene.my_tool.my_parent_type == 'parent_CONNECTED':
                    selection_names.data.edit_bones[bone_prefix + str(selected_bones[i + 1])].use_connect = True
                else:
                    pass

                bpy.ops.armature.select_all(action='DESELECT')
            except IndexError:
                pass

        # set roll from original bone
        for i, elem in enumerate(selected_bones):
            try:
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='DESELECT')

                # set roll of new bone to original bone
                selection_names.data.bones[bone_prefix + elem].select = True
                selection_names.data.bones[elem].select = True
                bpy.context.object.data.bones.active = bpy.context.object.pose.bones[elem].bone

                bpy.ops.object.mode_set(mode='EDIT')

                bpy.ops.armature.calculate_roll(type='ACTIVE')

            except IndexError:
                pass

        # links original bones to new bones
        if bpy.context.scene.my_tool.my_link_bones:
            if bpy.context.scene.my_tool.my_link_type == 'link_PARENTS':
                # links bones with parenting
                for i, elem in enumerate(selected_bones):
                    try:
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='EDIT')

                        # parents original bone to new bone
                        selection_names.data.edit_bones[elem].parent = \
                            selection_names.data.edit_bones[bone_prefix + elem]

                        bpy.ops.armature.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='POSE')
                    except IndexError:
                        pass
                pass
            else:
                # links bones with constraints
                for i, elem in enumerate(selected_bones):
                    try:
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')

                        # links bones with copy transform
                        selection_names.data.bones[bone_prefix + elem].select = True
                        selection_names.data.bones[elem].select = True
                        bpy.context.object.data.bones.active = bpy.context.object.pose.bones[elem].bone

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.object.mode_set(mode='POSE')

                        bpy.ops.pose.constraint_add_with_targets(type='COPY_TRANSFORMS')

                        bpy.ops.pose.select_all(action='DESELECT')
                    except IndexError:
                        pass
                pass
        else:
            bpy.ops.object.mode_set(mode='POSE')

        # use deform or not
        if not bpy.context.scene.my_tool.my_use_deform:
            for i in selected_bones:
                bpy.ops.pose.select_all(action='DESELECT')
                selection_names.data.bones[bone_prefix + i].select = True
                selection_names.data.bones[bone_prefix + i].use_deform = False
        else:
            for i in selected_bones:
                bpy.ops.pose.select_all(action='DESELECT')
                selection_names.data.bones[bone_prefix + i].select = True
                selection_names.data.bones[bone_prefix + i].use_deform = True

        # adds ik to end of chain or not
        if bpy.context.scene.my_tool.my_add_ik_to_chain:
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')

            selection_names.data.bones[bone_prefix + selected_bones[-1]].select = True
            bpy.context.object.data.bones.active = bpy.context.object.pose.bones[bone_prefix + selected_bones[-1]].bone
            bpy.ops.pose.ik_add(with_targets=False)
            bpy.ops.pose.select_all(action='DESELECT')
        else:
            pass

        # elongates bone or not
        if bpy.context.scene.my_tool.my_elongate_end_of_chain:
            bpy.ops.object.mode_set(mode='EDIT')
            selection_names.data.edit_bones[bone_prefix + selected_bones[-1]].length = \
                selection_names.data.edit_bones[bone_prefix + selected_bones[-1]].length + mytool.my_elongate_value
            bpy.ops.object.mode_set(mode='POSE')
        else:
            pass

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        return {'FINISHED'}

class WM_OT_SetParent(Operator):
    """Sets the parent of selected bone"""
    bl_label = "Set Parent"
    bl_idname = "wm.set_parent"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        selection_names = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        selected_bones = [obj.name for obj in bpy.context.selected_bones]

        for i in selected_bones:
            bpy.ops.armature.select_all(action='DESELECT')
            selection_names.data.edit_bones[i].parent = \
                selection_names.data.edit_bones[mytool.my_set_parent_value]

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}

class WM_OT_ClearParent(Operator):
    """Clears the parent of selected bone"""
    bl_label = "Clear Parent"
    bl_idname = "wm.clear_parent"

    def execute(self, context):
        selection_names = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        selected_bones = [obj.name for obj in bpy.context.selected_bones]

        for i in selected_bones:
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')

            selection_names.data.bones[i].select = True
            bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.parent_clear(type='CLEAR')
            bpy.ops.armature.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "Rigging Tools"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RIG Tools"

    @classmethod
    def poll(self, context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        column = layout.column()

        # layout.prop(mytool, "my_bool")
        # layout.prop(mytool, "my_enum", text="")
        # layout.prop(mytool, "my_int")
        # layout.prop(mytool, "my_float")
        # layout.prop(mytool, "my_float_vector", text="")
        # layout.prop(mytool, "my_string")
        row = column.row()
        row.label(text="Bone List File:")
        row.prop(mytool, "my_bone_list_path", text="")

        col = column.column()
        col.operator("wm.delete_listed_bones", icon='TRASH')

        col.separator()

        col.label(text="Make & Connect Bones:")

        row = column.row()
        row.prop(mytool, "my_parent_type", expand=True)

        row = column.row()
        row.label(text="Bone Prefix:")
        row.prop(mytool, "my_new_bone_prefix", text="")

        col = column.column()
        col.prop(mytool, "my_use_deform")

        col = column.column()
        col.prop(mytool, "my_add_ik_to_chain")

        row = column.row()
        row.prop(mytool, "my_elongate_end_of_chain")

        row = column.row()
        row.prop(mytool, "my_elongate_value")
        row.enabled = bpy.context.scene.my_tool.my_elongate_end_of_chain

        row = column.row()
        row.prop(mytool, "my_link_bones")

        row = column.row()
        row.prop(mytool, "my_link_type", expand=True)
        row.enabled = bpy.context.scene.my_tool.my_link_bones

        col = column.column()
        col.operator("wm.connect_selected_bones", icon='ADD', text='Add & Connect Selected Bones')

        col.separator()

        row = column.row()
        row.label(text="Parent:")
        row.prop(mytool, "my_set_parent_value", text="")

        row = column.row()
        row.operator("wm.clear_parent", icon='X')
        row.operator("wm.set_parent", icon='RESTRICT_INSTANCED_OFF')
        # layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        # layout.separator()


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    WM_OT_DeleteListedBones,
    WM_OT_ConnectSelectedBones,
    WM_OT_SetParent,
    WM_OT_ClearParent,
    OBJECT_PT_CustomPanel
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
