from lxml.etree import ElementTree


# Get functions
def get_allocated_cpu_rate_and_server_name(processor, mapping_cache, cpu_rates):
    """
    Get allocated cpu_rate and server_name for processor
    :param cpu_rates: dictionary of cpu processor names and cpu rate for example
    :param mapping_cache: mapping_cache built in LqnBuilder
    :param processor: processor element
    :return:
    """
    processor_name = processor.get("name").replace("_Processor", "")
    # connector_mapping maps processor_name to allocated_server_id
    allocated_sever_id = mapping_cache["connector_mapping"][processor_name]
    # server_mapping maps server_id to server_name
    allocated_cpu_server_name = mapping_cache["server_mapping"][allocated_sever_id]
    # Get cpu rate for current example from cpu_rates dictionary that maps server id to cpu rate of this server
    for server_id, server_name in mapping_cache["server_mapping"].items():
        if server_name == allocated_cpu_server_name:
            cpu_rate = cpu_rates[server_id]
            return cpu_rate, allocated_cpu_server_name
    return None, None


def get_by_tag_name(element, tag):
    """
    Get elements by tag name.
    :param element: element
    :param tag: tag string
    :return: list of elements that matches tag
    """
    results = []
    for child in element.findall('.//'):
        if tag in child.tag:
            results.append(child)
    return results


def get_element_by_identifier(attribute, search_string, element_tree):
    """
    Get element by attribute and string.
    :param attribute: string of attribute type
    :param search_string: identifying string to look for
    :param element_tree: element tree to look in
    :return: found element
    """
    return element_tree.find(
        '''.//*[@{attribute}='{search_string}']'''.format(attribute=attribute, search_string=search_string))


def get_by_id(element, element_id):
    """
    Get element by id.
    :param element: parent element
    :param element_id: element id
    :return: element
    """
    return get_element_by_identifier(attribute="id", search_string=element_id, element_tree=element)


def get_by_name(element, element_name):
    """
    Get element by name
    :param element: parent element
    :param element_name: name string
    :return: element
    """
    return get_element_by_identifier(attribute="name", search_string=element_name, element_tree=element)


def get_action_type(action):
    """
    Get action type as string.
    :param action: action element
    :return: string action type
    """
    action_type = action.get(get_xml_schema_type())
    if action_type:
        if "InternalAction" in action_type:
            return 'InternalAction'
        elif "StartAction" in action_type:
            return 'StartAction'
        elif "StopAction" in action_type:
            return 'StopAction'
        elif "BranchAction" in action_type:
            return 'BranchAction'
        elif "EntryLevelSystemCall" in action_type:
            return "EntryLevelSystemCall"
        elif "Start" in action_type:
            return "Start"
        elif "Stop" in action_type:
            return "Stop"
        elif "ExternalCallAction" in action_type:
            return 'ExternalCallAction'
        elif "Loop" in action_type:
            return 'LoopAction'
        elif "SetVariableAction" in action_type:
            return 'SetVariableAction'
    else:
        return None


def get_linkage_id(identifier, element_tree):
    """
    Get id to linking element from "href" attribute
    :param identifier: identifier of element to look in
    :param element_tree: current element tree
    :return: id
    """
    linkage_id = element_tree.find('.//{}'.format(identifier)).get("href").split("#")[1]
    return linkage_id


def get_entity_name(entity):
    """
    Get entity name of given entity. If no "entityName" is specified return "aName".
    :param entity: entity element
    :return: entity_name
    """
    entity_name = entity.get("entityName")
    if not entity_name:
        entity_name = "aName"
    return entity_name


def get_used_components(repository_tree, input_data):
    """
    Get repository components from "components__Repository" and only load components that correspond with assembled
    components of input data
    :return: all used components from repository as list
    """
    used_component = []
    repository_components = repository_tree.findall("./components__Repository")
    for repository_component in repository_components:
        repository_component_id = repository_component.get("id")
        if repository_component_id not in input_data["excluded_components"]:
            used_component.append(repository_component)
    return used_component


def get_element_from_list(attribute, search_string, element_list):
    """
    Get element by attribute and string.
    :param attribute: string of attribute type
    :param search_string: identifying string to look for
    :param element_list: element tree to look in
    :return: found element
    """
    for element in element_list:
        if search_string == element.get(attribute):
            return element
    return None


def get_xml_schema_type():
    """
    Get xml schema type.
    """
    return '{http://www.w3.org/2001/XMLSchema-instance}type'


def get_parent_by_tag(element, tag):
    """
    Get parent of element by tag name.
    :param element: child element
    :param tag: tag of parent element
    :return: parent element
    """
    parent = element.getparent()
    if tag == parent.tag:
        return parent
    else:
        return get_parent_by_tag(parent, tag)


def get_branch_type(branch):
    """
    Get branch type for branch. Type can be detailed, type, simple or probabilistic
    :param branch: branch element
    :return: branch type
    """
    branch_type = branch.get(get_xml_schema_type())
    if "GuardedBranchTransition" in branch_type:
        branch_conditions = branch.findall(".//branchCondition_GuardedBranchTransition")
        for condition in branch_conditions:
            branch_condition = condition.get("specification").replace(" ", "")
            if "isDetailed.VALUE==" in branch_condition:
                return "detailed"
            elif "type.VALUE==" in branch_condition:
                return "type"
            else:
                return "simple"
    else:
        return "probabilistic"


def get_branch_condition(branch):
    """
    Extract branchCondition_GuardedBranchTransition from specification, e.g.
    "type.VALUE == &quot;graphical&quot;" -> "#graphical"
    :param branch: "branches_Branch"
    :return: extracted condition string
    """
    branch_condition = branch.find("./branchCondition_GuardedBranchTransition").get(
        "specification").split("==")[-1].replace('"', "").replace(" ", "")
    branch_condition = '#{condition}#'.format(condition=branch_condition)
    return branch_condition


def get_unique_specification_string(specification):
    """
    Extract branchCondition_GuardedBranchTransition from specification, e.g.
    "type.VALUE == &quot;graphical&quot;" -> "#graphical"
    :return: extracted condition string
    """
    replaceable_characters = ['\r', '\n', '\"', ' ']
    result = specification
    for replaceable_character in replaceable_characters:
        result = result.replace(replaceable_character, "")
    result = '#{condition}#'.format(condition=result)
    return result


def get_uid_from_action_name(action_name, uid_string=None):
    """
    Extract id from action name by splitting at "__", because this marks the start of id in action name.
    If uid string is in action name, remove it
    :param action_name: full action name of processor (e.g. "{action_type}_{aName}_{id}[uid_string}]"
    :param uid_string: uid_string
    :return: {id}
    """
    if uid_string:
        cleaned_name = action_name.replace("_{uid_string}".format(uid_string=uid_string), "")
        return '_{}'.format(cleaned_name.split("__")[-1])
    else:
        return '_{}'.format(action_name.split("__")[-1])


# Check functions
def is_in_element_tree(attribute, search_string, element_tree):
    """
    Check if element is in element tree.
    :param attribute: string attribute type
    :param search_string: string to search for
    :param element_tree: tree to search in
    :return:
    """
    for element in element_tree:
        if attribute in element.attrib:
            if search_string in element.get(attribute):
                return True
    return False


def check_if_precedence_exist(entry_phase_activities, pre_activity_name, post_activity_name):
    """
    Checks if precedence already exist in task_activities returns True if precedence exists and false if
    it does not exist
    :param entry_phase_activities: task_activities element to add precedence to
    :param pre_activity_name: activity name for pre tag activity element
    :param post_activity_name: activity name for post tag activity element
    :return: Boolean
    """
    precedences = ElementTree(entry_phase_activities).findall("./precedence")
    if len(precedences) == 0:
        return False
    else:
        for existing_precedence in precedences:
            # try to get name from pre tag.
            try:
                pre_tag = existing_precedence.find("pre").find("activity").get("name")
            except AttributeError:
                # pre tag does not exist in precedence -> precedence does not exist yet
                pre_tag = None  # return False
            if pre_tag:
                # try to get name from post tag.
                try:
                    post_tag = existing_precedence.find("post").find("activity").get("name")
                except AttributeError:
                    post_tag = None  # return False
                # precedence has normal pre and post tag. Now compare the names to the new names that
                # should be created
                if pre_tag and post_tag:
                    # If names are the same the precedence already exists
                    if pre_tag == pre_activity_name and post_tag == post_activity_name:
                        return True
    return False


def is_part_of_composite_component(element, components):
    """
    Check if element is part of CompositeComponent
    :param element: element of repository
    :param components: repository components
    :return: Boolean
    """
    if element.tag != "components__Repository":
        parent = get_parent_by_tag(element=element, tag="components__Repository")
        parent_id = parent.get("id")
        for component in components:
            if "CompositeComponent" in component.get(get_xml_schema_type()):
                for assembly_context in component.findall("assemblyContexts__ComposedStructure"):
                    if parent_id == assembly_context.get("encapsulatedComponent__AssemblyContext"):
                        return True
    else:
        for component in components:
            if "CompositeComponent" in component.get(get_xml_schema_type()):
                for assembly_context in component.findall("assemblyContexts__ComposedStructure"):
                    if element.get("id") == assembly_context.get("encapsulatedComponent__AssemblyContext"):
                        return True
    return False


def copy_branch_check(branch_action):
    """
    Check if branch actions requires a copyied processor by checking the first "branches_Branch" type
    :param branch_action: branch action
    :return: Boolean
    """
    branch = branch_action.find("./branches_Branch")
    branch_type = get_branch_type(branch)
    if branch_type == "type":
        return True
    else:
        return False


def copy_external_check(external_action):
    """
    Check if branch actions requires a copied processor by checking the first "branches_Branch" type
    :param external_action: branch action
    :return: Boolean
    """
    try:
        type_named_reference = get_element_by_identifier(element_tree=external_action, attribute="referenceName",
                                                         search_string="type")
        if type_named_reference is not None:
            # Get child of sibling with tag = specification_VariableCharacterisation
            specification_variable = type_named_reference.getparent().find(".//specification_VariableCharacterisation")
            uid_specification = get_unique_specification_string(specification_variable.get("specification"))
            return True, uid_specification
    except AttributeError:
        pass
    return False, None


def check_and_retrieve_uid(mapping_cache, processor):
    """
    Check if processor name has uid, if true: return uid.
    :param mapping_cache: mapping_cache built in LqnBuilder
    :param processor: processor to check check for uid string
    :return: uid string
    """
    processor_list = create_processor_uid_mapping(mapping_cache=mapping_cache)
    if processor.get("name").replace("_Processor", "") in processor_list.keys():
        uid = processor_list[processor.get("name").replace("_Processor", "")]  # returns uid
        return uid
    return None


def is_part_of_branch(action):
    """
    Checks if action is part of branch action.
    :return: Boolean
    """
    try:
        branch_action = get_parent_by_tag(element=action, tag="steps_Behaviour")
    except AttributeError:  # parent with tag="steps_Behaviour" cannot be found --> is not in branch
        return False
    if branch_action is None:
        return False
    return True


# Create functions
def create_processors_for_composite_components(processor_name, processors_to_add, seff, cache, input_data,
                                               mapping_cache):
    """
    Check if current seff belongs to component that is part of CompositeComponent, if true: create corresponding
    processor names and add to processors_to_add.
    :param processor_name: Created processor name
    :param processors_to_add: list of processor names that must be created
    :param seff: current service effect specification
    :param cache: cached PCM files
    :param input_data: input containing cpu rates, allocation of components and assembled components
    :param mapping_cache: mapping_cache built in LqnBuilder
    :return: :return: list of processor names that must be created.
    """
    if not processors_to_add:
        if is_part_of_composite_component(element=seff, components=cache.get_xml_tree("repository").findall(
                ".//components__Repository")):
            component_id = get_parent_by_tag(element=seff, tag="components__Repository").get("id")
            allocated_server_ids = []
            allocated_server_ids = create_server_uids(allocated_server_ids=allocated_server_ids,
                                                      component_id=component_id, cache=cache,
                                                      composite_component_allocation=input_data[
                                                          "composite_component_allocation"])
            for server_uid in allocated_server_ids:
                uid = '#{uid}#'.format(uid=server_uid)
                unique_processor_name = '{processor_name}_{uid}'.format(processor_name=processor_name, uid=uid)
                mapping_cache["composite_uid_mapping"][unique_processor_name] = uid
                processors_to_add.append(unique_processor_name)
    return processors_to_add


def create_processors_for_external_actions(processor_name, processors_to_add, seff):
    """
    If current seff contains a ExternalCallAction, check if copying processor is required, if true: create corresponding
    processor names and add to processors_to_add. If ExternalCallAction does not require creation of multiple processors
    the returned list is empty.
    :param processor_name: Created processor name
    :param processors_to_add: list of processor names that must be created
    :param seff: current service effect specification
    :return: :return: list of processor names that must be created.
    """
    if not processors_to_add:
        for action in seff.findall("./steps_Behaviour"):
            action_type = get_action_type(action=action)
            if action_type == "ExternalCallAction":
                mandatory_to_copy, uid_specification = copy_external_check(external_action=action)
                if mandatory_to_copy:
                    external_processor_name = '{processor_name}_{uid_specification}'.format(
                        processor_name=processor_name,
                        uid_specification=uid_specification)
                    processors_to_add.append(external_processor_name)
    return processors_to_add


def create_processor_names_for_branch_action(processor_name, processors_to_add, seff, mapping_cache):
    """
    If current seff contains a BranchAction, check if copying processor is required, if true: create corresponding
    processor names and add to processors_to_add. If branch action does not require creation of multiple processors
    the returned list is empty.
    :param mapping_cache: mapping_cache built in LqnBuilder
    :param processor_name: Created processor name
    :param processors_to_add: list of processor names that must be created
    :param seff: current service effect specification
    :return: list of processor names that must be created.
    """
    for action in seff.findall("./steps_Behaviour"):
        action_type = get_action_type(action=action)
        if action_type == "BranchAction":
            mandatory_to_copy_branch = copy_branch_check(branch_action=action)
            if mandatory_to_copy_branch:
                for branch in action.findall("./branches_Branch"):
                    branch_uid = get_branch_condition(branch=branch)
                    branch_processor_name = '{processor_name}_{condition}'.format(processor_name=processor_name,
                                                                                  condition=branch_uid)
                    mapping_cache["branch_mapping"][branch.get("id")] = {branch_processor_name: branch_uid}
                    mapping_cache["is_detailed"][processor_name].update({branch_uid: False})
                    processors_to_add.append(branch_processor_name)
    return processors_to_add


def create_activity_name_from_action(action, uid_string=None):
    """
    Create activity name from action of format "{type}_{name}_{id}"
    :param uid_string:
    :param action: action element
    :return: activity name
    """
    action_type = get_action_type(action=action)
    action_name = get_entity_name(action)
    action_id = action.get("id")
    if uid_string:
        activity_name = '{type}_{name}_{id}_{uid_string}'.format(type=action_type, name=action_name, id=action_id,
                                                                 uid_string=uid_string)
    else:
        activity_name = '{type}_{name}_{id}'.format(type=action_type, name=action_name, id=action_id)
    return activity_name


def create_processor_uid_mapping(mapping_cache):
    """
    Create dictionary that maps processor name to uid
    :param mapping_cache: mapping_cache built in LqnBuilder
    :return: mapping for processor to uid
    """
    processor_uid_mapping = {}
    # Get uid mappings from mapping_cache
    branch_mapping = mapping_cache["branch_mapping"]
    loop_uid_mapping = mapping_cache["loop_uid_mapping"]
    composite_uid_mapping = mapping_cache["composite_uid_mapping"]
    # Add mappings to processor_uid_mapping
    for branch_id, processor_dict in branch_mapping.items():
        processor_uid_mapping.update(processor_dict)
    processor_uid_mapping.update(loop_uid_mapping)
    processor_uid_mapping.update(composite_uid_mapping)
    return processor_uid_mapping


def create_server_uids(allocated_server_ids, component_id, composite_component_allocation, cache):
    """

    :param allocated_server_ids:
    :param component_id:
    :param composite_component_allocation:
    :param cache:
    :return:
    """
    if component_id in composite_component_allocation.keys():
        # Get allocated server for component_id
        for server_id in composite_component_allocation[component_id]:
            allocated_server_ids.append(server_id)
    # Length 'composite_component_alocation' mapping == 1 if all CompositeComponents
    # are located on same server If true: loop over amount of CompositeComponents and
    # create uids by adding loop counter to allocated server name
    if len(allocated_server_ids) == 1:
        # Save tmp allocates_server_name
        allocated_server_id = allocated_server_ids[0]
        # Clear list
        allocated_server_ids = []
        for i in range(len(composite_component_allocation.keys())):
            server_name = get_by_id(element_id=allocated_server_id, element=cache.get_xml_tree(
                "resourceenvironment")).get("entityName")
            # allocated_server_ids.append(allocated_server + "-" + str(i+1))
            allocated_server_ids.append(
                '{server_name}-{counter}'.format(server_name=server_name, counter=i + 1))
    # Else get server names and add to list
    else:
        tmp_server_list = []
        for allocated_server_id in allocated_server_ids:
            server_name = get_by_id(element_id=allocated_server_id, element=cache.get_xml_tree(
                "resourceenvironment")).get("entityName")
            tmp_server_list.append(server_name)
        # Overwrite allcated server ids with list that contains names
        allocated_server_ids = tmp_server_list
    return allocated_server_ids


def create_synch_call_name(called_service_id, xml_cache, input_data, activity, uid_string, action, mapping_cache):
    # Get Interface operation by "calledService_ExternalService"
    interface_operation = get_by_id(element_id=called_service_id,
                                    element=xml_cache.get_xml_tree("repository"))
    operation_name = interface_operation.get("entityName")
    # Get the interface_name from interface's operation parent with tag "interfaces__Repository"
    # and get "entityName"
    interface = get_parent_by_tag(element=interface_operation, tag="interfaces__Repository")
    interface_name = interface.get("entityName")

    # Get component_name from parent element with tag "components__Repository" from
    # element that's "describedService__SEFF" == component_repository_id
    described_seff = None
    for component in get_used_components(xml_cache.get_xml_tree(name="repository"), input_data=input_data):
        described_seff = get_element_by_identifier(attribute="describedService__SEFF",
                                                   search_string=called_service_id,
                                                   element_tree=component)
        if described_seff is not None:
            break
    component = get_parent_by_tag(element=described_seff, tag="components__Repository")
    component_name = component.get("entityName")

    # Create synch_call_name and add synch-call to activity
    # check if action contains attribute referenceName=type in all children and
    # retrieve child of type namedReference__VariableUsage (see *.repository file)
    type_named_reference = get_element_by_identifier(element_tree=action, attribute="referenceName",
                                                     search_string="type")
    if type_named_reference is not None:
        # Get child of sibling with tag = specification_VariableCharacterisation
        specification_variable = type_named_reference.getparent().find(".//specification_VariableCharacterisation")
        uid_specification = get_unique_specification_string(specification_variable.get("specification"))
        synch_call_name = '{component}_{interface}_{operation}_{uid_specification}_Entry'.format(
            component=component_name,
            interface=interface_name,
            operation=operation_name,
            uid_specification=uid_specification)
        return synch_call_name
    else:
        # Check is actions belongs to composite component, if true build processor name with self.uid_string to
        # link to corresponding processor
        composite_component = is_part_of_composite_component(element=component,
                                                             components=xml_cache.get_xml_tree("repository").findall(
                                                                 "./components__Repository"))
        if composite_component and uid_string:
            synch_call_name = '{component}_{interface}_{operation}_{uid}_Entry'.format(
                component=component_name,
                interface=interface_name,
                operation=operation_name,
                uid=uid_string)
            return synch_call_name
        else:
            parent_component_name = get_parent_by_tag(element=activity, tag="processor").get("name")
            try:
                if input_data["graphical_mapping"][0] in parent_component_name:
                    synch_call_name = '{component}_{interface}_{operation}_{uid}_Entry'.format(
                        component=component_name,
                        interface=interface_name,
                        operation=operation_name,
                        uid=input_data["graphical_mapping"][1])
                    return synch_call_name
            except KeyError:
                # except for other examples than BRS
                pass
            # Create synch-calls for remaining processors
            processor_name_beginning = '{component}_{interface}_{operation}'.format(
                component=component_name,
                interface=interface_name,
                operation=operation_name)
            # Our heuristic: Choose first processor that matches processor_name_beginning as synch-call's destination
            for processor_name in mapping_cache["connector_mapping"].keys():
                if processor_name_beginning in processor_name:
                    synch_call_name = '{processor_name}_Entry'.format(processor_name=processor_name)
                    return synch_call_name
