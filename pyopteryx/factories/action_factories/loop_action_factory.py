from pyopteryx.factories.action_factories.abstract_action_factory import AbstractActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task, add_synch_call_to_activity


class LoopActionFactory(AbstractActionFactory):
    def __init__(self, action, task_activities, xml_cache, processor, mapping_cache):
        super().__init__(action=action, task_activities=task_activities, xml_cache=xml_cache, processor=processor,
                         mapping_cache=mapping_cache)

    def add_action(self):
        activity = add_activity_to_task(task_activities=self.task_activities,
                                        activity_name=self.activity_name,
                                        hide_activity=True)
        specification = self.action.find('iterationCount_LoopAction').get('specification')
        add_synch_call_to_activity(activity=activity,
                                   synch_call_dest='{}_Entry'.format(self.activity_name),
                                   calls_mean=specification)
        self._add_precedences(action=self.action,
                              task_activities=self.task_activities,
                              activity_name=self.activity_name)
