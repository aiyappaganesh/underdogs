class CenteredContents():
    def __init__(self, height, padding_left, contents, table_cell=True):
        self.height = height
        self.padding_left = padding_left
        self.contents = contents
        self.table_cell = table_cell

class CenteredContent():
    def __init__(self, copy, css, component=None):
        self.copy = copy
        self.css_classes = css
        self.component = component
