from pyopteryx.factories.loop_action_factories.external_action_factory import ExternalLoopActionFactory
from pyopteryx.factories.loop_action_factories.start_action_factory import StartLoopActionFactory
from pyopteryx.factories.loop_action_factories.stop_action_factory import StopLoopActionFactory
from pyopteryx.utils.xml_utils import get_action_type


class LoopActionFactory:
    def __init__(self, xml_cache, input_data, processor, action, mapping_cache):
        self.action = action
        self.input_data = input_data
        self.processor = processor
        self.xml_cache = xml_cache
        self.mapping_cache = mapping_cache

    def create_action_factory(self):
        action_type = get_action_type(action=self.action)
        if "Start" in action_type:
            return StartLoopActionFactory(action=self.action, xml_cache=self.xml_cache, input_data=self.input_data,
                                          processor=self.processor, mapping_cache=self.mapping_cache)
        elif "Stop" in action_type:
            return StopLoopActionFactory(action=self.action, xml_cache=self.xml_cache, input_data=self.input_data,
                                         processor=self.processor, mapping_cache=self.mapping_cache)
        elif "ExternalCallAction" in action_type:
            return ExternalLoopActionFactory(action=self.action, xml_cache=self.xml_cache, input_data=self.input_data,
                                             processor=self.processor, mapping_cache=self.mapping_cache)
