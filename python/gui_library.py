import os

from PyQt5.QtGui import (QIcon, QFont, QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (QSortFilterProxyModel, Qt)
from PyQt5.QtWidgets import (QPushButton, QCheckBox, QGroupBox, QHBoxLayout,
                             QLineEdit, QTreeView, QVBoxLayout,
                             QAbstractItemView, QSizePolicy)

import tools
import define

PLAYLIST, KNOWN, ARTIST, ALBUM, DURATION, COLUMNS = range(6)


class SortFilterProxyModel(QSortFilterProxyModel):

    library = None

    def __init__(self, library):

        super().__init__()

        self.library = library

    def filterAcceptsRow(self, sourceRow, sourceParent):

        playlist = self.sourceModel().data(self.sourceModel().index(sourceRow, PLAYLIST, sourceParent))
        if not self.library.filterKnownCheckbox.isChecked() and playlist.meta.known:
            return False

        pattern = self.filterRegExp().pattern()

        if pattern != '':

            artist = self.sourceModel().data(self.sourceModel().index(sourceRow, ARTIST, sourceParent))
            album = self.sourceModel().data(self.sourceModel().index(sourceRow, ALBUM, sourceParent))

            return pattern in artist.lower() or pattern in album.lower()

        else:

            # return super(SortFilterProxyModel, self).filterAcceptsRow(sourceRow, sourceParent)
            return True


class Library(QGroupBox):
    view = None
    model = None
    filter = None
    searchIcon = None
    searchLineEdit = None
    exportButton = None
    filterKnownCheckbox = None

    def __init__(self, playlists, font=QFont()):

        super().__init__()

        self.initUI(playlists, font)

    def initUI(self, playlists, font):

        layout_top = QHBoxLayout()
        layout_main = QHBoxLayout()

        # top

        self.filterKnownCheckbox = self.addCheckbox('', True, font, layout_top)
        self.filterKnownCheckbox.setToolTip('Uncheck to filter known items')
        self.searchIcon = self.addIcon(os.path.join(define.IMGDIR, 'lense.png'), layout_top)
        self.searchLineEdit = self.addEdit(font, layout_top)
        self.searchLineEdit.setToolTip('Type author or album name to filter library')

        # list

        model = QStandardItemModel(0, COLUMNS, self)

        model.setHeaderData(PLAYLIST, Qt.Horizontal, 'Playlist')
        model.setHeaderData(KNOWN, Qt.Horizontal, '')
        model.setHeaderData(ARTIST, Qt.Horizontal, 'Autor')
        model.setHeaderData(ALBUM, Qt.Horizontal, 'Album')
        model.setHeaderData(DURATION, Qt.Horizontal, 'Dauer')

        for playlist in playlists:
            model.insertRow(0)
            model.setData(model.index(0, PLAYLIST), playlist)
            item = QStandardItem()
            item.setCheckable(True)
            item.setCheckState(Qt.Checked if playlist.meta.known else Qt.Unchecked)
            model.setItem(0, KNOWN, item)
            model.setData(model.index(0, ARTIST), playlist.meta.artist)
            model.setData(model.index(0, ALBUM), playlist.meta.album)
            model.setData(model.index(0, DURATION), tools.friendlytime(playlist.meta.duration))

        filterModel = SortFilterProxyModel(self)
        filterModel.setSourceModel(model)

        view = QTreeView()
        view.setFont(font)
        view.setRootIsDecorated(False)
        view.setAlternatingRowColors(True)
        view.setSortingEnabled(True)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        view.setModel(filterModel)
        for i in range(model.columnCount() - 1, 0, -1):
            view.sortByColumn(i, Qt.AscendingOrder)
            view.resizeColumnToContents(i)
        view.hideColumn(0)

        layout_main.addWidget(view)

        # filter

        self.searchLineEdit.textChanged.connect(filterModel.setFilterFixedString)

        # export

        self.exportButton = self.addButton(os.path.join(define.IMGDIR, 'save.png'), layout_top, setHeight=True,
                                           setWidth=True)
        self.exportButton.setToolTip('Export all files of selected playlist')

        # layout

        layout = QVBoxLayout()
        layout.addLayout(layout_top)
        layout.addLayout(layout_main)

        self.setLayout(layout)

        self.view = view
        self.model = model
        self.filter = filterModel

    def addIcon(self, path, layout):

        button = QPushButton()
        button.setFlat(True)
        icon = QIcon(path)
        button.setIcon(icon)
        size = icon.availableSizes()[0]
        button.setFixedSize(size)
        button.setIconSize(size)
        layout.addWidget(button)

        return button

    def addButton(self, path, layout, setHeight=True, setWidth=False):

        button = QPushButton()
        icon = QIcon(path)
        button.setIcon(icon)
        size = icon.availableSizes()[0]
        if setHeight:
            button.setFixedHeight(size.height())
        if setWidth:
            button.setFixedWidth(size.width())
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setIconSize(size)
        layout.addWidget(button)

        return button

    def addEdit(self, font, layout):

        edit = QLineEdit('')
        edit.setFont(font)
        layout.addWidget(edit)

        return edit

    def addCheckbox(self, text, enabled, font, layout):

        check = QCheckBox('')
        check.setText(text)
        check.setFont(font)
        check.setChecked(enabled)
        layout.addWidget(check)

        return check

    def getPlaylist(self):

        indices = self.view.selectedIndexes()
        if len(indices) == 0:
            return None

        index = self.filter.mapToSource(indices[0])
        item = self.model.item(index.row())
        playlist = item.data(0)

        return playlist

    def clicked(self, index, database):

        index = self.filter.mapToSource(index)

        if index.column() == KNOWN:
            item = self.model.item(index.row(), index.column())
            playlist = self.model.item(index.row()).data(0)
            playlist.meta.known = item.checkState() == Qt.Checked
            database.write(playlist.meta)
