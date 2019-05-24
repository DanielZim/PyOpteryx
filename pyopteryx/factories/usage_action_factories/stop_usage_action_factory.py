from lxml.etree import SubElement

from pyopteryx.factories.usage_action_factories.abstract_usage_action_factory import AbstractUsageActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task


class StopUsageActionFactory(AbstractUsageActionFactory):
    def __init__(self, action, xml_cache, input_data, processor):
        super().__init__(action=action, xml_cache=xml_cache, input_data=input_data, processor=processor)

    def add_action(self):
        add_activity_to_task(task_activities=self.task_activities,
                             activity_name=self.activity_name,
                             hide_activity=True)

    def add_loop_config(self):
        add_activity_to_task(task_activities=self.task_activities,
                             activity_name=self.activity_name,
                             hide_activity=True)
        reply_entry = self.task_activities.find("./reply-entry")
        reply_activity = SubElement(reply_entry, 'reply-activity')
        reply_activity.set("name", self.activity_name)
