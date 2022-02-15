import pdb
import warnings
from typing import List

import msal
import requests

from powerbi_connector.decorators.request import get_all_info

__version__ = "1.0.0"


class PBIApiConnector:
    """
    PowerBI API Connector for Service Principal with Admin Rights, basically a wrapper for the official API
    with the purpose of facilitate the metadata extraction and group some endpoints from the official API.

    Pre-requisites and setup:
        https://docs.microsoft.com/en-us/power-bi/admin/read-only-apis-service-principal-authentication
        https://docs.microsoft.com/en-us/power-bi/admin/service-admin-metadata-scanning-setup

    Official docs:
        https://docs.microsoft.com/en-us/rest/api/power-bi/
    """

    PBI_DEFAULT_SCOPE = ['https://analysis.windows.net/powerbi/api/.default']

    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        """Acquires token for the current confidential client, not for an end user.

        :param str client_id: (Required)
            Client ID from the Service Principal with the right permissions
        :param str client_secret: (Required)
            Secret key from the Service Principal with the right permissions
        :param str tenant_id: (Required)
            Tenant ID from Power BI Application
        """
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.__client_secret = client_secret
        self.token = self.__get_credentials()

    def __build_header(self):
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}

    @staticmethod
    def __do_request(method: str, url: str, headers={}, params={}, payload={}):
        response = requests.request(method, headers=headers, url=url, params=params, data=payload)
        content = response.json()
        if 'exceeded' not in content:
            content.update({'status_code': response.status_code})
            return content
        return response.__dict__

    def __get_credentials(self):
        auth_context = msal.ConfidentialClientApplication(
            authority=f'https://login.microsoftonline.com/{self.tenant_id}',
            client_id=self.client_id,
            client_credential=self.__client_secret,
        )

        token = auth_context.acquire_token_for_client(scopes=self.PBI_DEFAULT_SCOPE)
        return token['access_token'] if token else None

    @get_all_info
    def get_groups_as_admin(self, top: int = 5000, expand: str = None, bfilter: str = None, skip: int = None):
        verb = 'GET'
        groups_url = f'https://api.powerbi.com/v1.0/myorg/admin/groups'
        params = {k: v for k, v in {'$top': top, '$expand': expand, '$filter': bfilter, '$skip': skip}.items() if
                  v is not None}
        groups = self.__do_request(method=verb, url=groups_url, headers=self.__build_header(), params=params)
        return groups

    @get_all_info
    def get_refreshables_for_group_as_admin(self, group: str = None,
                                            top: int = 5000, expand: str = 'group', skip: int = None):
        if group is not None:
            verb = 'GET'
            refreshables_url = f'https://api.powerbi.com/v1.0/myorg/admin/capacities/refreshables'
            params = {k: v for k, v in
                      {'$top': top,
                       '$expand': expand,
                       '$filter': f"group/id eq '{group}'",
                       '$skip': skip}.items() if
                      v is not None}
            refreshables = self.__do_request(method=verb, url=refreshables_url, headers=self.__build_header(),
                                             params=params)
            return refreshables
        return []

    @get_all_info
    def get_reports_for_group_as_admin(self, groupId: str = None,
                                       top: int = 5000, filter: str = None, skip: int = None):
        if groupId is not None:
            verb = 'GET'
            report_url = f'https://api.powerbi.com/v1.0/myorg/admin/groups/{groupId}/reports'
            params = {k: v for k, v in
                      {'$top': top,
                       '$filter': filter,
                       '$skip': skip}.items() if
                      v is not None}
            report = self.__do_request(method=verb, url=report_url, headers=self.__build_header(),
                                       params=params)
            return report
        return []

    def scan_result(self, scanId: str):
        """
        Retrieves the result of the inputed scanId

        :param str scanId:
            scanId obtained from scan_workspace response
        :return:
            Dict with metadata from the requested workspaces
        """
        verb = 'GET'
        scan_url = f'https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanResult/{scanId}'
        scan_result = self.__do_request(method=verb, url=scan_url, headers=self.__build_header())
        return scan_result

    def scan_status(self, scanId: str):
        """
        Returns status of request made by scan_workspaces

        :param str scanId: (Required)
            scanId obtained from scan_workspace response
        :return:
            payload with the scan status
        """
        verb = 'GET'
        scan_url = f'https://api.powerbi.com/v1.0/myorg/admin/workspaces/scanStatus/{scanId}'
        status = self.__do_request(method=verb, url=scan_url, headers=self.__build_header())
        return status

    def scan_workspaces(self, workspaces: List[str], datasetExpressions: bool = True, datasetSchema: bool = True,
                        datasourceDetails: bool = True, getArtifactUsers: bool = False, lineage: bool = True):
        """
        Start a workspace(s) scan on Power BI
        :param List[str] workspaces: (Required)
            The required workspace IDs to be scanned (supports 1 to 100 workspace IDs)
        :param bool datasetExpressions:
            Whether to return dataset expressions (Dax query and Mashup)
        :param bool datasetSchema:
            Whether to return dataset schema (Tables, Columns and Measures)
        :param bool datasourceDetails:
            Whether to return datasource details
        :param bool getArtifactUsers:
            Whether to return artifact user details (Preview) (Permission level)
        :param bool lineage:
            Whether to return lineage info (upstream dataflows, tiles, datasource IDs)
        :return:
            Dict with the creation status of the requested data
        """
        if len(workspaces) > 100:
            warnings.warn("This API can only retrieve 100 workspaces each request")

        verb = 'POST'
        scan_url = 'https://api.powerbi.com/v1.0/myorg/admin/workspaces/getInfo'
        payload = {
            'workspaces': workspaces,
        }
        params = {k: v for k, v in
                  {'datasetExpressions': datasetExpressions,
                   'datasetSchema': datasetSchema,
                   'datasourceDetails': datasourceDetails,
                   'getArtifactUsers': getArtifactUsers,
                   'lineage': lineage}.items()
                  if v is not None}
        status = self.__do_request(method=verb, url=scan_url, headers=self.__build_header(), payload=payload,
                                   params=params)
        return status
