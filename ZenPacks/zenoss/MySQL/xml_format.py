import xml.dom.minidom as minidom

def patch_minidom():
    def writexml_text(self, writer, indent='', addindent='', newl=''):
        text = self.data.strip()
        if text:
            minidom._write_data(writer, "%s%s%s"%(indent, text, newl))

    minidom.Text.writexml = writexml_text

def format_xml(filename):
    patch_minidom()
    xml = minidom.parse(filename)
    print xml.toprettyxml(indent='  ')

if __name__ == '__main__':
    format_xml('objects/objects.xml')
