from pyopteryx.factories.usage_action_factories.entrylevelsystemcall_usage_action_facotry import \
    EntryLevelSystemCallUsageActionFactory
from pyopteryx.factories.usage_action_factories.loop_usage_action_factory import LoopUsageActionFactory
from pyopteryx.factories.usage_action_factories.start_usage_action_factory import StartUsageActionFactory
from pyopteryx.factories.usage_action_factories.stop_usage_action_factory import StopUsageActionFactory
from pyopteryx.utils.xml_utils import get_action_type


class UsageActionFactory:
    def __init__(self, xml_cache, input_data, processor, action, mapping_cache):
        self.mapping_cache = mapping_cache
        self.action = action
        self.input_data = input_data
        self.processor = processor
        self.xml_cache = xml_cache

    def create_action_factory(self):
        """
        Creates and returns ActionFactory
        :return:
        """
        action_type = get_action_type(action=self.action)
        if "Start" in action_type:
            return StartUsageActionFactory(action=self.action, xml_cache=self.xml_cache, input_data=self.input_data,
                                           processor=self.processor)
        elif "Stop" in action_type:
            return StopUsageActionFactory(action=self.action, xml_cache=self.xml_cache, input_data=self.input_data,
                                          processor=self.processor)
        elif "EntryLevelSystemCall" in action_type:
            return EntryLevelSystemCallUsageActionFactory(action=self.action, xml_cache=self.xml_cache,
                                                          input_data=self.input_data, processor=self.processor,
                                                          mapping_cache=self.mapping_cache)
        else:
            return LoopUsageActionFactory(action=self.action, xml_cache=self.xml_cache, input_data=self.input_data,
                                          processor=self.processor)
