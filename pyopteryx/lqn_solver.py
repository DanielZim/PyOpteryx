import os
import subprocess
from datetime import datetime

from lxml import etree

from pyopteryx.lqn_builder import LqnBuilder
from pyopteryx.utils.xml_utils import get_element_by_identifier, get_by_id, get_linkage_id, get_xml_schema_type
from pyopteryx.utils.utils import save_xml


class LqnSolver:
    """
    Class that execute LQNSolver with created .in file.
    """

    def __init__(self, cache):
        """
        Set __temp_output_path__ to 'C:/Output/' and cache.
        :param cache: cached PCM files
        """
        self.__temp_output_path__ = 'C:/Output/'
        self.__cache = cache

    def __read_response_time_from_result_file(self, filename):
        """
        Read response time from created result file. If .out file couldn't be created return -1 as result time.
        :param filename: result file name
        :return: calculated result time
        """
        response_time = -1
        try:
            # Open lqxo-output-file
            xml_tree = etree.parse(self.__temp_output_path__ + filename)
        except OSError as e:
            print("Fehlerausgabe: " + str(e))
            return -1

        # Parse XML
        xml_root = xml_tree.getroot()

        # Iterate over all "processor"-nodes
        for xml_processor in xml_root.findall('processor'):
            # TODO: Usagescenationame auslesen aus __input_data['keys']['usage']
            if xml_processor.get('name') == 'UsageScenario_BRS_usage_scenario_1_Processor' or xml_processor.get(
                    'name') == 'UsageScenario_defaultUsageScenario_1_Processor':
                xml_task = xml_processor.find('task')
                xml_entry = xml_task.find('entry')
                xml_result_entry = xml_entry.find('result-entry')
                response_time = xml_result_entry.get('phase1-service-time')

        return response_time

    def evaluate_fitness(self, input_data):
        """
        Evaluate fitness by performing PyCM2LQN transformation for current input data and execute LQNSolver with
        that created .in file. Read response time from created .out file
        :param input_data: input containing cpu rates, allocation of components and assembled components
        :return: calculated response time and calculated costs
        """
        lqn_builder = LqnBuilder(input_data=input_data, cache=self.__cache)
        lqn_input_xml = lqn_builder.transform_pycm2lqn()

        date = datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")

        input_file_name = date + '.in.lqxo'
        result_file_name = date + '.out.lqxo'

        save_xml(lqn_input_xml, self.__temp_output_path__ + input_file_name)

        # Command expression for lqn tool (-f = fast flag, -w = suppress warnings)
        command = "lqns -w -x -f -o" + self.__temp_output_path__ + result_file_name + " " + self.__temp_output_path__ + input_file_name

        # Execute LQN-solver
        subprocess.call(command, shell=True)

        # Get response time from result file
        response_time = self.__read_response_time_from_result_file(result_file_name)

        self.__delete_in_and_out_files(input_file_name, result_file_name)

        costs = self.calculate_costs(input_data=input_data)

        return costs, response_time

    def __delete_in_and_out_files(self, input_file_name, result_file_name):
        """
        Delete created .in and .out files.
        :param input_file_name: created .in file
        :param result_file_name: created .out file
        """
        try:
            os.remove(self.__temp_output_path__ + input_file_name)
        except FileNotFoundError:
            pass
        try:
            os.remove(self.__temp_output_path__ + result_file_name)
        except FileNotFoundError:
            pass

    # TODO: Prototype calculated costs are not valid yet!
    def calculate_costs(self, input_data):
        """
        Calculate cost of current allocation, cpu rates of input data.
        :param input_data: input containing cpu rates, allocation of components and assembled components
        :return: calculated cost
        """
        cost = 0.0
        try:
            used_server = []
            # For every used server / cpu processor add "processingRateInitialFunction" to cost
            for component, allocated_server in input_data["component_allocations"].items():
                # iterate trough cost type "VariableProcessingResourceCost"
                for child in self.__cache.get_xml_tree("cost").findall(".//cost"):
                    child_type = child.get(get_xml_schema_type())
                    if child_type == "cost:VariableProcessingResourceCost":
                        # Get cpu server
                        resource_specification = get_linkage_id(identifier="processingresourcespecification",
                                                                element_tree=child)
                        server_element = get_by_id(element=self.__cache.get_xml_tree("resourceenvironment"),
                                                   element_id=resource_specification).getparent()
                        server_id = server_element.get("id")
                        # Add cost if component is allocated to server and server cost was not added before
                        if allocated_server == server_id and server_id not in used_server:
                            used_server.append(server_id)
                            cost_function = child.find("processingRateInitialFunction").get("specification").replace(
                                "procRate.VALUE", str(input_data["cpu_rates"][allocated_server])).replace("^", "**")
                            cost += eval(cost_function)
            # Add cost for assembled component
            for assembly_context, component in input_data["assembled_components"].items():
                cost_el = get_element_by_identifier(attribute="href", search_string='default.repository#' + component,
                                                    element_tree=self.__cache.get_xml_tree("cost"))
                if cost_el is not None:
                    assembly_cost = cost_el.getparent().get("componentInitialCost")
                    cost += float(assembly_cost)
            amount_server = len(used_server)
            cost += (22.0 * amount_server)
        except Exception as e:
            print(e)
        return cost
