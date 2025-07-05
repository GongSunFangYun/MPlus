# MD语法高亮

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QFont, QTextCharFormat, QSyntaxHighlighter, QColor
)


class MarkdownHighlighter(QSyntaxHighlighter):

    def __init__(self, document):
        super().__init__(document)
        self.highlightingRules = []
        self.initHighlightRules()

    def initHighlightRules(self):
        """初始化高亮规则"""
        # 颜色配置
        colors = {
            'heading': QColor("#569cd6"),
            'codeText': QColor("#ce9178"),
            'codeBg': QColor("#252525"),
            'link': QColor("#3794ff"),
            'emphasis': QColor("#d7ba7d"),
            'italic': QColor("#b5cea8"),
            'list': QColor("#c586c0"),
            'quote': QColor("#6a9955"),
            'image': QColor("#4ec9b0"),
            'html': QColor("#d7ba7d")
        }

        # 标题规则
        headerFormat = QTextCharFormat()
        headerFormat.setForeground(colors['heading'])
        headerFormat.setFontWeight(QFont.Bold)
        for level in range(1, 7):
            pattern = QRegularExpression(f"^#{{{level}}}\\s.*")
            self.highlightingRules.append((pattern, headerFormat))

        # 引用规则 - 修改后的版本
        blockquoteFormat = QTextCharFormat()
        blockquoteFormat.setForeground(colors['quote'])
        # 修改正则表达式以匹配任意数量的>符号
        self.highlightingRules.append((
            QRegularExpression("^>+\\s.*"),  # 匹配1个或多个>开头的行
            blockquoteFormat
        ))

        # 代码块
        codeBlockFormat = QTextCharFormat()
        codeBlockFormat.setForeground(colors['codeText'])
        codeBlockFormat.setBackground(colors['codeBg'])
        self.highlightingRules.append((
            QRegularExpression("```[\\s\\S]*?```|~~~[\\s\\S]*?~~~"),
            codeBlockFormat
        ))

        # 行内代码
        inlineCodeFormat = QTextCharFormat()
        inlineCodeFormat.setForeground(colors['codeText'])
        inlineCodeFormat.setBackground(colors['codeBg'])
        self.highlightingRules.append((
            QRegularExpression("`[^`]+`"),
            inlineCodeFormat
        ))

        # 强调文本
        emphasisFormat = QTextCharFormat()
        emphasisFormat.setFontWeight(QFont.Bold)
        emphasisFormat.setForeground(colors['emphasis'])
        self.highlightingRules.append((
            QRegularExpression("\\*\\*[^\\*]+\\*\\*|__[^_]+__"),
            emphasisFormat
        ))

        # 斜体文本
        italicFormat = QTextCharFormat()
        italicFormat.setFontItalic(True)
        italicFormat.setForeground(colors['italic'])
        self.highlightingRules.append((
            QRegularExpression("\\*[^\\*]+\\*|_[^_]+_"),
            italicFormat
        ))

        # 链接
        linkFormat = QTextCharFormat()
        linkFormat.setForeground(colors['link'])
        linkFormat.setFontUnderline(True)
        self.highlightingRules.append((
            QRegularExpression("\\[[^\\]]+\\]\\([^\\)]+\\)"),
            linkFormat
        ))

        # 图片
        imageFormat = QTextCharFormat()
        imageFormat.setForeground(colors['image'])
        self.highlightingRules.append((
            QRegularExpression("!\\[[^\\]]+\\]\\([^\\)]+\\)"),
            imageFormat
        ))

        # 列表
        listFormat = QTextCharFormat()
        listFormat.setForeground(colors['list'])
        self.highlightingRules.append((
            QRegularExpression("^[\\*\\+-]\\s|^\\d+\\.\\s"),
            listFormat
        ))

        # 引用
        blockquoteFormat = QTextCharFormat()
        blockquoteFormat.setForeground(colors['quote'])
        self.highlightingRules.append((
            QRegularExpression("^>\\s.*"),
            blockquoteFormat
        ))

        # HTML标签
        htmlFormat = QTextCharFormat()
        htmlFormat.setForeground(colors['html'])
        self.highlightingRules.append((
            QRegularExpression("<[^>]+>"),
            htmlFormat
        ))

    def highlightBlock(self, text):
        """高亮文本块"""
        for pattern, fmt in self.highlightingRules:
            matchIterator = pattern.globalMatch(text)
            while matchIterator.hasNext():
                match = matchIterator.next()
                self.setFormat(
                    match.capturedStart(),
                    match.capturedLength(),
                    fmt
                )