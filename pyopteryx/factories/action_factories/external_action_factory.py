from pyopteryx.factories.action_factories.abstract_action_factory import AbstractActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task, add_synch_call_to_activity, add_predecessor_precedence, \
    add_default_precedence, add_successor_precedence
from pyopteryx.utils.xml_utils import get_by_id, create_synch_call_name


class ExternalActionFactory(AbstractActionFactory):
    def __init__(self, action, task_activities, input_data, latency, xml_cache, mapping_cache,
                 processor):
        super().__init__(action=action, task_activities=task_activities, xml_cache=xml_cache, processor=processor,
                         mapping_cache=mapping_cache)
        self.processor_name = self.processor.get("name").replace("_Processor", "")
        self.action_id = action.get("id")
        self.input_data = input_data
        self.latency = latency

    def add_action(self):
        called_service_id = self.action.get("calledService_ExternalService")
        seff_on_server = self.input_data["component_connectors"][
            self.mapping_cache["connector_mapping"][self.processor_name]]

        # If called service service is a SEEF on current server
        # just create external call action
        if called_service_id in seff_on_server:
            activity = add_activity_to_task(task_activities=self.task_activities,
                                            activity_name=self.activity_name,
                                            hide_activity=True)
            synch_call_name = create_synch_call_name(called_service_id=called_service_id, activity=activity,
                                                     xml_cache=self.xml_cache, input_data=self.input_data,
                                                     uid_string=self.uid_string,
                                                     action=self.action,
                                                     mapping_cache=self.mapping_cache)
            add_synch_call_to_activity(activity=activity, synch_call_dest=synch_call_name)
            self._add_precedences(action=self.action,
                                  task_activities=self.task_activities,
                                  activity_name=self.activity_name)

        # If called service service is not a SEEF on current server, create activities:
        # - LAN_{External_action}_SYNCH
        # - LAN_{External_action}_return
        # - External_action
        else:
            activity = add_activity_to_task(task_activities=self.task_activities,
                                            activity_name=self.activity_name,
                                            hide_activity=True)
            self.__add_lan_activity(self.task_activities, "SYNCH")
            self.__add_lan_activity(self.task_activities, "return")
            synch_call_name = create_synch_call_name(called_service_id=called_service_id, activity=activity,
                                                     xml_cache=self.xml_cache, input_data=self.input_data,
                                                     uid_string=self.uid_string,
                                                     action=self.action,
                                                     mapping_cache=self.mapping_cache)

            add_synch_call_to_activity(activity=activity, synch_call_dest=synch_call_name)
            self._add_precedence_for_external_server_actions(action=self.action,
                                                             task_activities=self.task_activities,
                                                             external_call_action_name=self.activity_name)

    def __get_allocated_server(self, processor):
        """
        get cpu_rate and cpu_server_name on which the processor is located on
        :param processor:
        :return:
        """
        processor_name = processor.get("name").replace("_Processor", "")
        allocated_sever_id = self.mapping_cache["connector_mapping"][processor_name]
        allocated_cpu_server_name = self.mapping_cache["server_mapping"][allocated_sever_id]
        for server_id, server_name in self.mapping_cache["server_mapping"].items():
            if server_name == allocated_cpu_server_name:
                cpu_rate = self.input_data['cpu_rates'][server_id]
                return cpu_rate, allocated_cpu_server_name
        return ""

    def __add_lan_activity(self, task_activities, lan_type):
        """
        add LAN_{}_lan_type activity to task_activities of processor
        :param task_activities:
        :param lan_type:
        :return:
        """
        lan_activity_name = 'LAN_{activity_name}_{lan_type}'.format(activity_name=self.activity_name,
                                                                    lan_type=lan_type)
        lan_activity = add_activity_to_task(task_activities=task_activities,
                                            activity_name=lan_activity_name,
                                            hide_activity=True)
        add_synch_call_to_activity(activity=lan_activity, synch_call_dest=self.latency["SYNCH"])

    def _add_precedence_for_external_server_actions(self, action, task_activities, external_call_action_name):
        """
         Add precedences for external call actions that are allocated to a different cpu processor.
         There must be precedences:
            1. pre: predecessor -> post: ExternalCallAction_SYNCH
            2. pre: ExternalCallAction_SYNCH -> post: ExternalCallAction
            3. pre: ExternalCallAction -> post: ExternalCallAction_return
            4. pre: ExternalCallAction_return -> post: successor
        :param action: current ExternalCallAction element of repository
        :param task_activities: task_activities to add precedence to
        :param external_call_action_name: ExternalCallAction name
        """
        # ExternalCallAction_SYNCH name
        lan_synch_name = 'LAN_{}_SYNCH'.format(external_call_action_name)
        # ExternalCallAction_return name
        lan_return_name = 'LAN_{}_return'.format(external_call_action_name)
        # Add predecessor  precedence
        predecessor_action_id = action.get("predecessor_AbstractAction")
        predecessor_action = get_by_id(element=self.xml_cache.get_xml_tree("repository"),
                                       element_id=predecessor_action_id)
        if predecessor_action is not None:
            # add 1: predecessor -> SYNCH
            add_predecessor_precedence(task_activities=task_activities,
                                       predecessor_action=predecessor_action,
                                       post_activity_name=lan_synch_name,
                                       mapping_cache=self.mapping_cache)

        # add 2: SYNCH -> ExternalCall
        add_default_precedence(task_activities=task_activities,
                               pre_activity_name=lan_synch_name,
                               post_activity_name=external_call_action_name)

        # add 3: ExternalCall -> return
        add_default_precedence(task_activities=task_activities,
                               pre_activity_name=external_call_action_name,
                               post_activity_name=lan_return_name)

        # Add successor precedence
        successor_action_id = action.get("successor_AbstractAction")
        successor_action = get_by_id(element=self.xml_cache.get_xml_tree("repository"), element_id=successor_action_id)
        if successor_action is not None:
            # add 4: return -> successor
            add_successor_precedence(task_activities=task_activities,
                                     successor_action=successor_action,
                                     pre_activity_name=lan_return_name,
                                     mapping_cache=self.mapping_cache)
