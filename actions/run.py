import json

from lib.action import NetboxBaseAction
from st2client.client import Client
from st2client.models import KeyValuePair


class NetboxHTTPAction(NetboxBaseAction):
    """Base run action"""

    def run(self, endpoint_uri, http_verb, get_detail_route_eligible, **kwargs):
        """Base run action
        """

        if http_verb in ('get', 'post') and kwargs.get('id', False) and get_detail_route_eligible:
            # modify the `endpoint_uri` to use the detail route
            endpoint_uri = f"{endpoint_uri}{str(kwargs.pop('id'))}/"
            self.logger.debug(f'endpoint_uri transformed to {endpoint_uri} because id was passed')


        if http_verb == 'get':
            if kwargs.get('save_in_key_store') and not kwargs.get('save_in_key_store_key_name'):
                return False, 'save_in_key_store_key_name MUST be used with save_in_key_store!'

            result = self.make_request(endpoint_uri, http_verb, **kwargs)

            if kwargs['save_in_key_store']:
                # save the result in the st2 keystore
                client = Client(base_url='http://localhost')
                key_name = kwargs['save_in_key_store_key_name']
                client.keys.update(KeyValuePair(name=key_name, value=json.dumps(result),
                                                ttl=kwargs['save_in_key_store_ttl']))

                return True, f"Result stored in st2 key {key_name}"
        else:
            result = self.make_request(endpoint_uri, http_verb, **kwargs)

        return result
