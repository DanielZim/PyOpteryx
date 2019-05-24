from pyopteryx.factories.usage_action_factories.abstract_usage_action_factory import AbstractUsageActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task
from pyopteryx.utils.xml_utils import is_in_element_tree


class StartUsageActionFactory(AbstractUsageActionFactory):
    def __init__(self, action, xml_cache, input_data, processor):
        super().__init__(action=action, xml_cache=xml_cache, input_data=input_data, processor=processor)

    def add_action(self):
        # first stop action is reply-activity
        start_action_bool = is_in_element_tree(search_string="Start",
                                               attribute="name",
                                               element_tree=self.task_activities)
        # first start action is has bound_to_entry
        if not start_action_bool:
            add_activity_to_task(task_activities=self.task_activities,
                                 activity_name=self.activity_name,
                                 hide_activity=True,
                                 bound_to_entry=self.bound_to_entry)
        else:
            add_activity_to_task(task_activities=self.task_activities,
                                 activity_name=self.activity_name,
                                 hide_activity=True)

    def add_loop_config(self):
        add_activity_to_task(task_activities=self.task_activities,
                             activity_name=self.activity_name,
                             bound_to_entry=self.bound_to_entry,
                             hide_activity=True)
        self._add_precedences(action=self.action,
                              action_activity_name=self.activity_name)
