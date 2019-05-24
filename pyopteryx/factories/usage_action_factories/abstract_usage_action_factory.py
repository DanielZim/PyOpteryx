from pyopteryx.utils.builder_utils import add_predecessor_precedence, add_successor_precedence
from pyopteryx.utils.xml_utils import get_by_id, get_action_type, create_activity_name_from_action


class AbstractUsageActionFactory:
    def __init__(self, action, xml_cache, input_data, processor, mapping_cache=None):
        self.mapping_cache = mapping_cache
        self.action = action
        self.bound_to_entry = processor.find(".//entry").get("name")
        self.input_data = input_data
        self.processor = processor
        self.task_activities = processor.find(".//task-activities")
        self.xml_cache = xml_cache
        self.activity_name = create_activity_name_from_action(action=self.action)

    def add_action(self):
        """
        Add action to processor.
        """
        pass

    def add_loop_config(self):
        """
        Add actions to processor.
        :return:
        """
        pass

    def _add_precedences(self, action, action_activity_name):
        """
        Add precedences for action depending on the type of action: normal and usage.
        :param action: current action
        :param action_activity_name: parsed action name for precedence activity
        """
        predecessor_abstract_action_id = action.get("predecessor")
        successor_abstract_action_id = action.get("successor")
        predecessor_action = get_by_id(element=self.xml_cache.get_xml_tree(name="usagemodel"),
                                       element_id=predecessor_abstract_action_id)
        successor_action = get_by_id(element=self.xml_cache.get_xml_tree(name="usagemodel"),
                                     element_id=successor_abstract_action_id)
        # If action has predecessor add precedence
        if predecessor_action is not None:
            action_type = get_action_type(predecessor_action)
            if action_type == 'SetVariableAction':  # should already have been created, pass
                pass
            else:
                add_predecessor_precedence(task_activities=self.task_activities,
                                           predecessor_action=predecessor_action,
                                           post_activity_name=action_activity_name,
                                           mapping_cache=self.mapping_cache)
        # If action has successor add precedence
        if successor_action is not None:
            action_type = get_action_type(successor_action)
            if action_type == 'SetVariableAction':
                second_level_successor_id = successor_action.get('successor_AbstractAction')
                second_level_successor = get_by_id(element=self.xml_cache.get_xml_tree(name="repository"),
                                                   element_id=second_level_successor_id)
                add_successor_precedence(task_activities=self.task_activities,
                                         successor_action=second_level_successor,
                                         pre_activity_name=action_activity_name)
            else:
                add_successor_precedence(task_activities=self.task_activities,
                                         successor_action=successor_action,
                                         pre_activity_name=action_activity_name)
