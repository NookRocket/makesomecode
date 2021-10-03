import sys
import os
from PySide2 import QtWidgets, QtCore, QtGui

Source_Dir = 'C:/PICTURES'
Target_Dir = 'C:/myalbum'
StyleSheet = '''
*{  background: rgb(50, 50, 50);
    padding: 5px 10px 5px 10px;
    color: #DDDDDD;
    border: 1px groove rgb(38, 38, 38);
    border-radius: 3px;
}
QLabel{
    border: none;
}
QPushButton{
    background: rgb(70,70,70);
}
QPushButton:hover{
    background: rgb(70, 130, 200);
}
'''

class OrganizePhotoWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OrganizePhotoWindow, self).__init__(parent)
        self.setWindowTitle('Organize Photos')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setStyleSheet(StyleSheet)

        self.input_image_lineedit = QtWidgets.QLineEdit()
        self.input_image_button = QtWidgets.QPushButton('Browse')
        self.lib_image_lineedit = QtWidgets.QLineEdit()
        self.lib_image_button = QtWidgets.QPushButton('Browse')
        self.image_listwidget = QtWidgets.QListWidget()

        # Widget Settings
        self.image_listwidget.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.image_listwidget.setViewMode(QtWidgets.QListView.IconMode)
        self.image_listwidget.setResizeMode(QtWidgets.QListView.Adjust)
        self.image_listwidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.image_listwidget.setStyleSheet('QListWidget::item:hover{background:rgb( 70, 130, 200);}'
                                            'QListWidget::item:selected{background:rgb(90, 150, 200);}')

        # Connect signal
        self.input_image_button.clicked.connect(self.browse_input_dir)
        self.lib_image_button.clicked.connect(self.browse_input_dir)
        self.input_image_lineedit.textChanged.connect(self.list_image)
        self.image_listwidget.customContextMenuRequested.connect(self.show_category_menu)

        # Init value
        self.input_image_lineedit.setText(Source_Dir)
        self.lib_image_lineedit.setText(Target_Dir)

        self.initial_layout()

    def initial_layout(self):
        self.layout().setAlignment(QtCore.Qt.AlignTop)

        layout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(layout)
        label = QtWidgets.QLabel('Source Directory:')
        label.setStyleSheet('font: bold;')
        layout.addWidget(label)
        layout.addWidget(self.input_image_lineedit)
        layout.addWidget(self.input_image_button)

        layout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(layout)
        label = QtWidgets.QLabel('Target Directory:')
        label.setStyleSheet('font: bold;')
        layout.addWidget(label)
        layout.addWidget(self.lib_image_lineedit)     
        layout.addWidget(self.lib_image_button)        

        self.layout().addWidget(self.image_listwidget)
        self.resize(1000, 800)

    def browse_input_dir(self):
        dialog = QtWidgets.QFileDialog()
        selected_dir = dialog.getExistingDirectory( self, 'Select Folder')
        if selected_dir:
            if self.sender() == self.input_image_button:
                self.input_image_lineedit.setText(selected_dir)
            elif self.sender() == self.lib_image_button:
                self.lib_image_lineedit.setText(selected_dir)

    def list_image(self, dirpath):
        self.image_listwidget.clear()

        if not os.path.exists(dirpath):
            return

        image_type = ['.bmp', '.gif', '.jpg', 
                        '.jpeg', '.png', '.pbm', 
                        '.pgm', '.xbm', 'xpm']
        for image in os.listdir(dirpath):
            if os.path.splitext(image)[-1] in image_type:
                image_path = '{}/{}'.format(dirpath, image)
                item = QtWidgets.QListWidgetItem()
                item.setSizeHint( QtCore.QSize(300,300) )
                self.image_listwidget.addItem(item)
                self.create_image_widget( item, image_path)
                item.setData(QtCore.Qt.UserRole, image_path)
    
    def create_image_widget(self, item, image_path):
        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QVBoxLayout())
        widget.layout().setAlignment(QtCore.Qt.AlignBottom)
        widget.setStyleSheet('padding: 0px;'
                            'background: none;'
                            'border: none;')

        image_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(item.sizeHint(), QtCore.Qt.KeepAspectRatio,
                                QtCore.Qt.SmoothTransformation)

        image_label.setPixmap(pixmap)
        widget.layout().addWidget(image_label)

        name_label = QtWidgets.QLabel(os.path.basename(image_path))
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        widget.layout().addWidget(name_label)
        widget.setToolTip(name_label.text())
        self.image_listwidget.setItemWidget(item, widget)

    def show_category_menu(self, pos):
        item = self.image_listwidget.itemAt(pos)
        if item:
            album_dir = self.lib_image_lineedit.text().replace('\\','/')
            menu = QtWidgets.QMenu(self)
            menu.setStyleSheet(':item:selected{background: rgb(70, 130, 200);}')
            self.get_category(menu, album_dir)
            menu.exec_(self.image_listwidget.mapToGlobal(pos))
    
    def get_child_folder(self, root):
        if not os.path.exists(root):
            return
        return [f for f in os.listdir(root) 
                if os.path.isdir(os.path.join(root, f))]
    
    def get_category(self, menu, root):
        # 1) Are there any folder in side?
        categories = self.get_child_folder(root)

        # 2) No, there aren't. then add action item to context menu
        if not categories:
            action = menu.addAction(os.path.basename(root), self.move_image)
            action.setData(root)
            return
        
        # 3) Yes, there are. then add menu item to context menu 
        for cat in categories:
            child_dir = os.path.join(root, cat)
            # 4) Are there any folder in side (3) ?
            childs = self.get_child_folder(child_dir)
            # 5) Yes, there are. then add menu item to menu (4)
            if childs:
                child_menu = menu.addMenu(cat)
                self.get_category(child_menu, child_dir)
            # 6) No, there aren't. then add action item to menu (4)
            else:
                action = menu.addAction(cat, self.move_image)
                action.setData('/'.join([root, cat]))

    def move_image(self):
        action_menu = self.sender()
        cat_dir = action_menu.data()
        
        image_items = self.image_listwidget.selectedItems()
        for item in image_items:
            image_path = item.data(QtCore.Qt.UserRole)
            move_to_path = '{}/{}'.format(cat_dir, 
                                    os.path.basename(image_path))
            os.rename(image_path, move_to_path)

        self.list_image(self.input_image_lineedit.text())

if __name__ == '__main__':
    app = QtWidgets.QApplication( sys.argv )
    window = OrganizePhotoWindow()
    window.showMaximized()
    sys.exit(app.exec_())