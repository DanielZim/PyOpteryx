from pyopteryx.factories.action_factories.branch_action_factory import BranchActionFactory
from pyopteryx.factories.action_factories.external_action_factory import ExternalActionFactory
from pyopteryx.factories.action_factories.internal_action_factory import InternalActionFactory
from pyopteryx.factories.action_factories.loop_action_factory import LoopActionFactory
from pyopteryx.factories.action_factories.start_action_factory import StartActionFactory
from pyopteryx.factories.action_factories.stop_action_factory import StopActionFactory
from pyopteryx.utils.xml_utils import get_action_type


class ActionFactory:
    def __init__(self, xml_cache, mapping_cache, action, input_data, latency, processor):
        self.xml_cache = xml_cache
        self.mapping_cache = mapping_cache
        self.action = action
        self.input_data = input_data
        self.latency = latency
        self.processor = processor

    def create_action_factory(self, task_activities):
        """
        Creates, initializes and returns Actionfactory
        :param task_activities:
        :return:
        """
        action_type = get_action_type(action=self.action)
        if "StartAction" in action_type:
            return StartActionFactory(action=self.action,
                                      task_activities=task_activities,
                                      xml_cache=self.xml_cache,
                                      processor=self.processor,
                                      mapping_cache=self.mapping_cache)
        elif "InternalAction" in action_type:
            return InternalActionFactory(action=self.action,
                                         task_activities=task_activities,
                                         xml_cache=self.xml_cache,
                                         processor=self.processor,
                                         mapping_cache=self.mapping_cache)
        elif "ExternalCallAction" in action_type:
            return ExternalActionFactory(action=self.action,
                                         task_activities=task_activities,
                                         xml_cache=self.xml_cache,
                                         latency=self.latency,
                                         input_data=self.input_data,
                                         mapping_cache=self.mapping_cache,
                                         processor=self.processor)
        elif "BranchAction" in action_type:
            return BranchActionFactory(action=self.action,
                                       task_activities=task_activities,
                                       xml_cache=self.xml_cache,
                                       input_data=self.input_data,
                                       latency=self.latency,
                                       mapping_cache=self.mapping_cache,
                                       processor=self.processor)
        elif "StopAction" in action_type:
            return StopActionFactory(action=self.action,
                                     task_activities=task_activities,
                                     xml_cache=self.xml_cache,
                                     processor=self.processor,
                                     mapping_cache=self.mapping_cache)
        elif "LoopAction" in action_type:
            return LoopActionFactory(action=self.action,
                                     task_activities=task_activities,
                                     xml_cache=self.xml_cache,
                                     processor=self.processor,
                                     mapping_cache=self.mapping_cache)
