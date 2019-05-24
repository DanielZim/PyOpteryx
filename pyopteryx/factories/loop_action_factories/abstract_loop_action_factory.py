from pyopteryx.utils.builder_utils import add_predecessor_precedence, add_successor_precedence
from pyopteryx.utils.xml_utils import get_by_id, check_and_retrieve_uid, create_activity_name_from_action


class AbstractLoopActionFactory:
    def __init__(self, action, xml_cache, input_data, processor, mapping_cache):
        self.task_activities = processor.find(".//task-activities")
        self.xml_cache = xml_cache
        self.action = action
        self.processor = processor
        self.input_data = input_data
        self.mapping_cache = mapping_cache
        self.uid_string = check_and_retrieve_uid(mapping_cache=mapping_cache, processor=processor)
        self.activity_name = create_activity_name_from_action(action=action, uid_string=self.uid_string)

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
        # If action is normal action get predecessor from parameter
        # "predecessor_AbstractAction" and "successor_AbstractAction"
        predecessor_abstract_action_id = action.get("predecessor_AbstractAction")
        successor_abstract_action_id = action.get("successor_AbstractAction")
        predecessor_action = get_by_id(element=self.xml_cache.get_xml_tree("repository"),
                                       element_id=predecessor_abstract_action_id)
        successor_action = get_by_id(element=self.xml_cache.get_xml_tree("repository"),
                                     element_id=successor_abstract_action_id)
        # If action has predecessor add precedence
        if predecessor_action is not None:
            add_predecessor_precedence(task_activities=task_activities,
                                       predecessor_action=predecessor_action,
                                       post_activity_name=activity_name,
                                       mapping_cache=self.mapping_cache)
        # If action has successor add precedence
        if successor_action is not None:
            add_successor_precedence(task_activities=task_activities,
                                     successor_action=successor_action,
                                     pre_activity_name=activity_name,
                                     mapping_cache=self.mapping_cache)
