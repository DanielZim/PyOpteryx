from pyopteryx.factories.loop_action_factories.abstract_loop_action_factory import AbstractLoopActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task


class StartLoopActionFactory(AbstractLoopActionFactory):
    def __init__(self, action, xml_cache, input_data, processor, mapping_cache):
        super().__init__(action=action, xml_cache=xml_cache, input_data=input_data, processor=processor,
                         mapping_cache=mapping_cache)

    def add_action(self):
        entry_name = self.processor.find(".//entry").get("name")
        add_activity_to_task(task_activities=self.task_activities,
                             activity_name=self.activity_name,
                             bound_to_entry=entry_name,
                             host_demand_mean="0.0",
                             hide_activity=True)
        self._add_precedences(action=self.action,
                              task_activities=self.task_activities,
                              activity_name=self.activity_name)
