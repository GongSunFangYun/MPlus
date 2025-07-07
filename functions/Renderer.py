# 渲染MD内容，右侧那玩意
# 本质上还是QLabel套HTML渲染的，毕竟css可以直接用

import re

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
# pygments：代码高亮这一块👍

# noinspection RegExpRedundantEscape,PyBroadException
class MarkdownRenderer:
    def __init__(self):
        self.md = MarkdownIt(
            "commonmark",
            {
                "html": True,
                "linkify": True,
                "typographer": True,
                "highlight": self.highlightCode,
            }
        ).enable("table").enable("strikethrough")

        self.pygmentsFormatter = HtmlFormatter(
            style="monokai",
            noclasses=True,
            cssclass="codehilite",
            prestyles="margin: 0; padding: 0;"
        )

    def highlightCode(self, code, lang, _attrs):
        if not lang:
            lang = "text"
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
            return highlight(code, lexer, self.pygmentsFormatter)
        except:
            return f'<pre><code class="{lang}">{code}</code></pre>'

    def renderMarkdown(self, markdownText):
        processedText = self.preprocessSpecialStructures(markdownText)
        html = self.md.render(processedText)
        return self.postprocessHtml(html)

    def preprocessSpecialStructures(self, text):
        text = self.preprocessCodeBlocks(text)
        text = self.preprocessBlockquotes(text)
        return text

    def preprocessCodeBlocks(self, text):
        def replaceCodeBlock(match):
            lang = match.group(1) or "text"
            code = match.group(2)

            if '```' in code or '~~~' in code:
                return match.group(0)

            try:
                lexer = get_lexer_by_name(lang, stripall=True)
                return highlight(code, lexer, self.pygmentsFormatter)
            except:
                return f'<pre><code class="{lang}">{code}</code></pre>'

        text = re.sub(
            r'```([a-zA-Z0-9+-]*)\n((?:.(?!```$))*?.?)```',
            replaceCodeBlock,
            text,
            flags=re.DOTALL
        )

        text = re.sub(
            r'~~~([a-zA-Z0-9+-]*)\n((?:.(?!~~~$))*?.?)~~~',
            replaceCodeBlock,
            text,
            flags=re.DOTALL
        )

        return text

    @staticmethod
    def preprocessBlockquotes(text): # 这个也是一坨，直接硬算引用块缩进
        lines = text.split('\n')
        processed_lines = []
        current_block = []
        current_level = 0

        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                # 空行结束当前引用块
                if current_block:
                    processed_lines.append(f'[BLOCKQUOTE level={current_level}]{"\n".join(current_block)}[/BLOCKQUOTE]')
                    current_block = []
                processed_lines.append('')
                continue

            if stripped.startswith('>'):
                # 计算引用级别
                level = 0
                content = line
                while content.startswith('>'):
                    level += 1
                    content = content[1:].lstrip()

                # 新块或级别变化时刷新
                if current_block and level != current_level:
                    processed_lines.append(f'[BLOCKQUOTE level={current_level}]{"\n".join(current_block)}[/BLOCKQUOTE]')
                    current_block = []

                current_level = level
                current_block.append(content)
            else:
                # 非引用行，刷新当前块
                if current_block:
                    processed_lines.append(f'[BLOCKQUOTE level={current_level}]{"\n".join(current_block)}[/BLOCKQUOTE]')
                    current_block = []
                processed_lines.append(line)

        # 处理最后的块
        if current_block:
            processed_lines.append(f'[BLOCKQUOTE level={current_level}]{"\n".join(current_block)}[/BLOCKQUOTE]')

        return '\n'.join(processed_lines)

    @staticmethod
    def _flushBlockquote(output, block, level):
        if not block:
            return

        content = '\n'.join(block)
        output.append(f'[BLOCKQUOTE level={level}]{content}[/BLOCKQUOTE]')

    def postprocessHtml(self, html):
        # 先处理代码块
        html = re.sub(
            r'<div class="codehilite"><pre>',
            r'<div class="codehilite"><pre class="line-numbers">',
            html
        )

        # 确保所有BLOCKQUOTE标记都被处理
        while re.search(r'\[BLOCKQUOTE level=\d+\].*?\[/BLOCKQUOTE\]', html, re.DOTALL):
            html = re.sub(
                r'\[BLOCKQUOTE level=(\d+)\](.*?)\[/BLOCKQUOTE\]',
                self.wrapBlockquote,
                html,
                flags=re.DOTALL
            )

        return html

    def wrapBlockquote(self, match):
        level = int(match.group(1))
        content = match.group(2)

        # 清理可能残留的标记
        content = re.sub(r'\[/?BLOCKQUOTE[^\]]*\]', '', content)

        # 对引用内容单独进行Markdown渲染
        rendered_content = self.md.render(content)

        # 确保标题等元素没有外边距
        rendered_content = rendered_content.replace('<h1>', '<h1 style="margin:0;padding:0;">')
        rendered_content = rendered_content.replace('<h2>', '<h2 style="margin:0;padding:0;">')
        rendered_content = rendered_content.replace('<h3>', '<h3 style="margin:0;padding:0;">')

        return f'<blockquote class="level-{level}">{rendered_content}</blockquote>'
