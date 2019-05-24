from pyopteryx.utils.utils import open_xml_as_etree
from pyopteryx.utils.xml_utils import get_element_by_identifier


class XMLCache:
    """
    Cache for required PCM files whose contents can be accessed via the respective file name.
    """

    def __init__(self, xml_dict):
        self.cache = {}
        for file_name, file_path in xml_dict.items():
            # Clean repository file from excluded components
            if "repository" in file_name:
                self.__remove_element_from_repository(file_path=file_path, file_name=file_name)
            else:
                self.cache[file_name] = open_xml_as_etree(file_path)

    def get_xml_tree(self, name):
        """
        Get xml file by file name, if given name occurs in cached xml files.
        :param name: xml file name
        :return: xml file that corresponds to given name
        """
        for key in self.cache.keys():
            if key in name:
                return self.cache[key]

    def get_all_cached(self):
        """
        Get all cached xml files.
        :return: dict of cached xml files
        """
        return self.cache.items()

    def __remove_element_from_repository(self, file_path, file_name):
        """
        Exclude IAdminStub because it's "describedService__SEFF" is a duplicated id, that overshadows the
        "describedService__SEFF" id of "InnerCoreReportingEngine". IAdminStub's SEFFs don't show up in any sighted
        *in.lqxo file.
        :type file_name: repository file name
        :param file_path: repository file path
        :return: save cleaned repository to cache
        """
        # id of IAdminStub
        excluded_component_ids = ["_-anFcFE-EeCAJIcLKkksgA"]
        repository = open_xml_as_etree(xml_file_path=file_path)
        # Remove excluded components from repository and save cleaned repository afterwards in cache
        self.__remove_excluded_elements(excluded_ids=excluded_component_ids, repository=repository)

        # id of getCachedDataInner
        excluded_operation_ids = ["_IAymIKfFEd-L5vB0MCctNg"]
        # Remove excluded components from repository and save cleaned repository afterwards in cache
        self.__remove_excluded_elements(excluded_ids=excluded_operation_ids, repository=repository)

        # id of getCachedDataInner
        excluded_operation_ids = ["_IAymIKfFEd-L5vB0MCctNg"]
        # Remove excluded components from repository and save cleaned repository afterwards in cache
        self.__remove_excluded_elements(excluded_ids=excluded_operation_ids, repository=repository,
                                        attribute="describedService__SEFF")
        self.cache[file_name] = repository

    @staticmethod
    def __remove_excluded_elements(excluded_ids, repository, attribute="id"):
        for excluded_id in excluded_ids:
            excluded_component = get_element_by_identifier(attribute=attribute, search_string=excluded_id,
                                                           element_tree=repository)
            if excluded_component is not None:
                parent_element = excluded_component.getparent()
                if parent_element is not None:
                    parent_element.remove(excluded_component)
                else:
                    parent_element.remove(excluded_component)
