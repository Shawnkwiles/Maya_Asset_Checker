

import os
import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtUiTools, QtCore, QtGui, QtWidgets
from functools import partial # optional, for passing args during signal function calls
import sys

class MayaAssetChecker(QtWidgets.QWidget):
    """
    Create a default tool window.
    """
    window = None
    
    def __init__(self, parent = None):
        """
        Initialize class.
        """
        super(MayaAssetChecker, self).__init__(parent = parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.widgetPath = ('H:\\ART\\Tech Art\\My_maya_asset_checker\\Maya_AssetChecker_QTUI.ui')
        self.widget = QtUiTools.QUiLoader().load(self.widgetPath)
        self.widget.setParent(self)
        # set initial window size
        self.resize(600, 540)      
        
        # Locate UI widgets

        # Close button
        self.btn_close = self.widget.findChild(QtWidgets.QPushButton, 'btn_close')
        self.run_check = self.widget.findChild(QtWidgets.QPushButton, 'run_check')     

        # Mesh count number
        self.qline_mesh_number = self.widget.findChild(QtWidgets.QLineEdit, 'qline_mesh_number')
        self.frame_mesh_number = self.widget.findChild(QtWidgets.QFrame, 'frame_mesh_number') 
        self.checkbox_mesh_number = self.widget.findChild(QtWidgets.QCheckBox, 'checkbox_mesh_number')

        # Faces with more than 4 sides counter
        self.qline_faces_4sides = self.widget.findChild(QtWidgets.QLineEdit, 'qline_faces_4sides')
        self.frame_faces_4sides = self.widget.findChild(QtWidgets.QFrame, 'frame_faces_4sides') 
        self.checkbox_faces_4sides = self.widget.findChild(QtWidgets.QCheckBox, 'checkbox_faces_4sides')
        self.btn_select_ngons = self.widget.findChild(QtWidgets.QPushButton, 'btn_select_ngons')

        # Delete history
        self.line_del_history = self.widget.findChild(QtWidgets.QLineEdit, 'line_del_history')
        self.frame_del_history = self.widget.findChild(QtWidgets.QFrame, 'frame_del_history')
        self.checkbox_del_history = self.widget.findChild(QtWidgets.QCheckBox, 'checkbox_del_history')
        self.btn_del_history = self.widget.findChild(QtWidgets.QPushButton, 'btn_del_history')

        # Freeze transforms
        self.line_frez_transforms = self.widget.findChild(QtWidgets.QLineEdit, 'line_frez_transforms')
        self.frame_frez_transforms = self.widget.findChild(QtWidgets.QFrame, 'frame_frez_transforms')
        self.checkbox_frez_transforms = self.widget.findChild(QtWidgets.QCheckBox, 'checkbox_frez_transforms')
        self.btn_frez_transforms = self.widget.findChild(QtWidgets.QPushButton, 'btn_frez_transforms')

        # Check for valid matching file names
        self.line_valid = self.widget.findChild(QtWidgets.QLineEdit, 'line_valid')
        self.frame_valid = self.widget.findChild(QtWidgets.QFrame, 'frame_valid')
        self.checkbox_valid = self.widget.findChild(QtWidgets.QCheckBox, 'checkbox_valid')

        # Check for non manifold geometry
        self.line_non_manifold = self.widget.findChild(QtWidgets.QLineEdit, 'line_non_manifold')
        self.frame_non_manifold = self.widget.findChild(QtWidgets.QFrame, 'frame_non_manifold')
        self.checkbox_non_manifold = self.widget.findChild(QtWidgets.QCheckBox, 'checkbox_non_manifold')

        # Check for Uv's spanning multiple udims
        self.line_uv_across = self.widget.findChild(QtWidgets.QLineEdit, 'line_uv_across')
        self.frame_uv_across = self.widget.findChild(QtWidgets.QFrame, 'frame_uv_across')
        self.checkbox_uv_across = self.widget.findChild(QtWidgets.QCheckBox, 'checkbox_uv_across')

        # Assign functionality to buttons
        self.btn_close.clicked.connect(self.closeWindow)
        self.run_check.clicked.connect(self.run_check_clicked)
        self.btn_select_ngons.clicked.connect(self.select_ngons_clicked)
        self.btn_del_history.clicked.connect(self.delete_history)
        self.btn_frez_transforms.clicked.connect(self.freeze_transforms)
    
    """
    Core Functions
    """

    #run check after button is clicked
    def run_check_clicked(self):
        self.store_meshes_and_counts()
        self.update_mesh_count()
        self.check_history()
        self.freeze_transform_check()
        self.validate_naming()
        self.check_non_manifold_geometry()
        self.multiple_udim_uv()
        self.update_ngon_count()
        self.reselect_meshes()

    #store currently selected meshes, transforms, and numbers of meshes
    def store_meshes_and_counts(self):
        self.selected_meshes = cmds.ls(selection=True, long=True)
        self.selected_transform = cmds.ls(selection=True, type='transform', long=True)
        self.scene_mesh_count = len(cmds.ls(type='mesh'))
        self.selected_mesh_count = len(self.selected_meshes)

    #reselect meshes after updating ngon count
    def reselect_meshes(self):
        for obj in self.selected_meshes:
            cmds.select(self.selected_meshes)       

    #update qline text, check box, and color frame based on scene mesh count results
    def update_mesh_count(self):
        self.qline_mesh_number.setText(f"Number of meshes in scene: {self.scene_mesh_count}")

        if self.scene_mesh_count > 0:
            self.checkbox_mesh_number.setChecked(True)
            self.frame_mesh_number.setStyleSheet("background-color: green;")
        else:
            self.checkbox_mesh_number.setChecked(False)
            self.frame_mesh_number.setStyleSheet("background-color: red;")

    #check for faces with more than 4 sides and return number of ngons
    def count_ngons(*arg):
        cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
        num_ngon_faces = cmds.polyEvaluate(faceComponent=True)
        cmds.polySelectConstraint(disable=True)
        return num_ngon_faces

    #update qline text, check box, and color frame based on ngon count results, also clear selection after
    def update_ngon_count(self):
        ngon_count = self.count_ngons()
        self.qline_faces_4sides.setText(f"Faces with more than 4 sides: {ngon_count}")
        cmds.select(clear=True)

        if ngon_count > 0:
            self.checkbox_faces_4sides.setChecked(False)
            self.frame_faces_4sides.setStyleSheet("background-color: red;")
        else:
            self.checkbox_faces_4sides.setChecked(True)
            self.frame_faces_4sides.setStyleSheet("background-color: green;")

    #update ngon count, line, checkbox, and color frame based on results, leave ngons selected
    def update_ngon_count_select(self):
        ngon_count = self.count_ngons()
        self.qline_faces_4sides.setText(f"Faces with more than 4 sides: {ngon_count}")

        if ngon_count > 0:
            self.checkbox_faces_4sides.setChecked(False)
            self.frame_faces_4sides.setStyleSheet("background-color: red;")
        else:
            self.checkbox_faces_4sides.setChecked(True)
            self.frame_faces_4sides.setStyleSheet("background-color: green;")

    #when button is clicked select ngons on selected meshes
    def select_ngons_clicked(self, *arg):
        cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
        num_ngon_faces = cmds.polyEvaluate(faceComponent=True)
        cmds.polySelectConstraint(disable=True)
        self.update_ngon_count_select()

    #check if objects have history and update text, check box, and color frame
    def check_history(self):
        meshes_with_history = 0
 
        for obj in self.selected_meshes:
            object_history = cmds.listHistory(obj)  # Get the history nodes
            num_history_items = len(object_history)

            if num_history_items >= 2:
                print(f"Object '{obj}' history found")
                meshes_with_history += 1
            else:
                print(f"Object '{obj}' history not found")

        if meshes_with_history > 0:  # Check if any of the meshes have history
            self.checkbox_del_history.setChecked(False)
            self.frame_del_history.setStyleSheet("background-color: red;")
        else:
            self.checkbox_del_history.setChecked(True)
            self.frame_del_history.setStyleSheet("background-color: green;")

    #delete by type history and recheck history   
    def delete_history(self):        
        for obj in self.selected_meshes:
            cmds.delete(obj, constructionHistory = True)

        self.check_history()

    #check if transforms are frozen
    def freeze_transform_check(self):
        meshes_without_frozen_transforms = 0

        #get attributes of each mesh
        for obj in self.selected_transform:
            # Get translation, rotation, and scale values
            translation_attr = cmds.getAttr(obj + '.translate')[0]
            rotation_attr = cmds.getAttr(obj + '.rotate')[0]
            scale_attr = cmds.getAttr(obj + '.scale')[0]
            
            # Check if all transforms are zero and scale is 1
            if all(value == 0 for value in translation_attr) and all(value == 0 for value in rotation_attr) and all(value == 1 for value in scale_attr):
                print(f"Object '{obj}' has zeroed and frozen transforms.")
            else:
                print(f"Object '{obj}' does not have zeroed or frozen transforms.")
                meshes_without_frozen_transforms += 1

            if meshes_without_frozen_transforms > 0:
                self.checkbox_frez_transforms.setChecked(False)
                self.frame_frez_transforms.setStyleSheet("background-color: red;")
            else:
                self.checkbox_frez_transforms.setChecked(True)
                self.frame_frez_transforms.setStyleSheet("background-color: green;")

    #freeze transforms, recheck if transforms are frozen, update UI
    def freeze_transforms(self):
        for obj in self.selected_transform:
            # Freeze transforms on all selected meshes
            cmds.makeIdentity(self.selected_transform, apply=True, translate=True, rotate=True, scale=True, normal=False)

        self.freeze_transform_check()

    #check if name of asset matches the scene name and folder name
    def validate_naming(self):
        file_path = cmds.file(q=True, sn=True)
        folder_name = os.path.basename(os.path.dirname(file_path))
        file_name = os.path.splitext(os.path.basename(cmds.file(q=True, sn=True)))[0]
        number_of_valid = 0
        cleaned_asset_names = [name.lstrip('|') for name in self.selected_meshes]

        # Check if the cleaned asset name matches the folder and file names
        for obj in cleaned_asset_names:
            if obj == folder_name and obj == file_name:
                print(f"Asset '{obj}' matches folder '{folder_name}' and file '{file_name}'")
                number_of_valid += 1
            else:
                print(f"Asset '{obj}' does NOT match folder '{folder_name}' or file '{file_name}'")

        if self.selected_mesh_count > number_of_valid:
            self.line_valid.setText(f"Valid Matching Folder, File, and Asset Name: {number_of_valid} of {self.selected_mesh_count}")
            self.checkbox_valid.setChecked(False)
            self.frame_valid.setStyleSheet("background-color: red;")
        else:
            self.line_valid.setText(f"Valid Matching Folder, File, and Asset Name: {number_of_valid} of {self.selected_mesh_count}")
            self.checkbox_valid.setChecked(True)
            self.frame_valid.setStyleSheet("background-color: green;")

    #check if non manifol geo is present and update UI
    def check_non_manifold_geometry(self):
        """
        Checks if the selected meshes have any faces with non-manifold geometry.
        Returns a dictionary where the key is the mesh name and the value is a list of non-manifold face IDs.
        """
        non_manifold_faces = {}       
        
        for mesh in self.selected_transform:
            # Get the shape node of the mesh
            shape_node = cmds.listRelatives(mesh, shapes=True, fullPath=True)
            
            # Check for non-manifold geometry
            non_manifold = cmds.polyInfo(shape_node[0], nonManifoldVertices=True)
            print(f"Non-manifold vertices for {shape_node[0]}: {non_manifold}")
            
            # If non_manifold is not None, process the data
            if non_manifold:
                non_manifold_faces[mesh] = [int(s) for s in non_manifold[0].split()[2:]]
                print(f"non manifold vertices found")
                self.checkbox_non_manifold.setChecked(False)
                self.frame_non_manifold.setStyleSheet("background-color: red;")
            else:
                self.checkbox_non_manifold.setChecked(True)
                self.frame_non_manifold.setStyleSheet("background-color: green;")
    
    #check if selected objects are using multiple udims and update UI
    def multiple_udim_uv(self):
        """
        Checks if the selected meshes' UVs span multiple tiles or UDIMs.
        :return: True if UVs of any selected mesh span multiple UDIMs, False otherwise.
        """
        # Get the currently selected meshes
        number_of_multiple_udim_uvs = 0

        for mesh in self.selected_meshes:
            # Get the UV coordinates of the mesh
            uvs = cmds.polyEditUV(mesh + ".map[*]", query=True)

            if uvs:
                for i in range(0, len(uvs), 2):
                    u_coord = uvs[i]
                    v_coord = uvs[i + 1]

                    # Check if the UVs are outside the 0-1 range
                    if u_coord < 0 or u_coord > 1 or v_coord < 0 or v_coord > 1:                        
                        number_of_multiple_udim_uvs += 1                                            

        if self.selected_mesh_count < number_of_multiple_udim_uvs:
            print (f"The mesh contains multiple udim uv's ")
            self.checkbox_uv_across.setChecked(False)
            self.frame_uv_across.setStyleSheet("background-color: red;")
        else:
            print (f"The mesh does not contain multiple udim uv's ")
            self.checkbox_uv_across.setChecked(True)
            self.frame_uv_across.setStyleSheet("background-color: green;")
        


    def resizeEvent(self, event):
        """
        Called on automatically generated resize event
        """
        self.widget.resize(self.width(), self.height())
        
    def closeWindow(self):
        """
        Close window.
        """
        print ('closing window')
        self.destroy()


    
def openWindow():
    """
    ID Maya and attach tool window.
    """
    # Maya uses this so it should always return True
    if QtWidgets.QApplication.instance():
        # Id any current instances of tool and destroy
        for win in (QtWidgets.QApplication.allWindows()):
            if 'myToolWindowName' in win.objectName(): # update this name to match name below
                win.destroy()





    #QtWidgets.QApplication(sys.argv)
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)
    MayaAssetChecker.window = MayaAssetChecker(parent = mayaMainWindow)
    MayaAssetChecker.window.setObjectName('myToolWindowName') # code above uses this to ID any existing windows
    MayaAssetChecker.window.setWindowTitle('MayaAssetChecker')
    MayaAssetChecker.window.show()
    
openWindow()