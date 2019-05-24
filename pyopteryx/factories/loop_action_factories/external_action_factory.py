from pyopteryx.factories.loop_action_factories.abstract_loop_action_factory import AbstractLoopActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task, add_synch_call_to_activity
from pyopteryx.utils.xml_utils import get_used_components, create_synch_call_name


class ExternalLoopActionFactory(AbstractLoopActionFactory):
    def __init__(self, action, xml_cache, input_data, processor, mapping_cache):
        super().__init__(action=action, xml_cache=xml_cache, input_data=input_data, processor=processor,
                         mapping_cache=mapping_cache)
        self.repository_components_cleaned = get_used_components(xml_cache.get_xml_tree(name="repository"),
                                                                 input_data=input_data)

    def add_action(self):
        activity = add_activity_to_task(task_activities=self.task_activities,
                                        activity_name=self.activity_name,
                                        host_demand_mean="0.0",
                                        hide_activity=True)
        called_service_id = self.action.get('calledService_ExternalService')

        synch_call_name = create_synch_call_name(called_service_id=called_service_id, activity=activity,
                                                 xml_cache=self.xml_cache, input_data=self.input_data,
                                                 uid_string=self.uid_string,
                                                 action=self.action,
                                                 mapping_cache=self.mapping_cache)

        add_synch_call_to_activity(activity=activity, synch_call_dest=synch_call_name)
        self._add_precedences(action=self.action,
                              task_activities=self.task_activities,
                              activity_name=self.activity_name)
