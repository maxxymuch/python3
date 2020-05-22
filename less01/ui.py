import os.path
import sys


print('loading {}'.format(__name__))
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QPixmap, QIcon, QPalette
from PyQt5.QtWidgets import (QMainWindow, QLabel, QDesktopWidget, QSizePolicy, QScrollArea,
                             QAction, QFileDialog, QApplication, QInputDialog)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_PATH = os.path.join(ROOT_DIR, 'IMG')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.currentImage = ''

        self.init_ui()

    def init_ui(self):
        self.setGeometry(500, 500, 700, 500)
        self.center()

        self.image_label = QLabel()
        self.image_label.setBackgroundRole(QPalette.Dark)
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.image_label.setScaledContents(True)

        self.scroll_area = QScrollArea()
        self.scroll_area.setBackgroundRole(QPalette.Dark)
        self.scroll_area.setWidget(self.image_label)
        self.setCentralWidget(self.scroll_area)
        self.set_action()
        self.init_tool_bar()
        app_icon = QIcon(os.path.join(IMAGES_PATH, 'origin.png'))
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        file_menu.addAction(self.open_file)
        file_menu.addAction(self.save_file)
        self.enable_actions(False)
        self.setWindowTitle('Работа с изображением')
        self.setWindowIcon(app_icon)
        self.statusBar().showMessage('Откройте изображение для начала')


    def set_action(self):
        open_img = QIcon(os.path.join(IMAGES_PATH, 'open.png'))
        save_img = QIcon(os.path.join(IMAGES_PATH, 'save.png'))
        gray_img = QIcon(os.path.join(IMAGES_PATH, 'gray.png'))
        sepia_img = QIcon(os.path.join(IMAGES_PATH, 'sepia.png'))
        bw_img = QIcon(os.path.join(IMAGES_PATH, 'bw.png'))
        inv_img = QIcon(os.path.join(IMAGES_PATH, 'inv.png'))
        orig_img = QIcon(os.path.join(IMAGES_PATH, 'origin.png'))
        self.open_file = QAction(open_img, '&Открыть', self, shortcut='Comm+O', triggered=self.open_wind, )
        self.save_file = QAction(save_img, '&Сохранить как...', self, shortcut='Comm+S', triggered=self.save_wind)
        self.set_original_action = QAction(orig_img, 'Оригинал', self, triggered=self.to_original)
        self.set_gray_action = QAction(gray_img, 'Серый', self, triggered=self.to_gray)
        self.set_bw_action = QAction(bw_img, 'ЧБ', self, triggered=self.to_bw)
        self.set_sepia_action = QAction(sepia_img, 'Сепия', self, triggered=self.to_sepia)
        self.set_inverted_action = QAction(inv_img, 'Инверсия', self, triggered=self.to_inverted)

    def enable_actions(self, state):
        for action in self.toolbar.actions():
            action.setEnabled(state)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_tool_bar(self):

        self.toolbar = self.addToolBar('Image tools')
        self.toolbar.addAction(self.set_original_action)
        self.toolbar.addAction(self.set_gray_action)
        self.toolbar.addAction(self.set_bw_action)
        self.toolbar.addAction(self.set_sepia_action)
        self.toolbar.addAction(self.set_inverted_action)


    def open_wind(self):
        fname = QFileDialog.getOpenFileName(self, 'Открыть файл', os.path.expanduser(''),
                                            'Изображения (*.png *.xpm *.jpg);;Все файлы (*.*)')[0]
        if fname:
            self.statusBar().showMessage('Файл: {}'.format(fname))
            print(fname)
        if os.path.isfile(fname):
            self.pixmap = QPixmap(fname)
            self.currentImage = fname
            self.image_label.setPixmap(self.pixmap)
            self.adjust_size()
            self.enable_actions(True)

    def save_wind(self):
        fname = QFileDialog.getSaveFileName(self, 'Сохранить как', os.path.expanduser(''),
                                            'Изображения (*.png *.xpm *.jpg);;Все файлы (*.*)')[0]
        if fname:
            self.statusBar().showMessage('Файл сохранен как: {}'.format(fname))
            print(fname)
            self.pixmap.save(fname)
            self.currentImage = fname

    def adjust_size(self):
        self.image_label.adjustSize()
        self.resize(self.image_label.width() + 25, self.image_label.height() + 60)

    def to_original(self):
        if os.path.isfile(self.currentImage):
            self.pixmap = QPixmap(self.currentImage)
            self.image_label.setPixmap(self.pixmap)
            self.adjust_size()

    def to_gray(self):
        if os.path.isfile(self.currentImage):
            self.pixmap = ImageEditor(self.currentImage).gray()
            self.image_label.setPixmap(self.pixmap)
            self.adjust_size()

    def to_bw(self):
        if os.path.isfile(self.currentImage):
            self.pixmap = ImageEditor(self.currentImage).bw()
            self.image_label.setPixmap(self.pixmap)
            self.adjust_size()


    def to_sepia(self):
        if os.path.isfile(self.currentImage):
            self.pixmap = ImageEditor(self.currentImage).sepia()
            self.image_label.setPixmap(self.pixmap)
            self.adjust_size()

    def to_inverted(self):
        if os.path.isfile(self.currentImage):
            self.pixmap = ImageEditor(self.currentImage).inverted()
            self.image_label.setPixmap(self.pixmap)
            self.adjust_size()

class ImageEditor:
    def __init__(self, path):
        self.image = Image.open(path)
        self.draw = ImageDraw.Draw(self.image)
        self.width = self.image.size[0]
        self.height = self.image.size[1]
        self.pix = self.image.load()

    def gray(self):
        img_tmp = ImageQt(self.image.convert('L'))
        pixmap = QPixmap.fromImage(img_tmp)
        return pixmap

    def bw(self) -> object:
        factor = 30
        for i in range(self.width):
            for j in range(self.height):
                a = self.pix[i, j][0]
                b = self.pix[i, j][1]
                c = self.pix[i, j][2]
                s = a + b + c
                if s > (((255 + factor) // 2) * 3):
                    a, b, c = 255, 255, 255
                else:
                    a, b, c = 0, 0, 0
                self.draw.point((i, j), (a, b, c))
        img_tmp = ImageQt(self.image.convert('RGBA'))
        pixmap = QPixmap.fromImage(img_tmp)
        return pixmap


    def inverted(self):
        for i in range(self.width):
            for j in range(self.height):
                a = self.pix[i, j][0]
                b = self.pix[i, j][1]
                c = self.pix[i, j][2]
                self.draw.point((i, j), (255 - a, 255 - b, 255 - c))

        img_tmp = ImageQt(self.image.convert('RGBA'))
        pixmap = QPixmap.fromImage(img_tmp)
        return pixmap

    def sepia(self):
        for i in range(self.width):
            for j in range(self.height):
                r = self.pix[i, j][0]
                g = self.pix[i, j][1]
                b = self.pix[i, j][2]

                sep_r = int(r * .393 + g * .769 + b * .189)
                sep_g = int(r * .349 + g * .686 + b * .168)
                sep_b = int(r * .272 + g * .534 + b * .131)

                if sep_r > 255:
                    sep_r = 255
                if sep_g > 255:
                    sep_g = 255
                if sep_b > 255:
                    sep_b = 255
                self.draw.point((i, j), (sep_r, sep_g, sep_b))
        img_tmp = ImageQt(self.image.convert('RGBA'))
        pixmap = QPixmap.fromImage(img_tmp)
        return pixmap


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())