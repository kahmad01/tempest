# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib

from tempest.api_schema.response.compute.v2_1 import flavors as schema
from tempest.api_schema.response.compute.v2_1 import flavors_access \
    as schema_access
from tempest.api_schema.response.compute.v2_1 import flavors_extra_specs \
    as schema_extra_specs
from tempest.common import service_client


class FlavorsClient(service_client.ServiceClient):

    def list_flavors(self, detail=False, **params):
        url = 'flavors'
        _schema = schema.list_flavors

        if detail:
            url += '/detail'
            _schema = schema.list_flavors_details
        if params:
            url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url)
        body = json.loads(body)
        self.validate_response(_schema, resp, body)
        return service_client.ResponseBody(resp, body)

    def show_flavor(self, flavor_id):
        resp, body = self.get("flavors/%s" % flavor_id)
        body = json.loads(body)
        self.validate_response(schema.create_get_flavor_details, resp, body)
        return service_client.ResponseBody(resp, body)

    def create_flavor(self, **kwargs):
        """Creates a new flavor or instance type.
        Most parameters except the following are passed to the API without
        any changes.
        :param ephemeral: The name is changed to OS-FLV-EXT-DATA:ephemeral
        :param is_public: The name is changed to os-flavor-access:is_public
        """
        if kwargs.get('ephemeral'):
            kwargs['OS-FLV-EXT-DATA:ephemeral'] = kwargs.pop('ephemeral')
        if kwargs.get('is_public'):
            kwargs['os-flavor-access:is_public'] = kwargs.pop('is_public')

        post_body = json.dumps({'flavor': kwargs})
        resp, body = self.post('flavors', post_body)

        body = json.loads(body)
        self.validate_response(schema.create_get_flavor_details, resp, body)
        return service_client.ResponseBody(resp, body)

    def delete_flavor(self, flavor_id):
        """Deletes the given flavor."""
        resp, body = self.delete("flavors/{0}".format(flavor_id))
        self.validate_response(schema.delete_flavor, resp, body)
        return service_client.ResponseBody(resp, body)

    def is_resource_deleted(self, id):
        # Did not use show_flavor(id) for verification as it gives
        # 200 ok even for deleted id. LP #981263
        # we can remove the loop here and use get by ID when bug gets sortedout
        flavors = self.list_flavors(detail=True)['flavors']
        for flavor in flavors:
            if flavor['id'] == id:
                return False
        return True

    @property
    def resource_type(self):
        """Returns the primary type of resource this client works with."""
        return 'flavor'

    def set_flavor_extra_spec(self, flavor_id, **kwargs):
        """Sets extra Specs to the mentioned flavor."""
        post_body = json.dumps({'extra_specs': kwargs})
        resp, body = self.post('flavors/%s/os-extra_specs' % flavor_id,
                               post_body)
        body = json.loads(body)
        self.validate_response(schema_extra_specs.set_get_flavor_extra_specs,
                               resp, body)
        return service_client.ResponseBody(resp, body)

    def list_flavor_extra_specs(self, flavor_id):
        """Gets extra Specs details of the mentioned flavor."""
        resp, body = self.get('flavors/%s/os-extra_specs' % flavor_id)
        body = json.loads(body)
        self.validate_response(schema_extra_specs.set_get_flavor_extra_specs,
                               resp, body)
        return service_client.ResponseBody(resp, body)

    def show_flavor_extra_spec(self, flavor_id, key):
        """Gets extra Specs key-value of the mentioned flavor and key."""
        resp, body = self.get('flavors/%s/os-extra_specs/%s' % (flavor_id,
                              key))
        body = json.loads(body)
        self.validate_response(
            schema_extra_specs.set_get_flavor_extra_specs_key,
            resp, body)
        return service_client.ResponseBody(resp, body)

    def update_flavor_extra_spec(self, flavor_id, key, **kwargs):
        """Update specified extra Specs of the mentioned flavor and key."""
        resp, body = self.put('flavors/%s/os-extra_specs/%s' %
                              (flavor_id, key), json.dumps(kwargs))
        body = json.loads(body)
        self.validate_response(
            schema_extra_specs.set_get_flavor_extra_specs_key,
            resp, body)
        return service_client.ResponseBody(resp, body)

    def unset_flavor_extra_spec(self, flavor_id, key):
        """Unsets extra Specs from the mentioned flavor."""
        resp, body = self.delete('flavors/%s/os-extra_specs/%s' %
                                 (flavor_id, key))
        self.validate_response(schema.unset_flavor_extra_specs, resp, body)
        return service_client.ResponseBody(resp, body)

    def list_flavor_access(self, flavor_id):
        """Gets flavor access information given the flavor id."""
        resp, body = self.get('flavors/%s/os-flavor-access' % flavor_id)
        body = json.loads(body)
        self.validate_response(schema_access.add_remove_list_flavor_access,
                               resp, body)
        return service_client.ResponseBody(resp, body)

    def add_flavor_access(self, flavor_id, tenant_id):
        """Add flavor access for the specified tenant."""
        post_body = {
            'addTenantAccess': {
                'tenant': tenant_id
            }
        }
        post_body = json.dumps(post_body)
        resp, body = self.post('flavors/%s/action' % flavor_id, post_body)
        body = json.loads(body)
        self.validate_response(schema_access.add_remove_list_flavor_access,
                               resp, body)
        return service_client.ResponseBody(resp, body)

    def remove_flavor_access(self, flavor_id, tenant_id):
        """Remove flavor access from the specified tenant."""
        post_body = {
            'removeTenantAccess': {
                'tenant': tenant_id
            }
        }
        post_body = json.dumps(post_body)
        resp, body = self.post('flavors/%s/action' % flavor_id, post_body)
        body = json.loads(body)
        self.validate_response(schema_access.add_remove_list_flavor_access,
                               resp, body)
        return service_client.ResponseBody(resp, body)
