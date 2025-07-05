# Python Version: 3.13

import os
import sys

from PySide6.QtCore import Qt, QFile, QTextStream, QTimer, QUrl
from PySide6.QtGui import (
    QIcon, QPalette, QAction, QKeySequence, QDesktopServices, QTextDocument
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QScrollArea, QLabel, QFileDialog, QPushButton, QDialog, QFrame
)

from functions.DropFileRewrite import *
from functions.Highlighter import *
from functions.Renderer import *


# noinspection PyAttributeOutsideInit
class MarkdownPreviewer(QMainWindow):
    def __init__(self, file_path=None):
        super().__init__()
        self.currentFile = file_path  # Initialize with the provided file path
        self.setupUi()
        self.setupMenu()
        self.setupAutoSave()

        # Load the file if one was provided
        if file_path:
            self.loadFile(file_path)

    def setupUi(self):
        self.setWindowTitle("MPlus")
        self.setGeometry(100, 100, 1000, 600)

        if getattr(sys, 'frozen', False):
            os.chdir(os.path.dirname(sys.executable))
        else:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

        self.setWindowIcon(QIcon("_internal/ICON.ico"))
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainWidget.setStyleSheet("background-color: #252526;")

        mainLayout = QHBoxLayout(mainWidget)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #333337; }")
        mainLayout.addWidget(self.splitter)

        # 预览与编辑
        self.setupMarkdownInput()
        self.setupPreviewArea()

        self.splitter.setSizes([self.width() // 2, self.width() // 2])

        self.markdownInput.setPlaceholderText(
            "导入，拖拽您的MarkDown文件到此处，或者直接开始创作！\n"
        )

    # noinspection PyAttributeOutsideInit
    def setupMarkdownInput(self):
        self.markdownInput = DragDropTextEdit(load_callback=self.loadFile)
        self.markdownInput.setFont(QFont("Microsoft YaHei", 10))
        self.markdownInput.setStyleSheet("""
            QTextEdit {
                font-size: 12px;
                line-height: 1.5;
                padding: 12px;
                color: #ffffff;
                background-color: #1e1e1e;
                border: none;
                selection-color: white;
                selection-background-color: #094771;
            }
            QTextEdit:focus {
                border: 1px solid #569cd6;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #454545;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }
            QScrollBar:horizontal {
                background: #1e1e1e;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #454545;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, 
            QScrollBar::sub-line:horizontal {
                width: 0px;
                background: none;
            }
        """)
        self.markdownInput.textChanged.connect(self.updatePreview)
        self.highlighter = MarkdownHighlighter(self.markdownInput.document())
        self.splitter.addWidget(self.markdownInput)

    def setupPreviewArea(self):
        self.previewArea = QScrollArea()
        self.previewArea.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QScrollBar:vertical {
                background: #252526;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #454545;
                min-height: 20px;
            }
        """)

        self.previewLabel = QLabel()
        self.previewLabel.setWordWrap(True)
        self.previewLabel.setAlignment(Qt.AlignTop)
        self.previewLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.previewLabel.setStyleSheet("""
            QLabel {
                font-family: "Microsoft YaHei", sans-serif;
                font-size: 14px;
                line-height: 1.6;
                padding: 15px;
                color: #ffffff;
                background-color: #1e1e1e;
            }
        """)

        self.previewArea.setWidget(self.previewLabel)
        self.previewArea.setWidgetResizable(True)
        self.splitter.addWidget(self.previewArea)

    def setupMenu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #252526;
                color: white;
                border: none;
            }
            QMenuBar::item:selected {
                background-color: #333337;
            }
            QMenu {
                background-color: #252526;
                color: white;
                border: 1px solid #333337;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)

        # 文件菜单
        fileMenu = menubar.addMenu("文件")

        openAction = QAction("打开文件", self)
        openAction.setIcon(QIcon.fromTheme("document-open"))
        openAction.setShortcut(QKeySequence("Ctrl+O"))
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)

        saveAction = QAction("保存", self)
        saveAction.setIcon(QIcon.fromTheme("document-save"))
        saveAction.setShortcut(QKeySequence("Ctrl+S"))
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)

        exportAction = QAction("导出/另存为", self)
        exportAction.setIcon(QIcon.fromTheme("document-save-as"))
        exportAction.setShortcut(QKeySequence("Ctrl+Shift+S"))
        exportAction.triggered.connect(self.exportFile)
        fileMenu.addAction(exportAction)

        printAction = QAction("打印", self)
        printAction.setIcon(QIcon.fromTheme("document-print"))
        printAction.setShortcut(QKeySequence("Ctrl+P"))
        printAction.triggered.connect(self.printPreviewContent)
        fileMenu.addAction(printAction)

        exitAction = QAction("退出", self)
        exitAction.setIcon(QIcon.fromTheme("application-exit"))
        exitAction.setShortcut(QKeySequence("Ctrl+Q"))
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        editMenu = menubar.addMenu("编辑")

        undoAction = QAction("撤销", self)
        undoAction.setIcon(QIcon.fromTheme("edit-undo"))
        undoAction.setShortcut(QKeySequence("Ctrl+Z"))
        undoAction.triggered.connect(self.markdownInput.undo)
        editMenu.addAction(undoAction)

        redoAction = QAction("重做", self)
        redoAction.setIcon(QIcon.fromTheme("edit-redo"))
        redoAction.setShortcut(QKeySequence("Ctrl+Y"))
        redoAction.triggered.connect(self.markdownInput.redo)
        editMenu.addAction(redoAction)

        cutAction = QAction("剪切", self)
        cutAction.setIcon(QIcon.fromTheme("edit-cut"))
        cutAction.setShortcut(QKeySequence("Ctrl+X"))
        cutAction.triggered.connect(self.markdownInput.cut)
        editMenu.addAction(cutAction)

        copyAction = QAction("复制", self)
        copyAction.setIcon(QIcon.fromTheme("edit-copy"))
        copyAction.setShortcut(QKeySequence("Ctrl+C"))
        copyAction.triggered.connect(self.markdownInput.copy)
        editMenu.addAction(copyAction)

        pasteAction = QAction("粘贴", self)
        pasteAction.setIcon(QIcon.fromTheme("edit-paste"))
        pasteAction.setShortcut(QKeySequence("Ctrl+V"))
        pasteAction.triggered.connect(self.markdownInput.paste)
        editMenu.addAction(pasteAction)

        selectAllAction = QAction("全选", self)
        selectAllAction.setIcon(QIcon.fromTheme("edit-select-all"))
        selectAllAction.setShortcut(QKeySequence("Ctrl+A"))
        selectAllAction.triggered.connect(self.markdownInput.selectAll)
        editMenu.addAction(selectAllAction)

        # 帮助菜单
        helpMenu = menubar.addMenu("帮助")

        tutorialAction = QAction("教程", self)
        tutorialAction.setIcon(QIcon.fromTheme("system-search"))
        tutorialAction.setShortcut(QKeySequence("Ctrl+H"))
        tutorialAction.triggered.connect(self.showTutorial)
        helpMenu.addAction(tutorialAction)

        aboutAction = QAction("关于", self)
        aboutAction.setIcon(QIcon.fromTheme("help-about"))
        aboutAction.setShortcut(QKeySequence("Ctrl+I"))
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)

    def setupAutoSave(self):  # 自动保存
        self.autoSaveTimer = QTimer(self)
        self.autoSaveTimer.setInterval(30000)
        self.autoSaveTimer.timeout.connect(self.autoSave)
        self.autoSaveTimer.start()

    def updatePreview(self):
        markdownText = self.markdownInput.toPlainText()
        renderer = MarkdownRenderer()
        html = renderer.renderMarkdown(markdownText)

        css = """
        <style>
            body { font-family: "Microsoft YaHei", sans-serif; color: white; background-color: #1e1e1e; }
            pre, code { font-family: Consolas, "Microsoft YaHei", monospace; background-color: #252525; }
            pre { padding: 10px; border-radius: 3px; }
            h1, h2, h3, h4, h5, h6 { font-family: "Microsoft YaHei", sans-serif; }
            table { border-collapse: collapse; width: 100%; margin: 15px 0; border: 1px solid #454545; }
            th, td { border: 1px solid #454545; padding: 8px 12px; text-align: left; }
            th { background-color: #333337; font-weight: bold; }
            tr:nth-child(even) { background-color: #252525; }
            tr:hover { background-color: #2a2a2a; }
            .codehilite { position: relative; margin: 1em 0; border-radius: 4px; overflow: hidden; }
            .codehilite pre { margin: 0; padding: 1em; overflow-x: auto; }
            blockquote { margin: 10px 0; padding: 12px 15px; background-color: rgba(50, 50, 50, 0.3); border-left: 4px solid #6a9955; }
            blockquote.level-2, blockquote blockquote { margin-left: 20px; background-color: rgba(60, 60, 60, 0.3); border-left-color: #8a7578; }
            blockquote.level-3, blockquote blockquote blockquote { margin-left: 40px; background-color: rgba(70, 70, 70, 0.3); border-left-color: #7a6568; }
            blockquote.level-4 { margin-left: 60px; background-color: rgba(80, 80, 80, 0.3); border-left-color: #6a5558; }
            blockquote.level-5 {
            margin-left: 80px;
            background-color: rgba(90, 90, 90, 0.3);
            border-left-color: #5a4548;
            }
            blockquote.level-6 {
            margin-left: 100px;
            background-color: rgba(90, 90, 90, 0.3);
            border-left-color: #4a4548;
            }
            blockquote.level-7 {
            margin-left: 120px;
            background-color: rgba(90, 90, 90, 0.3);
            border-left-color: #3a4548;
            }        
            blockquote.level-8 {
            margin-left: 140px;
            background-color: rgba(90, 90, 90, 0.3);
            border-left-color: #2a4548;
            }        
            blockquote.level-9 {
            margin-left: 160px;
            background-color: rgba(90, 90, 90, 0.3);
            border-left-color: #1a4548;
            }                 
            blockquote.level-10 {
            margin-left: 180px;
            background-color: rgba(90, 90, 90, 0.3);
            border-left-color: #0a4548;
            }                        
        </style>
        """

        self.previewLabel.setText(css + html)

    def openFile(self):  # 打开文件
        filePath, _ = QFileDialog.getOpenFileName(
            self, "打开 Markdown 文件", "",
            "Markdown文件 (*.md *.markdown *.txt);;所有文件 (*)"
        )
        if filePath:
            self.loadFile(filePath)

    def loadFile(self, filePath):  # 加载文件，顺带和光标爆了
        file = QFile(filePath)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            content = stream.readAll()
            file.close()

            # 1. 保存当前分割器状态
            splitter_sizes = self.splitter.sizes()

            # 2. 移除旧的 QTextEdit
            old_editor = self.markdownInput
            old_editor.setParent(None)  # 从布局中移除
            old_editor.deleteLater()  # 安全销毁

            # 3. 创建新的 QTextEdit 并插入到 splitter 的左侧
            self.markdownInput = DragDropTextEdit(load_callback=self.loadFile)
            self.setupMarkdownInput()  # 重新应用样式和设置
            self.splitter.insertWidget(0, self.markdownInput)  # 确保在左侧

            # 4. 恢复内容
            self.markdownInput.setPlainText(content)
            self.currentFile = filePath
            self.updateWindowTitle()

            # 5. 恢复分割器比例
            self.splitter.setSizes(splitter_sizes)

            # 6. 强制聚焦并显示光标
            self.markdownInput.setFocus()
            cursor = self.markdownInput.textCursor()
            self.markdownInput.setTextCursor(cursor)

    def saveFile(self):  # 保存文件
        if self.currentFile:
            self.saveToFile(self.currentFile)
        else:
            self.exportFile()

    def exportFile(self):  # 另存为文件（保存到文件也调用这个）
        filePath, _ = QFileDialog.getSaveFileName(
            self, "保存/另存为 Markdown 文件", "",
            "Markdown文件 (*.md *.markdown);;文本文件 (*.txt);;所有文件 (*)"
        )
        if filePath:
            self.saveToFile(filePath)
            self.currentFile = filePath
            self.updateWindowTitle()

    def saveToFile(self, filePath):  # 保存到文件
        file = QFile(filePath)
        if file.open(QFile.WriteOnly | QFile.Text):
            stream = QTextStream(file)
            stream << self.markdownInput.toPlainText()
            file.close()
            self.currentFile = filePath
            self.updateWindowTitle()

    def autoSave(self):
        if self.currentFile and self.markdownInput.document().isModified():
            self.saveToFile(self.currentFile)

    @staticmethod
    def getPrinter():
        printer = QPrinter()
        # 获取默认打印机名称
        default_printer = printer.printerName()
        # 获取所有可用打印机
        available_printers = QPrinter.availablePrinters()
        printer_names = [p.printerName() for p in available_printers]
        return default_printer, printer_names

    def printPreviewContent(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        dialog.setWindowTitle("打印 Markdown 内容")

        # 设置默认选项（可选）
        dialog.setOption(QPrintDialog.PrintToFile, False)
        dialog.setOption(QPrintDialog.PrintSelection, False)

        # 显示对话框，用户点击"确定"后打印
        if dialog.exec() == QPrintDialog.Accepted:
            self._printHTML(printer)

    def _printHTML(self, printer):
        html = self.previewLabel.text()
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)

    def updateWindowTitle(self):  # 按所求更改标题为文件路径，测试
        if self.currentFile:
            baseName = os.path.basename(self.currentFile)
            dirPath = os.path.dirname(self.currentFile)
            self.setWindowTitle(f"MPlus | {dirPath}/{baseName}")
        else:
            self.setWindowTitle("MPlus")

    def showAbout(self):  # 硬编码关于信息，太操蛋了
        dialog = QDialog(self)
        dialog.setWindowTitle("关于 MPlus Markdown PER")
        dialog.setFixedSize(420, 360)

        layout = QVBoxLayout()

        # 图标和标题
        titleLayout = QHBoxLayout()
        iconLabel = QLabel()

        if getattr(sys, 'frozen', False):
            os.chdir(os.path.dirname(sys.executable))
        else:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

        iconLabel.setPixmap(QIcon("_internal/ICON.ico").pixmap(48, 48))
        titleLayout.addWidget(iconLabel)

        titleLabel = QLabel("      MPlus Markdown PER")
        titleLabel.setStyleSheet("font-size: 24px; font-weight: bold;")
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch()
        layout.addLayout(titleLayout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #333337;")
        layout.addWidget(line)

        aboutText = """
        <p><b>构建版本：</b> Release 1.0 (2025年7月5日 构建)</p>
        <p>MPlus 是一个基于 Python 的开源 Markdown 编辑器。</p>

        <h4>|| 许可证声明 ||</h4>
        <p>
           MPlus采用 <a href="https://www.apache.org/licenses/LICENSE-2.0" style="color: #569cd6;">Apache License 2.0</a> 进行开源。
        </p>
        <p>
           Apache License 2.0 是一个宽松的开源许可证，其允许您自由地使用、复制、修改、分发和进行商业利用该项目。您只需要在您的产品或服务中保留原版权声明和许可证声明即可。
        </p>
        """

        infoLabel = QLabel(aboutText)
        infoLabel.setStyleSheet("font-size: 14px;")
        infoLabel.setWordWrap(True)
        infoLabel.setOpenExternalLinks(True)
        layout.addWidget(infoLabel)

        # GitHub链接
        githubLink = QLabel(
            '<a href="https://github.com/GongSunFangYun/MPlus/" style="color: #569cd6;">GitHub项目主页</a>')
        githubLink.setOpenExternalLinks(True)
        githubLink.setStyleSheet("font-size: 14px; margin-top: 10px;")
        layout.addWidget(githubLink, alignment=Qt.AlignLeft)

        # 版权信息
        copyrightLabel = QLabel("© 2024-2025 GongGunFangYun. All rights reserved.")
        copyrightLabel.setStyleSheet("font-size: 12px; color: #aaaaaa; margin-top: 15px;")
        layout.addWidget(copyrightLabel)

        # 关闭按钮
        buttonClose = QPushButton("关闭")
        buttonClose.clicked.connect(dialog.accept)
        buttonClose.setStyleSheet("""
            QPushButton {
                background-color: #333337;
                color: white;
                padding: 5px 15px;
                min-width: 80px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #094771;
            }
        """)
        layout.addWidget(buttonClose, alignment=Qt.AlignCenter)

        dialog.setLayout(layout)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #252526;
                color: white;
                padding: 15px;
            }
        """)
        dialog.exec()

    @staticmethod
    def showTutorial():  # Runoob的教程太好用了
        tutorialUrl = "https://www.runoob.com/markdown/md-tutorial.html"
        QDesktopServices.openUrl(QUrl(tutorialUrl))


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # 暗色主题
    darkPalette = QPalette()
    darkPalette.setColor(QPalette.Window, QColor("#252526"))
    darkPalette.setColor(QPalette.WindowText, Qt.white)
    darkPalette.setColor(QPalette.Base, QColor("#1e1e1e"))
    darkPalette.setColor(QPalette.Text, Qt.white)
    darkPalette.setColor(QPalette.Button, QColor("#333337"))
    darkPalette.setColor(QPalette.ButtonText, Qt.white)
    QApplication.setPalette(darkPalette)


    file_path = None
    if len(sys.argv) > 1:
        potential_file = sys.argv[1]
        if os.path.isfile(potential_file):
            file_path = potential_file

    window = MarkdownPreviewer(file_path)
    window.show()
    sys.exit(app.exec())