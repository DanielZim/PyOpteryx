import os
from decimal import Decimal, ROUND_HALF_DOWN

from pandas import read_csv

from pyopteryx.lqn_init import get_project_config
from pyopteryx.lqn_input import get_cpu_rates, get_assembled_components, get_component_allocations, \
    get_composite_component, get_cpu_to_seff_id_mapping, get_graphical_mapping
from pyopteryx.lqn_solver import LqnSolver
from pyopteryx.utils.print_utils import print_correct_and_calculated_response_times, print_detailed_results, \
    print_results
from pyopteryx.utils.utils import get_all_file_names_with_given_extension
from pyopteryx.utils.xml_cache import XMLCache

CURRENT_PROJECT = "SimpleHeuristicsExample"
path_to_allocation = "default.allocation"
path_to_cost = "default.cost"
path_to_designdecision = "simpleexample.designdecision"
path_to_repository = "default.repository"
path_to_system = "default.system"
path_to_usagemodel = "default.usagemodel"
path_to_resourceenvironment = "default.resourceenvironment"
setting_type = "default"
conv_val = "0.0001"

CURRENT_PROJECT = "BusinessReportingSystem"
path_to_allocation = "brs.allocation"
path_to_cost = "brs.cost"
path_to_designdecision = "brs.designdecision"
path_to_repository = "brs.repository"
path_to_system = "brs.system"
path_to_usagemodel = "brs.usagemodel"
path_to_resourceenvironment = "brs.resourceenvironment"
setting_type = "brs"
conv_val = "0.001"

if __name__ == '__main__':
    path_to_project = "pcms/{}".format(CURRENT_PROJECT)
    file_dict = {
        'allocation': os.path.join(path_to_project, path_to_allocation),
        'cost': os.path.join(path_to_project, path_to_cost),
        'designdecision': os.path.join(path_to_project, path_to_designdecision),
        'repository': os.path.join(path_to_project, path_to_repository),
        'system': os.path.join(path_to_project, path_to_system),
        'usagemodel': os.path.join(path_to_project, path_to_usagemodel),
        'resourceenvironment': os.path.join(path_to_project, path_to_resourceenvironment)
    }

    cache = XMLCache(file_dict)
    model_config = get_project_config(cache)

    lqn_solver = LqnSolver(cache)
    # Counter for test prints
    error_counter = 0
    counter = 0
    examples_amount = 0
    examples_counter = 0
    amount_calculated = 0
    amount_rounding_error = 0
    # Get all CSV test files in folder "peropteryx_import/*.csv"
    file_names = get_all_file_names_with_given_extension("peropteryx_import/{}/*.csv".format(CURRENT_PROJECT))


    def create_input(test_file_content, index, model_config):
        # get CPU rates from CSV test files
        cpu_rates = get_cpu_rates(current_example_row=test_file_content.iloc[index], model_config=model_config)
        # get Assembled Component info from CSV test files
        assembled_components, excluded_components, alternative_design_options = get_assembled_components(
            current_example_row=test_file_content.iloc[index],
            model_config=model_config)
        # get Allocations info from CSV test files
        allocations = get_component_allocations(current_example_row=test_file_content.iloc[index],
                                                model_config=model_config)
        composite_component_allocation = get_composite_component(current_example_row=test_file_content.iloc[index],
                                                                 cache=cache, model_config=model_config)
        component_connectors = get_cpu_to_seff_id_mapping(current_example_row=test_file_content.iloc[index],
                                                          model_config=model_config, allocations=allocations,
                                                          cache=cache)
        graphical_mapping = get_graphical_mapping(current_example_row=test_file_content.iloc[index], cache=cache,
                                                  model_config=model_config,
                                                  composite_component_allocation=composite_component_allocation)
        input_data = {
            "component_allocations": allocations,
            "assembled_components": assembled_components,
            'excluded_components': excluded_components,
            'alternative_design_options': alternative_design_options,
            'composite_component_allocation': composite_component_allocation,
            'graphical_mapping': graphical_mapping,
            'solver_params': {
                'conv_val': conv_val
            }
        }
        input_data.update(cpu_rates)
        input_data.update(component_connectors)

        return input_data


    # load all CSV test files
    for file_name in file_names:
        # read content of CSV file with pandas
        test_file_content = read_csv(file_name, sep=";")
        # set initial response time
        dec_response_time_old = Decimal(-1)
        examples_amount = examples_amount + len(test_file_content)
        # validate calculated response times to exact response times from examples in CSV test file
        index = 50
        for index in range(index, index + 1):  # TODO: change if needed for testing
            examples_counter += 1
            response_time = test_file_content[model_config["keys"]["response_time"]][index]
            if response_time != 'Infinity':
                input_data = create_input(test_file_content=test_file_content, index=index, model_config=model_config)
                # count validated examples
                counter += 1
                # calculate response times and costs
                costs, rt = lqn_solver.evaluate_fitness(input_data=input_data)
                if rt != -1:
                    amount_calculated += 1

                calculated_rt = Decimal(rt)
                calculated_precision = calculated_rt.as_tuple().exponent

                given_rt = Decimal(response_time)
                given_precision = given_rt.as_tuple().exponent

                places = -3
                rounding = q = Decimal(10) ** places
                dec_response_time = given_rt.quantize(rounding, ROUND_HALF_DOWN)
                rt = calculated_rt.quantize(rounding, ROUND_HALF_DOWN)

                # Calculate Difference and increase rounding error if 0.0 < abs <= 0.001
                difference = abs(rt - dec_response_time)
                if difference <= 0.001 and difference != 0.0:
                    amount_rounding_error += 1
                print_correct_and_calculated_response_times(correct=dec_response_time, calculated=rt, difference=difference)

                # check if calculated response time is equal to exact response time
                if rt != dec_response_time:
                    error_counter += 1
                # set response time to last correct response time to skip same response times
                # of directly following examples
                response_time_old = response_time
                print_detailed_results(amount_calculated=amount_calculated, amount_rounding_error=amount_rounding_error,
                                       counter=counter, error_counter=error_counter)

    print_results(examples_amount=examples_amount, counter=counter, error_counter=error_counter,
                  amount_calculated=amount_calculated, amount_rounding_error=amount_rounding_error)
