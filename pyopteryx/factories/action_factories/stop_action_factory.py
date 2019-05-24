from pyopteryx.factories.action_factories.abstract_action_factory import AbstractActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task, add_reply_entry
from pyopteryx.utils.xml_utils import is_part_of_branch


class StopActionFactory(AbstractActionFactory):
    def __init__(self, action, task_activities, xml_cache, processor, mapping_cache):
        super().__init__(action=action, task_activities=task_activities, xml_cache=xml_cache, processor=processor,
                         mapping_cache=mapping_cache)

    def add_action(self):
        add_activity_to_task(task_activities=self.task_activities,
                             activity_name=self.activity_name,
                             hide_activity=True)
        # first stop action is reply-activity
        if not is_part_of_branch(action=self.action):
            add_reply_entry(processor=self.processor, activity_name=self.activity_name)
