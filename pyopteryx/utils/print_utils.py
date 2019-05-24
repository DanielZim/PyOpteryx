def print_results(examples_amount, counter, error_counter, amount_calculated, amount_rounding_error):
    """
    Prints information about amount of valid and tested examples and details
    :param examples_amount: amount of all examples
    :param counter: amount of valid examples
    :param error_counter: amount of wrong calculated response times
    :param amount_calculated: amount of calculated response times
    :param amount_rounding_error: amount of possible rounding errors that are 0 < difference <= 0.001
    :return:
    """
    print("\n--------------------------- RESULTS ---------------------------")
    print("#Examples: {} | #TestedExamples: {}".format(examples_amount, counter))
    print_detailed_results(amount_calculated=amount_calculated, amount_rounding_error=amount_rounding_error,
                           counter=counter, error_counter=error_counter)


def print_detailed_results(amount_calculated, amount_rounding_error, counter, error_counter):
    """
    Prints amount of errors, correct response times, calculated reponse times and possible rounding errors
    :param amount_calculated: amount of calculated response times
    :param amount_rounding_error: amount of possible rounding errors that are 0 < difference <= 0.001
    :param counter: amount of valid examples
    :param error_counter: amount of wrong response times
    """
    print("#WrongRTs: {error} | #CorrectRTs: {correct} | #Calculated: {calculated} | #Rounding: {rounding}".format(
        error=error_counter,
        correct=(counter - error_counter),
        calculated=amount_calculated,
        rounding=amount_rounding_error))


def print_correct_and_calculated_response_times(correct, calculated, difference):
    """
    Prints correct and calculated response times and difference between them
    :param correct: response time from csv file
    :param calculated: calculated response time for given example
    :param difference: abs(calculated-correct)
    """
    print('correct: {correct} -> calculated: {calculated} | diff: {difference}'.format(
        correct=correct, calculated=calculated, difference=difference))


def print_index_diff(index, correct, calculated, difference):
    """
    Prints index and abs difference if difference is >= 0.001
    """
    if difference >= 0.001:
        print('index: {index}, diff: {difference}'.format(index=index, correct=correct, calculated=calculated,
                                                          difference=difference))
