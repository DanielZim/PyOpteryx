import re
from operator import attrgetter

from pyopteryx.utils.xml_utils import get_by_name


def precedence_error_check(tree):
    """
    Check if ExternalCallAction is part of LAN precedences. If true, delete precedence that includes ExternalCallAction
    without LAN calls
    :param tree: lqn-model tree
    """
    to_be_deleted = []
    task_activities = tree.findall(".//task-activities")
    for task_activity in task_activities:
        precedences = task_activity.findall(".//precedence")
        for precedence in precedences:
            pre = precedence.find('pre')
            post = precedence.find('post')
            if pre is not None and post is not None:
                post_activity = post.find('activity')
                post_name = post_activity.get('name')
                match = re.findall(r"(?<=LAN_ExternalCallAction_)(.*?)(?=_SYNCH)", post_name)
                if len(match) > 0:
                    unique_id = match[0]
                    for prec in precedences:
                        prec_pre = prec.find('pre')
                        prec_post = prec.find('post')
                        if prec_pre is not None and prec_post is not None:
                            prec_pre_activity = prec_pre.find('activity')
                            prec_post_activity = prec_post.find('activity')
                            prec_pre_name = prec_pre_activity.get('name')
                            prec_post_name = prec_post_activity.get('name')
                            if unique_id in prec_pre_name:
                                prec_pre_match = re.findall(r"(?<!LAN_)ExternalCallAction_{}".format(unique_id),
                                                            prec_pre_name)
                                if len(prec_pre_match) > 0:
                                    # all actions except LAN_ExternalCallAction as pre
                                    prec_post_match = re.findall(r"(?<!LAN_ExternalCall)Action_", prec_post_name)
                                    if len(prec_post_match) > 0:
                                        to_be_deleted.append(prec)
    for element in to_be_deleted:
        element.getparent().remove(element)


def sort_processor_elements(processor):
    """
    Sort all children of processor alphabetically
    :param processor: processor to sort
    :return: processor is sorted
    """
    task = processor.find("task")
    try:
        for child in task.findall("*"):
            child[:] = sorted(child, key=attrgetter("tag"))
    except AttributeError:
        pass


def delete_unused_processors(mapping_cache, xml_tree):
    """
    Check all entries of component interface processors if they are used as "dest" if not,
    delete this processor since it is not used.
    :param mapping_cache: mapping_cache built in LqnBuilder
    :param xml_tree: lqn-model tree
    """
    # Loop through all component interface processors and delete unused ones
    for processor_name in mapping_cache["connector_mapping"].keys():
        processor = get_by_name(element=xml_tree,
                                element_name='{processor_name}_Processor'.format(processor_name=processor_name))
        entry = processor.find(".//entry")
        if entry is not None:
            entry_name = entry.get("name")
            amount_usages = len(
                xml_tree.findall('''.//*[@dest='{search_string}']'''.format(search_string=entry_name)))
            # Delete processor if entry is not used
            if amount_usages == 0:
                xml_tree.remove(processor)
