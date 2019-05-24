import re

from lxml.etree import SubElement

from pyopteryx.factories.action_factories import action_factory as branch_factory
from pyopteryx.factories.action_factories.abstract_action_factory import AbstractActionFactory
from pyopteryx.utils.utils import string_int_to_string_float
from pyopteryx.utils.builder_utils import add_activity_to_task
from pyopteryx.utils.xml_utils import get_element_by_identifier, get_by_id, get_action_type, get_element_from_list, \
    get_xml_schema_type, get_branch_type, create_activity_name_from_action


class BranchActionFactory(AbstractActionFactory):
    def __init__(self, action, task_activities, xml_cache, input_data, latency, mapping_cache, processor):
        super().__init__(action=action, task_activities=task_activities, xml_cache=xml_cache, processor=processor,
                         mapping_cache=mapping_cache)
        self.latency = latency
        self.input_data = input_data

    def add_action(self):
        self.__branch_factory(action=self.action, task_activities=self.task_activities)

    # ---- TODO:  BranchFactory Start ----
    def __branch_factory(self, action, task_activities):
        """
        creates branches depending on branch_type
        :param action:
        :param task_activities:
        :return:
        """
        branches = action.findall("./branches_Branch")
        for branch in branches:
            branch_type = get_branch_type(branch=branch)
            if "probabilistic" == branch_type:
                return self.__add_probabilistic_branch(action=action, task_activities=self.task_activities)
            elif "type" == branch_type:
                return self.__add_type_branch(action=action, task_activities=task_activities)
            elif "detailed" == branch_type:
                return self.__add_detailed_branch(action=action, task_activities=task_activities)
            elif "simple" == branch_type:
                return self.__add_simple_branch(action=self.action, task_activities=self.task_activities)
            else:
                raise ValueError("Unknown branch_type. Abort Mission.")

    def __add_simple_branch(self, action, task_activities):
        """
        Creates simple branches (only relevant in SimpleHeuristicsExample)
        :param action:
        :param task_activities:
        :return:
        """
        action_activity_name = create_activity_name_from_action(action=action)
        add_activity_to_task(task_activities=task_activities, activity_name=action_activity_name, hide_activity=True)

        post_or_element, stop_pre_or_tag = self.__add_pre_or_and_post_or(action=action,
                                                                         action_activity_name=action_activity_name,
                                                                         task_activities=task_activities)

        for branch in action.findall("./branches_Branch"):
            branches_steps = branch.find("./branchBehaviour_BranchTransition").findall(".//steps_Behaviour")
            branch_start_actions, final_successor_action = self.__get_final_successor_and_start(actions=branches_steps)
            # Create ActionFactory and add action
            self.__create_actions_for_all_branches(branches_steps, task_activities)

            branch_conditions = branch.findall(".//branchCondition_GuardedBranchTransition")
            for condition in branch_conditions:
                condition_types = self.__get_condition_types(condition)
                reference_name = self.__get_reference_name(condition_types=condition_types)
                variable_usage = get_element_by_identifier(attribute="referenceName", search_string=reference_name,
                                                           element_tree=self.xml_cache.get_xml_tree("usagemodel"))

                for branch_start_action in branch_start_actions:
                    parent = variable_usage.getparent()
                    bool_exp = parent.find(".//specification_VariableCharacterisation").get("specification")
                    match_object = re.findall(r'true;+\d\.\d*|false;+\d\.\d*', bool_exp)
                    # Get branch probability for post element
                    branch_probability = "0"
                    # First start action has false probability
                    if "NOT" in condition_types:
                        for matching_object in match_object:
                            if "false" in matching_object:
                                branch_probability = matching_object.split(";")[1]
                    else:
                        for matching_object in match_object:
                            if "true" in matching_object:
                                branch_probability = matching_object.split(";")[1]

                    post_predecessor_activity_name = create_activity_name_from_action(action=branch_start_action)
                    post_predecessor_activity = SubElement(post_or_element, 'activity')
                    post_predecessor_activity.set("name", post_predecessor_activity_name)
                    post_predecessor_activity.set("prob", branch_probability)

            self.__add_stop_action_precedences(final_successor_action, stop_pre_or_tag)

    def __add_detailed_branch(self, action, task_activities):
        """
        Copy whole processor and make names unique by adding unique string.
        :param action:
        :param task_activities:
        :return:
        """
        add_activity_to_task(task_activities=task_activities,
                             activity_name=self.activity_name,
                             hide_activity=True)
        post_or_element, stop_pre_or_tag = self.__add_pre_or_and_post_or(action=self.action,
                                                                         action_activity_name=self.activity_name,
                                                                         task_activities=task_activities)
        branch_counter = 0
        branches = action.findall("./branches_Branch")
        for branch in branches:
            branches_steps = branch.find("./branchBehaviour_BranchTransition").findall("./steps_Behaviour")
            branch_start_actions, final_successor_action = self.__get_final_successor_and_start(actions=branches_steps)
            self.__create_actions_for_all_branches(branches_steps, task_activities)
            # if branch is of type "ProbabilisticBranchTransition" it has entity "branchProbability":
            # use this to create or post tag
            branch_conditions = branch.findall(".//branchCondition_GuardedBranchTransition")
            for condition in branch_conditions:
                condition_types = self.__get_condition_types(condition)
                reference_name = self.__get_reference_name(condition_types=condition_types)
                variable_usage = get_element_by_identifier(attribute="referenceName", search_string=reference_name,
                                                           element_tree=self.xml_cache.get_xml_tree("usagemodel"))
                for branch_start_action in branch_start_actions:
                    parent = variable_usage.getparent()
                    bool_exp = parent.find(".//specification_VariableCharacterisation").get("specification")
                    match_object = re.findall(r'"t";+\d\.\d*|"f";+\d\.\d*', bool_exp)
                    # Get branch probability for post element
                    branch_uuid, branch_probability = match_object[branch_counter].replace('\"', "#").split(";")
                    post_predecessor_activity_name = create_activity_name_from_action(action=branch_start_action,
                                                                                      uid_string=self.uid_string)
                    post_predecessor_activity = SubElement(post_or_element, 'activity')
                    post_predecessor_activity.set("name", post_predecessor_activity_name)
                    post_predecessor_activity.set("prob", branch_probability)
            branch_counter += 1

            # Add precedence for stop actions
            self.__add_stop_action_precedences(final_successor_action, stop_pre_or_tag, uid=self.uid_string)

    def __add_probabilistic_branch(self, action, task_activities):
        """
        Creates Probabilistic branches with probabilities
        :param action:
        :param task_activities:
        :return:
        """
        activity_name = create_activity_name_from_action(action=action)
        add_activity_to_task(task_activities=task_activities, activity_name=activity_name, hide_activity=True)

        post_or_element, stop_pre_or_tag = self.__add_pre_or_and_post_or(action=action,
                                                                         action_activity_name=activity_name,
                                                                         task_activities=task_activities)
        branches = action.findall("./branches_Branch")
        for branch in branches:
            branches_actions = branch.find("./branchBehaviour_BranchTransition").findall(".//steps_Behaviour")
            self.__create_actions_for_all_branches(branches_steps=branches_actions, task_activities=task_activities)

            branch_start_actions, final_successor_action = self.__get_final_successor_and_start(
                actions=branches_actions)
            # if branch is of type "ProbabilisticBranchTransition" it has entity "branchProbability":
            # use this to create or post tag
            branch_probability = branch.get("branchProbability")
            for start_action in branch_start_actions:
                post_predecessor_activity = SubElement(post_or_element, 'activity')
                post_predecessor_activity_id = create_activity_name_from_action(action=start_action)
                post_predecessor_activity.set("name", post_predecessor_activity_id)
                post_predecessor_activity.set("prob", string_int_to_string_float(branch_probability))

            self.__add_stop_action_precedences(final_successor_action=final_successor_action,
                                               stop_pre_or_tag=stop_pre_or_tag)

    def __add_type_branch(self, action, task_activities):
        """
        Creates type branches with type values as part of unique strings
        :param action:
        :param task_activities:
        :return:
        """
        # 1) Add branch action
        add_activity_to_task(task_activities=task_activities, activity_name=self.activity_name, hide_activity=True)

        post_or_element, stop_pre_or_tag = self.__add_pre_or_and_post_or(action=action,
                                                                         action_activity_name=self.activity_name,
                                                                         task_activities=task_activities)
        for branch in action.findall("./branches_Branch"):
            for name, uid in self.mapping_cache["branch_mapping"][branch.get("id")].items():
                processor_name = '{processor_name}_Processor'.format(processor_name=name)
                branch_uid = uid
                if processor_name == self.processor.get("name"):
                    branches_steps = branch.find("./branchBehaviour_BranchTransition").findall(".//steps_Behaviour")
                    branch_start_actions, final_successor_action = self.__get_final_successor_and_start(
                        actions=branches_steps)
                    # Add actions recursively for first actions of branches_Steps, which is StartAction
                    self.__add_actions(action=branches_steps[0], processor=self.processor)
                    self.__add_precedence_for_start_action(branches_steps=branches_steps,
                                                           post_or_element=post_or_element,
                                                           uid=branch_uid)
                    self.__add_stop_action_precedences(final_successor_action=final_successor_action,
                                                       stop_pre_or_tag=stop_pre_or_tag,
                                                       uid=branch_uid)

    @staticmethod
    def __get_condition_types(condition):
        """
        Get branch condition types as list. For SimpleHeuristicsExample ["NOT", "inBook"],
        which will be used for defining if a branch uses probability for true or false.
        :param condition: string
        :return: list of condition types
        """
        branch_condition = condition.get("specification")
        condition_type, condition_value = branch_condition.split(".")
        condition_types = condition_type.split(" ")
        return condition_types

    def __create_actions_for_all_branches(self, branches_steps, task_activities):
        """
        Create ActionFactory and add action
        :param branches_steps:
        :param task_activities:
        :return:
        """
        for branch_action in branches_steps:
            action_factory = branch_factory.ActionFactory(xml_cache=self.xml_cache,
                                                          mapping_cache=self.mapping_cache,
                                                          input_data=self.input_data,
                                                          action=branch_action,
                                                          latency=self.latency,
                                                          processor=self.processor
                                                          ).create_action_factory(task_activities=task_activities)
            action_factory.add_action()

    def __add_actions(self, action, processor):
        """
        Create ActionFactory and add action as <activity> to processors' <task-activities>
        and all corresponding <precedences> for action
        :param processor: processor to add actions to
        :param action: first action of a component is always StartAction
        :return:
        """
        # Create ActionFactory for action
        task_activities = processor.find(".//task-activities")
        action_factory = branch_factory.ActionFactory(xml_cache=self.xml_cache,
                                                      mapping_cache=self.mapping_cache,
                                                      action=action,
                                                      input_data=self.input_data,
                                                      latency=self.latency,
                                                      processor=processor
                                                      ).create_action_factory(task_activities=task_activities)
        # If action is of type 'SetVariableAction' no factory will be created,
        # since 'SetVariableAction' is not supported
        if action_factory:
            action_factory.add_action()

        # Add actions recursively if current action has successor action
        successor_id = action.get("successor_AbstractAction")
        if successor_id is not None:
            successor = get_by_id(element=action.getparent(), element_id=successor_id)
            self.__add_actions(action=successor, processor=processor)

    def __add_pre_or_and_post_or(self, action, action_activity_name, task_activities):
        """
        Create pre-or and post-or precedences along with their respective activities
        :param action:
        :param action_activity_name:
        :param task_activities:
        :return:
        """
        # Add: StopAction_1, StopAction_2 -> final successor of BranchAction
        final_successor_id = action.get("successor_AbstractAction")
        final_successor_action = get_by_id(element=self.xml_cache.get_xml_tree("repository"),
                                           element_id=final_successor_id)
        final_successor_action_name = create_activity_name_from_action(action=final_successor_action,
                                                                       uid_string=self.uid_string)
        # create precedence that contains pre-or and post tag
        final_successor_precedence = SubElement(task_activities, 'precedence')
        stop_pre_or_tag = SubElement(final_successor_precedence, 'pre-OR')
        stop_post_tag = SubElement(final_successor_precedence, 'post')

        # add activity_name to post element
        stop_post_activity = SubElement(stop_post_tag, 'activity')
        stop_post_activity.set("name", final_successor_action_name)
        # branch action as pre tag and each branches' start_action as post-OR tag
        pre_precedence = SubElement(task_activities, 'precedence')
        # create pre-element
        pre_tag = SubElement(pre_precedence, 'pre')
        stop_pre_or_activity = SubElement(pre_tag, 'activity')
        stop_pre_or_activity.set("name", action_activity_name)
        post_or_element = SubElement(pre_precedence, 'post-OR')
        return post_or_element, stop_pre_or_tag

    @staticmethod
    def __get_final_successor_and_start(actions):
        """
        Get StartActions and StopActions from all branches in lists
        :param actions:
        :return:
        """
        branch_start_actions = []
        final_successor_action = []
        for steps in actions:
            steps_action = get_action_type(action=steps)
            if "StartAction" in steps_action:
                branch_start_actions.append(steps)
            elif "StopAction" in steps_action:
                final_successor_action.append(steps)
        return branch_start_actions, final_successor_action

    def __get_reference_name(self, condition_types):
        """
        Get reference name to look for probabilities in usagemodel. "<branchCondition_GuardedBranchTransition />"
        (repository) is used to look for reference name in usagemodel. Find matching reference name in condition types
        and return corresponding reference name.
        :param condition_types: 'specification="NOT isBook.VALUE"' -> ["NOT", "isBook", "VALUE"]
        :return: reference name
        """
        named_references = self.__get_references()
        reference_name = ""
        for reference in named_references:
            try:
                name_index = condition_types.index(reference)
                reference_name = condition_types[name_index]
                break
            except ValueError:
                pass
        return reference_name

    def __get_references(self):
        """
        Get references from usagemodel where references of branch action probabilities are stored
        :return:
        """
        named_references = []
        for usage in self.xml_cache.get_xml_tree("usagemodel"):
            variable_usages = usage.findall(".//namedReference__VariableUsage")
            for name in variable_usages:
                named_references.append(name.get("referenceName"))
        return named_references

    @staticmethod
    def __add_stop_action_precedences(final_successor_action, stop_pre_or_tag, uid=None):
        """
        Add precedences for StopAction
        :param final_successor_action:
        :param stop_pre_or_tag:
        :param uid:
        :return:
        """
        # Add precedence for stop actions
        for stop_action in final_successor_action:
            activity_name = create_activity_name_from_action(action=stop_action, uid_string=uid)
            stop_pre_or_activity = SubElement(stop_pre_or_tag, 'activity')
            stop_pre_or_activity.set("name", activity_name)

    @staticmethod
    def __add_precedence_for_start_action(branches_steps, post_or_element, uid=None):
        """
        Add precedences for StartAction.
        :param branches_steps:
        :param post_or_element:
        :param uid:
        :return:
        """
        action = get_element_from_list(search_string="seff:StartAction",
                                       attribute=get_xml_schema_type(),
                                       element_list=branches_steps)
        activity_name = create_activity_name_from_action(action=action, uid_string=uid)
        activity = SubElement(post_or_element, 'activity')
        activity.set("name", activity_name)
        activity.set("prob", "1.0")
