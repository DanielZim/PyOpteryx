from pyopteryx.utils.xml_utils import get_by_tag_name, get_by_id, get_xml_schema_type, get_linkage_id


def get_project_config(cache):
    """
    Collects info from cached files and returns config dict
    :param cache:
    :return:
    """
    config = {}
    config = add_server_config(config, cache)
    config = add_allocation_config(config, cache)
    config = add_assembled_component_config(config, cache)
    config = add_keys_config(config, cache)
    return config


def add_keys_config(config, cache):
    """
    config["keys"] saves responsetime_column_name
    :param config:
    :param cache:
    :return:
    """
    usagemodel_root = cache.get_xml_tree('usagemodel')
    keys_config = {}
    for child in usagemodel_root.findall("./usageScenario_UsageModel"):
        keys_config["response_time"] = "response time:{}".format(child.get('entityName'))
    config["keys"] = keys_config
    return config


def add_assembled_component_config(config, cache):
    """
        loop through all degreesOfFreedom xsi:type="specific:AssembledComponentDegree" in designdecision,
        build dict of assembled components and map to their id
        {
            AssembledComponentDegreeImpl:assembly_context_entityName :
            {
                id= primary_changed_id
                options = {
                    {component_name} (ID: {component_id}) : component_id,
                    {component_name} (ID: {component_id}) : component_id
                }
            },
            ...
            ...
        }
    :param config:
    :param cache:
    :return:
    """
    assembled_component_config = {}
    designdecision_root = cache.get_xml_tree("designdecision")
    for degree_of_freedom in get_by_tag_name(designdecision_root, 'degreesOfFreedom'):
        if degree_of_freedom.get(get_xml_schema_type()) == "specific:AssembledComponentDegree":
            assembled_component_degree_impl_config = {}
            for child in get_by_tag_name(degree_of_freedom, 'primaryChanged'):
                pc_file, pc_id = child.get("href").split("#")
                pc_file_root = cache.get_xml_tree(pc_file)
                assembly_context = get_by_id(pc_file_root, pc_id).get("entityName")
                assembled_component_degree_impl_config['id'] = pc_id
                options = {}
                for dof in list(degree_of_freedom):
                    if "primaryChanged" not in dof.tag:
                        file, id = dof.get("href").split("#")
                        file_root = cache.get_xml_tree(file)
                        basic_component = get_by_id(file_root, id).get("entityName")
                        options["{} (ID: {})".format(basic_component, id)] = id
                assembled_component_degree_impl_config['options'] = options
                assembled_component_config[
                    "AssembledComponentDegreeImpl:{}".format(
                        assembly_context)] = assembled_component_degree_impl_config
    config["assembled_components"] = assembled_component_config
    return config


def add_allocation_config(config, cache):
    """
    config["components"] maps Allocation name that can be found in csv to allocation_id
    :param config:
    :param cache:
    :return:
    """
    allocation_root = cache.get_xml_tree("allocation")
    allocation_config = {}
    for allocation in allocation_root.findall("allocationContexts_Allocation"):
        allocation_config["AllocationDegreeImpl:{}".format(allocation.get("entityName"))] = allocation.get("id")
    config["components"] = allocation_config
    return config


def add_server_config(config, cache):
    """
    config["server"] map server name to server id
    config["cpu_rate"] map cpu_rate_string that can be found in the csv to cpu_id
    :param config:
    :param cache:
    :return:
    """
    res_env_root = cache.get_xml_tree('resourceenvironment')
    server_config = {}
    cpu_rate_config = {}
    for server in res_env_root.findall('.//resourceContainer_ResourceEnvironment'):
        server_id = server.get('id')
        server_config["{} (ID: {})".format(server.get("entityName"), server_id)] = server_id
        cpu_rate_config["ContinuousProcessingRateDegreeImpl:{}:CPU".format(server.get("entityName"))] = server_id
    config["server"] = server_config
    config["cpu_rate"] = cpu_rate_config
    return config
