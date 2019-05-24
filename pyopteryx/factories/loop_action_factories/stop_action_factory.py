from pyopteryx.factories.loop_action_factories.abstract_loop_action_factory import AbstractLoopActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task, add_reply_entry


class StopLoopActionFactory(AbstractLoopActionFactory):
    def __init__(self, action, xml_cache, input_data, processor, mapping_cache):
        super().__init__(action=action, xml_cache=xml_cache, input_data=input_data, processor=processor,
                         mapping_cache=mapping_cache)

    def add_action(self):
        add_activity_to_task(task_activities=self.task_activities,
                             activity_name=self.activity_name,
                             host_demand_mean="0.0",
                             hide_activity=True)
        add_reply_entry(processor=self.processor, activity_name=self.activity_name)
