from collections import defaultdict

from pyopteryx.utils.xml_utils import get_element_by_identifier, get_by_id, get_linkage_id, get_xml_schema_type


def get_graphical_mapping(current_example_row, cache, model_config, composite_component_allocation):
    """
    Get graphical mapping for BRS.
    :param current_example_row:
    :param cache:
    :param model_config:
    :param composite_component_allocation:
    :return: tuple of form ("GraphicalReporting", "server_uid")
    """
    try:
        # Get first key of composite_component_allocation
        first_composite_key = list(composite_component_allocation.keys())[0]
        length_composite = len(composite_component_allocation[first_composite_key])
        for column_name in model_config["components"]:
            allocation_name = column_name.replace("AllocationDegreeImpl:", "")
            context = get_element_by_identifier(element_tree=cache.get_xml_tree("allocation"),
                                                search_string=allocation_name,
                                                attribute="entityName")
            if "_MNz1gHqQEd6uqIqMUZizUw" == context.get("id"):
                # check if column (with name of component) of current test data is allocated to existing server
                if current_example_row[column_name] in model_config["server"].keys():
                    # if component is allocated to existing server append allocation to list
                    for server_string in model_config["server"]:
                        # if component is part of composite
                        if current_example_row[column_name] == server_string:
                            server_id_clean = model_config["server"][current_example_row[column_name]]
                            server_name = get_by_id(element=cache.get_xml_tree("resourceenvironment"),
                                                    element_id=server_id_clean).get("entityName")
                            if length_composite == 1:
                                server_uid = '#{server_name}-2#'.format(server_name=server_name)
                            else:
                                server_uid = '#{server_name}#'.format(server_name=server_name)
        if server_uid:
            graphical_mapping = ("GraphicalReporting", server_uid)
            return graphical_mapping
    except IndexError:
        # Simple Heuristics has no composite_component_mapping
        pass
    return {}


def get_composite_component(current_example_row, cache, model_config):
    """
    maps component_id to dict of {cpu_id: False, ...}
    :param current_example_row:
    :param cache:
    :param model_config:
    :return: nested mapping_dict = { #there can be multiple components
        component_id = {        #components can be deployed on multiple servers
            cpu_id: False,
            ...
        },
        ...
    }
    """
    mapping_dict = defaultdict(lambda: {})
    # for context in
    for column_name in model_config["components"]:
        allocation_name = column_name.replace("AllocationDegreeImpl:", "")
        context = get_element_by_identifier(element_tree=cache.get_xml_tree("allocation"),
                                            search_string=allocation_name,
                                            attribute="entityName")
        system_id = get_linkage_id(identifier="assemblyContext_AllocationContext", element_tree=context)
        assembly_context = get_by_id(element=cache.get_xml_tree("system"), element_id=system_id)
        component = assembly_context.find("./encapsulatedComponent__AssemblyContext")
        if component.get(get_xml_schema_type()) == "repository:CompositeComponent":
            repo_id = get_linkage_id(element_tree=assembly_context, identifier="encapsulatedComponent__AssemblyContext")
            composite_component = get_by_id(element=cache.get_xml_tree("repository"), element_id=repo_id)
            for composed_structure in composite_component.findall("./assemblyContexts__ComposedStructure"):
                component_id = composed_structure.get("encapsulatedComponent__AssemblyContext")
                # check if column (with name of component) of current test data is allocated to existing server
                if current_example_row[column_name] in model_config["server"].keys():
                    # if component is allocated to existing server append allocation to list
                    for server_id in model_config["server"]:
                        # if component is part of composite
                        if current_example_row[column_name] == server_id:
                            temp_server_id = model_config["server"][current_example_row[column_name]]
                            mapping_dict[component_id].update({temp_server_id: False})
    return mapping_dict


def get_component_allocations(current_example_row, model_config):
    """
    Get allocation of components from CSV test data
    :param current_example_row: CSV test data as pandas data frame
    :param model_config: configurations for pcm model that contain server names, component names, ...
    :return: allocations dict = {
        allocation_id: cpu_id,
        ...
    }
    """
    allocations = {}
    # get allocation for every component that is declared in the config file
    for component in model_config["components"]:
        # check if column (with name of component) of current test data is allocated to existing server
        if current_example_row[component] in model_config["server"].keys():
            # if component is allocated to existing server append allocation to list
            for server_id in model_config["server"]:
                # if component is part of composite
                if current_example_row[component] == server_id:
                    # map component id : server id
                    allocations[model_config['components'][component]] = model_config["server"][server_id]
    return allocations


def get_cpu_to_seff_id_mapping(current_example_row, model_config, allocations, cache):
    """
    get Mapping from cpu id to list of deployed seffs on this server
    :param current_example_row:
    :param model_config:
    :param allocations:
    :param cache:
    :return: nested component_connectors_dict = {
        cpu_id : [seff_id, seff_id2, seff_id3, ...],
        cpu_id2: [seff_id3, seff_id4, seff_id5, ...],
        ...
    }
    """
    alloc_root = cache.get_xml_tree("allocation")
    component_connectors = {"component_connectors": {}}
    for cpu_key in model_config["cpu_rate"]:
        cpu_id = model_config["cpu_rate"][cpu_key]
        for allocation_id in allocations.keys():
            allocation_context = get_by_id(element=alloc_root, element_id=allocation_id)
            for key in current_example_row.keys():
                if allocation_context.get('entityName') in key and cpu_id in current_example_row[key]:
                    assembly_context_id = get_linkage_id(identifier="assemblyContext_AllocationContext",
                                                         element_tree=allocation_context)
                    seff_ids = _get_seff_ids_from_assembly_context(assembly_context_id, cache=cache)
                    nested_dict = component_connectors["component_connectors"]
                    if cpu_id in nested_dict.keys():  # if key already exists, append
                        for seff_id in seff_ids:
                            component_connectors["component_connectors"][cpu_id].append(seff_id)
                    else:  # create key
                        component_connectors["component_connectors"].update({cpu_id: seff_ids})
    return component_connectors


def _get_seff_ids_from_assembly_context(assembly_context_id, cache):
    """
    Search for seffs from assembly_context
    :param assembly_context_id:
    :param cache:
    :return: list of seff_ids that belong to assembly_context
    """
    file_root = cache.get_xml_tree('system')
    composed_structure = get_by_id(element=file_root, element_id=assembly_context_id)
    component_id = get_linkage_id(identifier="encapsulatedComponent__AssemblyContext", element_tree=composed_structure)
    list_of_seff_ids = []
    file_root = cache.get_xml_tree('repository')
    component = get_by_id(element=file_root, element_id=component_id)
    component_type = component.get(get_xml_schema_type())
    if component_type == 'repository:CompositeComponent':
        for composed_structure in component.findall('./assemblyContexts__ComposedStructure'):
            assembly_context_id = composed_structure.get('encapsulatedComponent__AssemblyContext')
            assembly_context = get_by_id(element=file_root, element_id=assembly_context_id)
            for seff in assembly_context.findall("./serviceEffectSpecifications__BasicComponent"):
                seff_id = seff.get("describedService__SEFF")
                list_of_seff_ids.append(seff_id)
    else:
        for seff in component.findall("./serviceEffectSpecifications__BasicComponent"):
            seff_id = seff.get("describedService__SEFF")
            list_of_seff_ids.append(seff_id)
    return list_of_seff_ids


def get_cpu_rates(current_example_row, model_config):
    """
    Get cpu rates of server from CSV test data
    :param current_example_row: CSV test data as pandas data frame
    :param model_config: configurations for pcm model that contain server names, component names, ...
    :return: nested cpu rates dict = {
        "cpu_rates": {
            cpu_id : cpu_rate,
            cpu_id2: cpu_rate2,
            ...
    }
    """
    cpu_rates = {"cpu_rates": {}}
    for cpu_key in model_config["cpu_rate"]:
        cpu_column_name = cpu_key
        config = float(current_example_row[cpu_column_name])
        cpu_rates["cpu_rates"].update({model_config["cpu_rate"][cpu_key]: config})
    return cpu_rates


def get_assembled_components(current_example_row, model_config):
    """
    Get assembled components
    :param current_example_row: CSV test data as pandas data frame
    :param model_config: configurations for pcm model that contain server names, component names, ...
    :return: assembled components dict = { # maps from system to repository
        assembled_component_id : component_id,
        ...
    }
    excluded_components = [unused_component_id1, unused_component_id2, ... ]
    excluded_design_options = { # maps from repository
        component_id : [design_option_id1, design_option_id2, ...],
        ...
    }
    """
    assembled_components = {}
    excluded_components = []
    excluded_design_options = {}
    # find translation for every assembled component id and append to list
    assembled_components_config = model_config["assembled_components"]
    for component in assembled_components_config:
        new_option = None
        tmp_excluded = []
        options = assembled_components_config[component]["options"]
        for option in options:
            # if current id is example id of csv file append translation to assembled_components
            if option == current_example_row[component]:
                assembled_components[assembled_components_config[component]["id"]] = options[option]
                new_option = options[option]
            else:
                tmp_excluded.append(options[option])
                excluded_components.append(options[option])
        excluded_design_options[new_option] = tmp_excluded
    return assembled_components, excluded_components, excluded_design_options
