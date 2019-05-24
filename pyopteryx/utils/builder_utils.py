from lxml.etree import SubElement

from pyopteryx.utils.xml_utils import get_allocated_cpu_rate_and_server_name, get_by_id, get_by_name, get_action_type, \
    get_entity_name, get_parent_by_tag, get_uid_from_action_name, check_if_precedence_exist, check_and_retrieve_uid
from pyopteryx.utils.scheduling_enum import Scheduling
from pyopteryx.utils.utils import string_int_to_string_float, remove_last_word, calculate_expression_string


def add_default_processor(xml_tree, processor_name):
    """
    Add processor to lqn-model tree.
    :param xml_tree: lqn-model tree
    :param processor_name: string
    :return: Created processor
    """
    processor = add_processor_element(xml_tree, processor_name=processor_name)
    task = add_task_to_processor(processor=processor)
    entry = add_entry_to_task(task=task, entry_name=processor_name)
    task_activities = SubElement(task, 'task-activities')
    reply_entry = SubElement(task_activities, 'reply-entry')
    entry_name = entry.get("name")
    reply_entry.set("name", entry_name)
    return processor


def add_reply_entry(processor, activity_name):
    """
    Set reply entry name to activity_name and create reply-activity.
    :param processor: processor to add reply entry to
    :param activity_name: string
    """
    reply_entry = processor.find(".//reply-entry")
    reply_activity = SubElement(reply_entry, 'reply-activity')
    reply_activity.set("name", activity_name)


def add_processor_element(xml_tree, processor_name, multiplicity="1", scheduling=Scheduling.FCFS, speed_factor=None,
                          quantum="0.001"):
    """
    Add processor with given id to xml tree. If "server" is in processor_name add additional parameter.
    :param xml_tree:
    :param speed_factor:
    :param scheduling:
    :param multiplicity:
    :param quantum:
    :param processor_name: <string> id of processor to create as string
    """
    processor_element = SubElement(xml_tree, 'processor')
    processor_element.set("multiplicity", multiplicity)
    processor_element.set("name", "{}_Processor".format(processor_name))
    if speed_factor:
        processor_element.set("speed-factor", speed_factor)
    if "cpu" in processor_name.lower():
        processor_element.set("scheduling", Scheduling.PS)
        processor_element.set("quantum", quantum)
    else:
        processor_element.set("scheduling", scheduling)
    return processor_element


def add_task_to_processor(processor, activity_graph="YES", multiplicity="1", scheduling="inf", think_time="0.0"):
    """
    Add task to processor with given processor element.
    :param think_time:
    :param scheduling:
    :param multiplicity:
    :param activity_graph:
    :param processor: processor xml element
    :return: created task element
    """
    task = SubElement(processor, 'task')
    task.set("activity-graph", activity_graph)
    task.set("multiplicity", multiplicity)
    task.set("name", "{}_Task".format(remove_last_word(processor.get('name'))))
    task.set("scheduling", scheduling)
    task.set("think-time", string_int_to_string_float(think_time))
    add_service_name_to_task(task)
    return task


def add_service_name_to_task(task, service_name="MyService"):
    """
    Add service name to task element.
    :param task: task element
    :param service_name: string
    :return: added service xml tag to task element
    """
    service_element = SubElement(task, 'service')
    service_element.set("name", service_name)


def add_entry_to_task(task, entry_name, entry_type="NONE", open_arrival_rate=None):
    """
    Add entry xml tag to task.
    :param task: task to add entry to
    :param entry_name: name
    :param entry_type: detault "NONE"
    :param open_arrival_rate: string
    :return: created entry
    """
    entry = SubElement(task, 'entry')
    entry.set("type", entry_type)
    entry.set("name", "{entry_name}_Entry".format(entry_name=entry_name))
    if open_arrival_rate:
        entry.set("open-arrival-rate", string_int_to_string_float(open_arrival_rate))
    return entry


def add_activity_to_entry(entry, activity_name, host_demand_mean="0.0", host_demand_cvsq=None, hide_activity=False):
    """
    Add activity element to entry.
    :param entry:
    :param activity_name:
    :param host_demand_mean:
    :param host_demand_cvsq:
    :param hide_activity:
    :return:
    """
    entry_phase_activities = SubElement(entry, 'entry-phase-activities')
    activity = SubElement(entry_phase_activities, 'activity')
    set_activity_name(activity, activity_name, hide_activity)
    activity.set("phase", "1")
    if host_demand_cvsq:
        activity.set("host-demand-cvsq", host_demand_cvsq)
    activity.set("host-demand-mean", host_demand_mean)


def set_activity_name(activity, activity_name, hide_activity):
    """
    Set name of activity element to activity_name. Hide '_Activity' if hide_activity is 'True'.
    :param activity: activity to set name
    :param activity_name: string
    :param hide_activity: Boolean
    :return:
    """
    if hide_activity:
        activity.set("name", "{activity_name}".format(activity_name=activity_name))
    elif not hide_activity:
        activity.set("name", "{activity_name}_Activity".format(activity_name=activity_name))


def add_synch_call_to_activity(activity, synch_call_dest, calls_mean="1.0"):
    """
    Add synch call to activity.
    :param calls_mean: default 1.0
    :param activity: activity to add synch call to
    :param synch_call_dest: destination for synch call
    """
    synch_call = SubElement(activity, 'synch-call')
    synch_call.set("dest", synch_call_dest)
    if calls_mean:
        if 'noOfEntries' in calls_mean:
            synch_call.set("calls-mean", "7.0")  # TODO: noOfEntries.VALUE aus file auslesen
        else:
            synch_call.set("calls-mean", calls_mean)


def add_activity_to_task(task_activities, activity_name, host_demand_mean="0.0", host_demand_cvsq=None,
                         hide_activity=False, bound_to_entry=None, phase=None):
    """
    Add activity to task.
    :param task_activities: current task ac
    :param activity_name: name of created activity
    :param host_demand_mean: used for cpu calculations
    :param host_demand_cvsq:
    :param hide_activity: <bool> hide "Activity" in created activity attribute name if TRUE
    :param bound_to_entry: first activity is bound to entry
    :param phase:
    """
    activity = SubElement(task_activities, 'activity')
    set_activity_name(activity, activity_name, hide_activity)
    # Add attributes, if specified as parameters
    if phase:
        activity.set("phase", phase)
    if host_demand_cvsq:
        activity.set("host-demand-cvsq", string_int_to_string_float(host_demand_cvsq))
    if host_demand_mean:
        activity.set("host-demand-mean", string_int_to_string_float(host_demand_mean))
    if bound_to_entry:
        activity.set("bound-to-entry", bound_to_entry)
    return activity


def add_predecessor_precedence(task_activities, predecessor_action, post_activity_name, mapping_cache=None):
    """
    Add precedence for actions' predecessor
    :param mapping_cache:
    :param task_activities: task_activities to add precedence to
    :param predecessor_action: predecessor action element from repository
    :param post_activity_name: activity name of post tag
    """
    predecessor_action_id = predecessor_action.get("id")
    predecessor_action_name = get_entity_name(predecessor_action)
    pre_activity_name = '{type}_{name}_{id}'.format(type=get_action_type(predecessor_action),
                                                    name=predecessor_action_name,
                                                    id=predecessor_action_id)
    if mapping_cache:
        uid = check_and_retrieve_uid(mapping_cache=mapping_cache,
                                     processor=get_parent_by_tag(element=task_activities, tag="processor"))
        if uid:
            pre_activity_name = '{type}_{name}_{id}_{uid}'.format(type=get_action_type(predecessor_action),
                                                                  name=predecessor_action_name,
                                                                  id=predecessor_action_id,
                                                                  uid=uid)
    add_default_precedence(task_activities=task_activities,
                           pre_activity_name=pre_activity_name,
                           post_activity_name=post_activity_name)


def add_default_precedence(task_activities, pre_activity_name, post_activity_name):
    """
    Add precedence if it does not already exists  to task_activities
    :param task_activities: task_activities element to add precedence to
    :param pre_activity_name: activity name for pre tag activity element
    :param post_activity_name: activity name for post tag activity element
    """
    existing_bool = check_if_precedence_exist(entry_phase_activities=task_activities,
                                              pre_activity_name=pre_activity_name,
                                              post_activity_name=post_activity_name)
    if not existing_bool:
        precedence = SubElement(task_activities, 'precedence')
        pre_tag_element = SubElement(precedence, 'pre')
        pre_activity = SubElement(pre_tag_element, 'activity')
        pre_activity.set("name", pre_activity_name)
        post_tag_element = SubElement(precedence, 'post')
        post_activity = SubElement(post_tag_element, 'activity')
        post_activity.set("name", post_activity_name)


def add_successor_precedence(task_activities, successor_action, pre_activity_name, mapping_cache=None):
    """
    Add precedence for actions' successor
    :param mapping_cache:
    :param task_activities: task_activities to add precedence to
    :param successor_action: successor action element from repository
    :param pre_activity_name: activity name of pre tag
    """
    successor_action_id = successor_action.get("id")
    successor_action_name = get_entity_name(successor_action)
    post_activity_name = '{type}_{name}_{id}'.format(type=get_action_type(successor_action),
                                                     name=successor_action_name,
                                                     id=successor_action_id)
    if mapping_cache:
        uid = check_and_retrieve_uid(mapping_cache=mapping_cache,
                                     processor=get_parent_by_tag(element=task_activities, tag="processor"))
        if uid:
            post_activity_name = '{type}_{name}_{id}_{uid}'.format(type=get_action_type(successor_action),
                                                                   name=successor_action_name,
                                                                   id=successor_action_id,
                                                                   uid=uid)
    # If ExternalCallAction is successor don't create precedences in order to avoid duplicated
    if "ExternalCallAction" not in post_activity_name:
        add_default_precedence(task_activities=task_activities,
                               pre_activity_name=pre_activity_name,
                               post_activity_name=post_activity_name)


def add_internal_actions_to_cpu(processor, mapping_cache, xml_tree, cpu_rates, repository):
    """
    If current processor has internal actions, add these internal actions to allocated cpu processor
    :param repository: repository file
    :param cpu_rates: dictionary of cpu processor names and cpu rate for example
    :param xml_tree: lqn-model tree
    :param mapping_cache: mapping_cache built in LqnBuilder
    :param processor: processor to add actions to
    :return:
    """
    # Only loop through processors that have task activities and therefore probably internal actions
    task_activities = processor.find(".//task-activities")
    if task_activities is not None:
        actions = task_activities.findall("activity")
        for action in actions:
            action_name = action.get("name")
            if "InternalAction" in action_name:
                cpu_rate, cpu_name = get_allocated_cpu_rate_and_server_name(processor=processor,
                                                                            mapping_cache=mapping_cache,
                                                                            cpu_rates=cpu_rates)
                # Get uid_string of processor and extract action id from internal action
                uid_string = check_and_retrieve_uid(mapping_cache=mapping_cache, processor=processor)
                action_id = get_uid_from_action_name(action_name=action_name, uid_string=uid_string)
                # Get action element in repository to get specification, that is needed for
                # calculating host-demand-mean
                repository_action = get_by_id(repository, element_id=action_id)
                specification = repository_action.find(".//specification_ParametericResourceDemand").get(
                    "specification")
                host_demand_mean = calculate_expression_string(input_string=specification,
                                                               processing_rate=cpu_rate)
                # Add internal action as entry to cpu processor with calculated host-demand-mean
                cpu_processor = get_by_name(element_name=cpu_name, element=xml_tree)
                entry = add_entry_to_task(task=cpu_processor.find("task"),
                                          entry_name=action_name,
                                          entry_type="PH1PH2")
                add_activity_to_entry(entry=entry,
                                      activity_name=action_name,
                                      host_demand_mean=host_demand_mean)
