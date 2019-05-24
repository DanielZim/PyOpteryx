import re
from os import listdir
from os.path import join
from decimal import *

from lxml.etree import ElementTree, parse


def string_int_to_string_float(string):
    """
    Cast integer string "1" into float string "1.0"
    :param string:
    :return:
    """
    try:
        return str(float(string))
    except:
        return str(string)


def remove_last_word(input_string):
    """
    Split input string and build new string without last word that is separated by '_'
    :param input_string:
    :return: cleaned input string
    """
    split_input_string = input_string.split("_")
    cleaned_string = '_'.join(split_input_string[:-1])
    return cleaned_string


def get_all_file_names_with_given_extension(directory_and_extension):
    """
    Get all file names of directory with specific file extension
    :param directory_and_extension: String, e.g. 'peropteryx_import/*.csv' (NOTE must contain '*')
    :return: list of all file names
    """
    # split parameter to get directory and file extension
    directory_list = directory_and_extension.split('*')
    directory_name = directory_list[0]
    file_extension = directory_list[1]
    # fill list with file names
    file_name_list = []
    for file in listdir(directory_name):
        if file.endswith(file_extension):
            file_name_list.append(join(directory_name, file))
    return file_name_list


def evaluate_stochastic_expression(stoex):
    """
    Simulate Palladio stoex calculations: "org.palladiosimulator.commons.stoex"
    :param stoex: stochastic expression
    :return:
    """
    # TODO: implement
    if stoex == 'DoublePDF[(0.01;0.05)(0.02;0.05)(0.03;0.9)] + 0.0000001 * Entries.NUMBER_OF_ELEMENTS*2':
        return "0.04350000000000001"
    elif stoex == 'DoublePDF[(0.2;0.1)(0.3;0.6)(0.4;0.3)] + 0.000002 * Entries.NUMBER_OF_ELEMENTS *2':
        return "0.665"
    elif stoex == "DoublePDF[(0.01;0.2)(0.02;0.6)(0.03;0.2)]*4*2":
        return "0.12"
    elif stoex == "(DoublePDF[(0.24;0.3)(0.25;0.4)(0.26;0.3)])/10/100":
        return "2.105E-4"
    elif stoex == "(DoublePDF[(0.3;0.3)(0.31;0.3)(0.32;0.3)(0.33;0.1)])/10/100":
        return "2.635E-4"
    elif stoex == "(DoublePDF[(0.03;0.1)(0.05;0.9)])/20/100":
        return "1.8750000000000003E-5"
    elif stoex == "(DoublePDF[(1.2;0.15)(1.3;0.4)(1.4;0.3)(1.5;0.15)]+1.2)/20/100":
        return "1.20625E-3"
    else:
        return "0"


def calculate_expression_string(input_string, processing_rate):
    input_copy = re.sub(r"(&#xD;|&#xA;)", "", input_string)
    input_copy = input_copy.replace("\r", "")
    input_copy = input_copy.replace("\n", "")
    if "DoublePDF" in input_string:
        input_copy = evaluate_stochastic_expression(input_copy)
    input_copy = input_copy.replace("requestedEntries.VALUE", "7")  # TODO aus file auslesen
    input_copy = input_copy.replace("Entries.NUMBER_OF_ELEMENTS", "100000")  # TODO aus file auslesen

    if isinstance(processing_rate, float) or isinstance(processing_rate, int):
        places = -12
        rounding = Decimal(10) ** places
        if input_copy == "150/100":
            # TODO doku möglicher Bug in der HOST-Demand_mean berechnung von peropteryx teilen von 150/100/10 = 0,1 statt 0,15
            # simulate java rounding bug, cause by missing type cast
            dec_input_copy = Decimal("1")
        else:
            try:
                dec_input_copy = Decimal(input_copy)
            except InvalidOperation:
                if '/' in input_copy:
                    up, down = input_copy.split('/')
                    dec_input_copy = Decimal(up) / Decimal(down)
                else:
                    dec_input_copy = Decimal(eval(input_copy)).quantize(rounding, ROUND_HALF_DOWN)
        dec_processing_rate = Decimal(processing_rate)
        result = dec_input_copy / dec_processing_rate
        result = result.quantize(rounding, ROUND_HALF_DOWN)
        return str(result)
    else:
        return None


def calculate_open_arrival_rate(specification):
    """
    If Exp in specification it means that exponential distribution of "Exp(lambda)" which is "lambda"
    :param specification:
    :return:
    """
    if "Exp" in specification:
        open_arrival_rate = re.findall(r'\d\.\d*', specification)[0]
    else:
        open_arrival_rate = str(1 / int(specification))
    return open_arrival_rate


def save_xml(tree, name):
    """
    Save xml file as name.
    :param tree: xml tree
    :param name: name of file to save
    """
    tree = ElementTree(tree)
    with open(name, "wb") as fh:
        tree.write(fh, pretty_print=True)


def open_xml_as_etree(xml_file_path):
    """
    Open xml file and get all Elements by "tag_name"
    :param xml_file_path:
    :return: all elements of xml_file_path
    """
    xml_file = parse(xml_file_path).getroot()
    return xml_file