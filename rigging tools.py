bl_info = {
    "name": "Rigging Tools",
    "description": "Rigging tools that are mostly aimed at rigging exported game rigs.",
    "author": "sauce",
    "version": (0, 0, 9),
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

    my_target_weapon_armature: StringProperty(
        name="",
        description="The armature that gets targeted",
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

    my_target_bone_prefix: StringProperty(
        name="Bone Prefix:",
        description="The prefix that gets added to the target bones",
        default="TRGT-",
        maxlen=1024,
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
        items=[('link_TRANSFORM', "Transform", ""),
               ('link_LOCROT', "Loc/Rot", ""),
               ('link_PARENTS', "Parenting", ""),
               ]
    )

    my_target_link_type: EnumProperty(
        name="Link Type:",
        description="Links using constraints",
        items=[('link_TRANSFORM', "Transform", ""),
               ('link_LOCROT', "Loc/Rot", ""),
               ]
    )

    my_parent_using: EnumProperty(
        name="Parent Using:",
        description="Parents generated bones to each other based on selected order, instead of their hierarchy",
        items=[('parent_HIERARCHY', "Hierarchy", ""),
               ('link_SELECTED', "Selected", ""),
               ]
    )


# ------------------------------------------------------------------------
#    Fuctions
# ------------------------------------------------------------------------

# get selected bones
def get_selected_bones():
    return [obj.name for obj in bpy.context.selected_bones]

# get all bones
def get_all_bones():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='SELECT')
    all_bones = get_selected_bones()
    bpy.ops.armature.select_all(action='DESELECT')
    return all_bones


# bones for drop down
def arma_items(self, context):
    obs = []
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            obs.append((ob.name, ob.name, ""))
    return obs

def arma_upd(self, context):
    self.arma_coll.clear()
    for ob in context.scene.objects:
        if ob.type == 'ARMATURE':
            item = self.arma_coll.add()
            item.name = ob.name

def bone_items(self, context):
    arma = context.scene.objects.get(self.arma)
    if arma is None:
        return
    return [(bone.name, bone.name, "") for bone in arma.data.bones]

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
        active_object = bpy.context.active_object
        bone_list_formatted = []

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')

        # get bones from list
        opened_file = open(mytool.my_bone_list_path, "r")
        bone_list = opened_file.readlines()

        # removes \n
        for i in bone_list:
            bone_list_formatted.append(i.strip())

        # gets all bones
        all_bones = get_all_bones()

        # compares all bones list to bone list and only keeps matching bones
        bone_list_formatted = list(set(bone_list_formatted) & set(all_bones))

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        # delete bones using list
        for i in bone_list_formatted:
            active_object.data.bones[i].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.delete()

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}

class WM_OT_ConnectSelectedBones(Operator):
    """Generates and connects generated bones selected"""
    bl_label = "Connect Selected Bones"
    bl_idname = "wm.connect_selected_bones"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        active_object = bpy.context.active_object

        # get prefix from input
        bone_prefix = mytool.my_new_bone_prefix

        bpy.ops.object.mode_set(mode='EDIT')

        # gets selected bones into list
        selected_bones = get_selected_bones()

        # parent based on selected or hierarchy
        if bpy.context.scene.my_tool.my_parent_using == 'parent_HIERARCHY':
            # duplicates selected bones
            bpy.ops.armature.duplicate(do_flip_names=False)

            # gets dupped bones and adds prefix
            for i in selected_bones:
                bpy.context.object.pose.bones[i + '.001'].name = bone_prefix + i
                bpy.ops.armature.select_all(action='DESELECT')
        else:
            bpy.ops.armature.select_all(action='DESELECT')

            for i in selected_bones:
                bpy.ops.object.mode_set(mode='POSE')
                active_object.data.bones[i].select = True

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.armature.duplicate(do_flip_names=False)

                # gets dupped bones and adds prefix
                bpy.context.object.pose.bones.get(i + '.001').name = bone_prefix + i
                bpy.ops.armature.select_all(action='DESELECT')

        # connect bones
        for i, elem in enumerate(selected_bones):
            try:
                # set 3d cursor to head of next bone in list
                bpy.ops.object.mode_set(mode='POSE')
                active_object.data.bones[str(selected_bones[i+1])].select_head = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.view3d.snap_cursor_to_selected()

                # snaps current bone in list to 3d cusor
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='POSE')
                active_object.data.bones[bone_prefix + elem].select_tail = True
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
                active_object.data.edit_bones[bone_prefix + str(selected_bones[i + 1])].parent = \
                    active_object.data.edit_bones[bone_prefix + elem]

                # make parents connected if user chooses
                if bpy.context.scene.my_tool.my_parent_type == 'parent_CONNECTED':
                    active_object.data.edit_bones[bone_prefix + str(selected_bones[i + 1])].use_connect = True

                bpy.ops.armature.select_all(action='DESELECT')
            except IndexError:
                pass

        # set roll from original bone
        for i in selected_bones:
            try:
                bpy.ops.object.mode_set(mode='POSE')
                bpy.ops.pose.select_all(action='DESELECT')

                # set roll of new bone to original bone
                active_object.data.bones[bone_prefix + i].select = True
                active_object.data.bones[i].select = True
                bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone

                bpy.ops.object.mode_set(mode='EDIT')

                bpy.ops.armature.calculate_roll(type='ACTIVE')

            except IndexError:
                pass

        # links original bones to new bones
        if bpy.context.scene.my_tool.my_link_bones:
            if bpy.context.scene.my_tool.my_link_type == 'link_PARENTS':
                # links bones with parenting
                for i in selected_bones:
                    try:
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='EDIT')

                        # parents original bone to new bone
                        active_object.data.edit_bones[i].parent = \
                            active_object.data.edit_bones[bone_prefix + i]

                        bpy.ops.armature.select_all(action='DESELECT')
                        bpy.ops.object.mode_set(mode='POSE')
                    except IndexError:
                        pass
            elif bpy.context.scene.my_tool.my_link_type == 'link_TRANSFORM':
                # links bones with copy transform
                for i in selected_bones:
                    try:
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')

                        # links bones with copy transform
                        active_object.data.bones[bone_prefix + i].select = True
                        active_object.data.bones[i].select = True
                        bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.object.mode_set(mode='POSE')

                        bpy.ops.pose.constraint_add_with_targets(type='COPY_TRANSFORMS')

                        bpy.ops.pose.select_all(action='DESELECT')
                    except IndexError:
                        pass
            else:
                # links bones with copy loc & rot
                for i in selected_bones:
                    try:
                        bpy.ops.object.mode_set(mode='POSE')
                        bpy.ops.pose.select_all(action='DESELECT')

                        # links bones with copy transform
                        active_object.data.bones[bone_prefix + i].select = True
                        active_object.data.bones[i].select = True
                        bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.object.mode_set(mode='POSE')

                        bpy.ops.pose.constraint_add_with_targets(type='COPY_ROTATION')
                        bpy.ops.pose.constraint_add_with_targets(type='COPY_LOCATION')

                        bpy.ops.pose.select_all(action='DESELECT')
                    except IndexError:
                        pass
        else:
            bpy.ops.object.mode_set(mode='POSE')

        # use deform or not
        if not bpy.context.scene.my_tool.my_use_deform:
            for i in selected_bones:
                active_object.data.bones[bone_prefix + i].use_deform = False
        else:
            for i in selected_bones:
                active_object.data.bones[bone_prefix + i].use_deform = True

        # adds ik to end of chain or not
        if bpy.context.scene.my_tool.my_add_ik_to_chain:
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')

            active_object.data.bones[bone_prefix + selected_bones[-1]].select = True
            bpy.context.object.data.bones.active = bpy.context.object.pose.bones[bone_prefix + selected_bones[-1]].bone
            bpy.ops.pose.ik_add(with_targets=False)
            bpy.ops.pose.select_all(action='DESELECT')

        # elongates last bone or not
        if bpy.context.scene.my_tool.my_elongate_end_of_chain:
            bpy.ops.object.mode_set(mode='EDIT')
            active_object.data.edit_bones[bone_prefix + selected_bones[-1]].length = \
                active_object.data.edit_bones[bone_prefix + selected_bones[-1]].length + mytool.my_elongate_value
            bpy.ops.object.mode_set(mode='POSE')

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        return {'FINISHED'}

class WM_OT_SetParent(Operator):
    """Sets the parent of selected bone"""
    bl_label = "Set Parent"
    bl_idname = "wm.set_parent"

    def execute(self, context):
        active_object = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        selected_bones = get_selected_bones()

        for i in selected_bones:
            bpy.ops.armature.select_all(action='DESELECT')
            active_object.data.edit_bones[i].parent = \
                active_object.data.edit_bones[bpy.context.scene.bone_name]

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}

class WM_OT_ClearParent(Operator):
    """Clears the parent of selected bone"""
    bl_label = "Clear Parent"
    bl_idname = "wm.clear_parent"

    def execute(self, context):
        active_object = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')
        selected_bones = get_selected_bones()

        for i in selected_bones:
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')

            active_object.data.bones[i].select = True
            bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.parent_clear(type='CLEAR')
            bpy.ops.armature.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}

class WM_OT_AddTargetBones(Operator):
    """Adds target bones to selected"""
    bl_label = "Add Target Bones"
    bl_idname = "wm.add_target_bones"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        active_object = bpy.context.active_object

        # get prefix from input
        bone_prefix = mytool.my_target_bone_prefix

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')

        # get all bones
        all_bones = get_all_bones()

        # duplicate bones
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.duplicate(do_flip_names=False)

        # gets dupped bones and adds prefix
        for i in all_bones:
            bpy.context.object.pose.bones[i + '.001'].name = bone_prefix + i
            bpy.ops.armature.select_all(action='DESELECT')

        # adds constraints to original bones to target bones
        if bpy.context.scene.my_tool.my_target_link_type == 'link_TRANSFORM':
            # links bones with copy transform
            for i in all_bones:
                try:
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.pose.select_all(action='DESELECT')

                    # links bones with copy transform
                    active_object.data.bones[bone_prefix + i].select = True
                    active_object.data.bones[i].select = True
                    bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone

                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.object.mode_set(mode='POSE')

                    bpy.ops.pose.constraint_add_with_targets(type='COPY_TRANSFORMS')

                    bpy.ops.pose.select_all(action='DESELECT')

                    # disables use deform on generated target bones
                    active_object.data.bones[bone_prefix + i].use_deform = False
                except IndexError:
                    pass
        else:
            # links bones with copy loc & rot
            for i in all_bones:
                try:
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.pose.select_all(action='DESELECT')

                    # links bones with copy transform
                    active_object.data.bones[bone_prefix + i].select = True
                    active_object.data.bones[i].select = True
                    bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone

                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.object.mode_set(mode='POSE')

                    bpy.ops.pose.constraint_add_with_targets(type='COPY_ROTATION')
                    bpy.ops.pose.constraint_add_with_targets(type='COPY_LOCATION')

                    bpy.ops.pose.select_all(action='DESELECT')

                    # disables use deform on generated target bones
                    active_object.data.bones[bone_prefix + i].use_deform = False
                except IndexError:
                    pass

        bpy.ops.object.mode_set(mode='POSE')

        return {'FINISHED'}

class WM_OT_LinkArmToWeaponArmature(Operator):
    """Links bones in an armature to another with the same name"""
    bl_label = "Link Arm to Weapon Armature"
    bl_idname = "wm.link_arm_to_weapon_armature"

    def execute(self, context):
        active_object = bpy.context.active_object

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # makes base armature active and gets all bones
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.target_arm_armature]
        all_bones_base = get_all_bones()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # makes target armature active and gets all bones
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.target_weapon_armature]
        all_bones_target = get_all_bones()

        # only keeps bones that are in both armatures
        bone_list_formatted = list(set(all_bones_base) & set(all_bones_target))
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.target_arm_armature]

        bpy.ops.object.mode_set(mode='POSE')

        for i in bone_list_formatted:
            try:
                bpy.ops.pose.select_all(action='DESELECT')
                active_object.data.bones[i].select = True
                bpy.context.object.data.bones.active = bpy.context.object.pose.bones[i].bone
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='POSE')

                # adds copy transform
                bpy.ops.pose.constraint_add(type='COPY_TRANSFORMS')

                # sets target and sub target
                bpy.context.object.pose.bones[i].constraints["Copy Transforms"].target = \
                    bpy.data.objects[bpy.context.scene.target_weapon_armature]

                bpy.context.object.pose.bones[i].constraints["Copy Transforms"].subtarget = i
                bpy.ops.pose.select_all(action='DESELECT')
            # if a bone is not found, skips it
            except:
                continue
                
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

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
        row.label(text="Parent By:")
        row.prop(mytool, "my_parent_using", expand=True)

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
        row.prop_search(scene, "bone_name", bpy.context.active_object.data, "bones", text='')

        row = column.row()
        row.operator("wm.clear_parent", icon='X')
        row.operator("wm.set_parent", icon='RESTRICT_INSTANCED_OFF')

        col = column.column()
        col.separator()

        row = column.row()
        row.label(text="Bone Prefix:")
        row.prop(mytool, "my_target_bone_prefix", text="")

        row = column.row()
        row.prop(mytool, "my_target_link_type", expand=True)

        col = column.column()
        col.operator("wm.add_target_bones", icon='ADD', text='Add & Link Target Bones')

        col = column.column()
        col.separator()

        row = column.row()
        row.label(text="Base Armature:")
        row.prop_search(scene, "target_arm_armature", bpy.data, "armatures", text='')

        row = column.row()
        row.label(text="Target Armature:")
        row.prop_search(scene, "target_weapon_armature", bpy.data, "armatures", text='')

        col = column.column()
        col.operator("wm.link_arm_to_weapon_armature", icon='RESTRICT_INSTANCED_OFF', text='Link Bones from Armatures')

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
    WM_OT_AddTargetBones,
    WM_OT_LinkArmToWeaponArmature,
    OBJECT_PT_CustomPanel
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.arma_name = bpy.props.StringProperty()
    bpy.types.Scene.bone_name = bpy.props.StringProperty()
    bpy.types.Scene.target_arm_armature = bpy.props.StringProperty()
    bpy.types.Scene.target_weapon_armature = bpy.props.StringProperty()

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool

    del bpy.types.Scene.arma_name
    del bpy.types.Scene.bone_name
    del bpy.types.Scene.target_arm_armature
    del bpy.types.Scene.target_weapon_armature


if __name__ == "__main__":
    register()
