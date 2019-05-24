from pyopteryx.factories.action_factories.abstract_action_factory import AbstractActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task
from pyopteryx.utils.xml_utils import is_in_element_tree


class StartActionFactory(AbstractActionFactory):
    def __init__(self, action, task_activities, xml_cache, processor, mapping_cache):
        super().__init__(action=action, task_activities=task_activities, xml_cache=xml_cache, processor=processor,
                         mapping_cache=mapping_cache)

    def add_action(self):
        # Check if processor's <task-activities> has already a StartAction
        has_start_action = is_in_element_tree(search_string="StartAction",
                                              attribute="name",
                                              element_tree=self.task_activities)
        # first start action must have bound to entry attribute
        if has_start_action is False:
            add_activity_to_task(task_activities=self.task_activities,
                                 activity_name=self.activity_name,
                                 hide_activity=True,
                                 bound_to_entry=self.entry_name)
        else:
            add_activity_to_task(task_activities=self.task_activities,
                                 activity_name=self.activity_name,
                                 hide_activity=True)
        self._add_precedences(action=self.action,
                              task_activities=self.task_activities,
                              activity_name=self.activity_name)
