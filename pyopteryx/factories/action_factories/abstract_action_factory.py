from pyopteryx.utils.builder_utils import add_predecessor_precedence, add_successor_precedence
from pyopteryx.utils.xml_utils import get_by_id, get_action_type, check_and_retrieve_uid, \
    create_activity_name_from_action


class AbstractActionFactory:
    def __init__(self, action, task_activities, xml_cache, processor, mapping_cache):
        self.action = action
        self.processor = processor
        self.task = processor.find("task")
        self.entry_name = processor.find(".//entry").get("name")
        self.task_activities = task_activities
        self.task = processor.find("task")
        self.reply_entry = task_activities.find("./reply-entry")
        self.mapping_cache = mapping_cache
        self.uid_string = check_and_retrieve_uid(mapping_cache=mapping_cache, processor=processor)
        self.activity_name = create_activity_name_from_action(action=action, uid_string=self.uid_string)
        self.xml_cache = xml_cache

    def add_action(self):
        """
        Add action to processor.
        """
        pass

    def _add_precedences(self, action, task_activities, activity_name):
        """
        Add precedences for action depending on the type of action: normal and usage.
        :param action: current action
        :param task_activities: task_activities to add precedence to
        :param activity_name: parsed action name for precedence activity
        """
        # If action is usage action get predecessor from parameter "predecessor" and "successor"
        predecessor_abstract_action_id = action.get("predecessor_AbstractAction")
        successor_abstract_action_id = action.get("successor_AbstractAction")
        predecessor_action = get_by_id(element=self.xml_cache.get_xml_tree(name="repository"),
                                       element_id=predecessor_abstract_action_id)
        successor_action = get_by_id(element=self.xml_cache.get_xml_tree(name="repository"),
                                     element_id=successor_abstract_action_id)
        # If action has predecessor add precedence
        if predecessor_action is not None:
            action_type = get_action_type(predecessor_action)
            if action_type == 'SetVariableAction':  # should already have been created, pass
                pass
            else:
                add_predecessor_precedence(task_activities=task_activities,
                                           predecessor_action=predecessor_action,
                                           post_activity_name=activity_name,
                                           mapping_cache=self.mapping_cache)
        # If action has successor add precedence
        if successor_action is not None:
            action_type = get_action_type(successor_action)
            # skip SetVariableAction and take successor of SetVariableAction as successor of current action
            # SetVariableAction not supported by Peropteryx + LQNS, see documentation
            if action_type == 'SetVariableAction':
                second_level_successor_id = successor_action.get('successor_AbstractAction')
                second_level_successor = get_by_id(element=self.xml_cache.get_xml_tree(name="repository"),
                                                   element_id=second_level_successor_id)
                add_successor_precedence(task_activities=task_activities,
                                         successor_action=second_level_successor,
                                         pre_activity_name=activity_name,
                                         mapping_cache=self.mapping_cache)
            else:
                add_successor_precedence(task_activities=task_activities,
                                         successor_action=successor_action,
                                         pre_activity_name=activity_name,
                                         mapping_cache=self.mapping_cache)
