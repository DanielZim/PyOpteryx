from pyopteryx.factories.usage_action_factories.abstract_usage_action_factory import AbstractUsageActionFactory
from pyopteryx.utils.builder_utils import add_activity_to_task, add_synch_call_to_activity
from pyopteryx.utils.xml_utils import get_element_by_identifier, get_by_id, get_linkage_id, get_used_components, \
    get_parent_by_tag, get_unique_specification_string, is_part_of_composite_component


class EntryLevelSystemCallUsageActionFactory(AbstractUsageActionFactory):
    def __init__(self, action, xml_cache, input_data, processor, mapping_cache):
        super().__init__(action=action, xml_cache=xml_cache, input_data=input_data, processor=processor,
                         mapping_cache=mapping_cache)

    def add_action(self):
        activity = add_activity_to_task(task_activities=self.task_activities,
                                        activity_name=self.activity_name,
                                        hide_activity=True)
        self._add_synch_call(activity=activity, usage_action=self.action)
        self._add_precedences(action=self.action,
                              action_activity_name=self.activity_name)

    def add_loop_config(self):
        activity = add_activity_to_task(task_activities=self.task_activities,
                                        activity_name=self.activity_name,
                                        hide_activity=True)
        self._add_synch_call(activity=activity, usage_action=self.action)
        self._add_precedences(action=self.action,
                              action_activity_name=self.activity_name)

    def _add_synch_call(self, activity, usage_action):
        """
        Adds a synch-call to the given usage_action
        :param activity:
        :param usage_action:
        :return:
        """
        repository = self.xml_cache.get_xml_tree("repository")
        # Get id that links from current usage action to id of element with "signatures__OperationInterface"-tag
        component_repository_id = get_linkage_id(identifier="operationSignature__EntryLevelSystemCall",
                                                 element_tree=usage_action)
        # Get interface operation from element with "signatures__OperationInterface"-tag
        # that's id == component_repository_id
        interface_operation = get_by_id(element_id=component_repository_id, element=repository)
        operation_name = interface_operation.get("entityName")
        # Get the interface_name from interface's operation parent with tag "interfaces__Repository"
        # and get "entityName"
        interface = get_parent_by_tag(element=interface_operation, tag="interfaces__Repository")
        interface_name = interface.get("entityName")

        # Get component_name from parent element with tag "components__Repository" from
        # element that's "describedService__SEFF" == component_repository_id
        described_seff = None
        for component in get_used_components(self.xml_cache.get_xml_tree(name="repository"),
                                             input_data=self.input_data):
            described_seff = get_element_by_identifier(attribute="describedService__SEFF",
                                                       search_string=component_repository_id,
                                                       element_tree=component)
            if described_seff is not None:
                break

        component = get_parent_by_tag(element=described_seff, tag="components__Repository")
        synch_call_name = self.__create_synch_call_name(component=component, interface_name=interface_name,
                                                        operation_name=operation_name)
        add_synch_call_to_activity(activity=activity, synch_call_dest=synch_call_name)

    def __create_synch_call_name(self, component, interface_name, operation_name):
        """
        Creates a unique synch_call_name
        :param component:
        :param interface_name:
        :param operation_name:
        :return:
        """
        component_name = component.get("entityName")
        # If synch-call destination is type branch processor, find uid for that processor and add to synch call name
        type_named_reference = get_element_by_identifier(element_tree=self.action, attribute="referenceName",
                                                         search_string="type")
        if type_named_reference is not None:
            # Get child of sibling with tag = specification_VariableCharacterisation
            element = get_element_by_identifier(element_tree=type_named_reference.getparent(),
                                                attribute="type", search_string="TYPE")
            if element is None:
                element = get_element_by_identifier(element_tree=type_named_reference.getparent(),
                                                    attribute="type", search_string="VALUE")
            specification_variable = element.find(".//specification_VariableCharacterisation")
            uid = get_unique_specification_string(specification_variable.get("specification"))
            synch_call_name = '{component}_{interface}_{operation}_{uid}_Entry'.format(component=component_name,
                                                                                       interface=interface_name,
                                                                                       operation=operation_name,
                                                                                       uid=uid)
            return synch_call_name
        else:
            # Check is actions belongs to composite component, if true build processor name with self.uid_string to
            # link to corresponding processor
            composite_component = is_part_of_composite_component(element=component,
                                                                 components=self.xml_cache.get_xml_tree(
                                                                     "repository").findall(
                                                                     "./components__Repository"))
            if composite_component:
                processor_name_beginning = '{component}_{interface}_{operation}'.format(
                    component=component_name,
                    interface=interface_name,
                    operation=operation_name)
                for processor_name in self.mapping_cache["connector_mapping"].keys():
                    if processor_name_beginning in processor_name:
                        synch_call_name = '{processor_name}_Entry'.format(processor_name=processor_name)
                        return synch_call_name
                # # TODO: richtige UID bekommen!!!!!!
                # synch_call_name = '{component}_{interface}_{operation}_{uid_specification}_Entry'.format(
                #     component=component_name,
                #     interface=interface_name,
                #     operation=operation_name,
                #     uid_specification="#server5#")
                # return synch_call_name
            else:
                #  Simple Heuristics: Create synch_call_name and add synch-call to activity
                synch_call_name = '{component}_{interface}_{operation}_Entry'.format(component=component_name,
                                                                                     interface=interface_name,
                                                                                     operation=operation_name)
                return synch_call_name
