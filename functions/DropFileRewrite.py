# 重写版本的拖拽导入

from PySide6.QtWidgets import (
    QTextEdit
)

class DragDropTextEdit(QTextEdit):
    def __init__(self, parent=None, load_callback=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.load_callback = load_callback

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.md', '.markdown', '.txt')):
                    if self.load_callback:
                        self.load_callback(file_path)
                    break
            event.acceptProposedAction()
        else:
            super().dropEvent(event)