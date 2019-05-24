from pyopteryx.factories.usage_action_factories.abstract_usage_action_factory import AbstractUsageActionFactory
from pyopteryx.utils.utils import string_int_to_string_float
from pyopteryx.utils.builder_utils import add_activity_to_task, add_synch_call_to_activity


class LoopUsageActionFactory(AbstractUsageActionFactory):
    def __init__(self, action, xml_cache, input_data, processor):
        super().__init__(action=action, xml_cache=xml_cache, input_data=input_data, processor=processor)

    def add_action(self):
        action_id = self.action.get("id")
        activity = add_activity_to_task(task_activities=self.task_activities,
                                        activity_name=self.activity_name,
                                        host_demand_mean="0.0",
                                        hide_activity=True)
        specification = string_int_to_string_float(self.action.find("loopIteration_Loop").get("specification"))
        synch_call_name = 'UsageScenario_Loop_{}_Entry'.format(action_id)
        add_synch_call_to_activity(activity=activity,
                                   synch_call_dest=synch_call_name,
                                   calls_mean=specification)
        self._add_precedences(action=self.action,
                              action_activity_name=self.activity_name)

    def add_loop_config(self):
        activity = add_activity_to_task(task_activities=self.task_activities,
                                        activity_name=self.activity_name,
                                        host_demand_mean="0.0",
                                        hide_activity=True)
        self._add_synch_call_to_loop_activity(activity=activity,
                                              usage=self.action)
        self._add_precedences(action=self.action,
                              action_activity_name=self.activity_name)

    @staticmethod
    def _add_synch_call_to_loop_activity(activity, usage):
        synch_call_name = 'UsageScenario_Loop_{}_Entry'.format(usage.get('id'))
        add_synch_call_to_activity(activity, synch_call_name, calls_mean=string_int_to_string_float(
            usage.find('.//loopIteration_Loop').get('specification')))
