import glob
import os
from operator import attrgetter

import lxml.etree as le


# Function to sort XML elements by id
#  (where the elements have an 'id' attribute that can be cast to an int)
def sortbyname(elem):
    name = elem.get('name')
    if name:
        try:
            return name
        except ValueError:
            return ''
    return ''


# Function to sort XML attributes alphabetically by key
#  The original item is left unmodified, and it's attributes are
#  copied to the provided sorteditem
def sortAttrs(item, sorteditem):
    attrkeys = sorted(item.keys())
    for key in attrkeys:
        sorteditem.set(key, item.get(key))


# Function to sort XML elements
#  The sorted elements will be added as children of the provided newroot
#  This is a recursive function, and will be called on each of the children
#  of items.
def sortElements(items, newroot):
    # The intended sort order is to sort by XML element name
    #  If more than one element has the same name, we want to
    #   sort by their text contents.
    #  If more than one element has the same name and they do
    #   not contain any text contents, we want to sort by the
    #   value of their ID attribute.
    #  If more than one element has the same name, but has
    #   no text contents or ID attribute, their order is left
    #   unmodified.
    #
    # We do this by performing three sorts in the reverse order
    items = sorted(items, key=sortbyname)
    items = sorted(items, key=attrgetter('tag'))

    # Once sorted, we sort each of the items
    for item in items:
        # Create a new item to represent the sorted version
        #  of the next item, and copy the tag name and contents
        newitem = le.Element(item.tag)
        if item.text and item.text.isspace() == False:
            newitem.text = item.text

        # Copy the attributes (sorted by key) to the new item
        sortAttrs(item, newitem)

        # Copy the children of item (sorted) to the new item
        sortElements(list(item), newitem)

        # Append this sorted item to the sorted root
        newroot.append(newitem)


# Function to sort the provided XML file
#  fileobj.filename will be left untouched
#  A new sorted copy of it will be created at fileobj.tmpfilename
def sortFile(file_name, tmp_path):
    with open(file_name, 'r') as original:
        # parse the XML file and get a pointer to the top
        xmldoc = le.parse(original)
        xmlroot = xmldoc.getroot()

        # create a new XML element that will be the top of
        #  the sorted copy of the XML file
        newxmlroot = le.Element(xmlroot.tag)

        # create the sorted copy of the XML file
        sortAttrs(xmlroot, newxmlroot)
        sortElements(list(xmlroot), newxmlroot)

        # write the sorted XML file to the temp file
        newtree = le.ElementTree(newxmlroot)
        with open(tmp_path, 'wb') as newfile:
            newtree.write(newfile, pretty_print=True)


# file_name_orig = "pcm2lqn-2019-01-18-181952.in.lqxo"
file_name_orig = "original_vorlage.xml"

test_xml_path_orig = "original.xml"

output_folder = os.path.normpath('C:\Output')
list_of_files = glob.glob('{}/*.in.lqxo'.format(output_folder))  # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
sorted_latest = "latest.xml"

sortFile(file_name_orig, tmp_path=test_xml_path_orig)
sortFile(latest_file, tmp_path=sorted_latest)


# TODO compare via https://www.corefiling.com/opensource/xmldiff/
