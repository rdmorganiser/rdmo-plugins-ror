import re

from django.conf import settings

import requests

from rdmo.options.providers import Provider


class RorProvider(Provider):

    search = True
    refresh = True

    def get_options(self, project, search=None, user=None, site=None):
        if search:
            url = getattr(settings, 'ROR_PROVIDER_URL', 'https://api.ror.org/v1/').rstrip('/')
            headers = getattr(settings, 'ROR_PROVIDER_HEADERS', {})

            response = requests.get(url + '/organizations', params={
                'query': self.get_search(search)
            }, headers=headers)

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                pass
            else:
                if data.get('items'):
                    return [
                        {
                            'id': self.get_id(item),
                            'text': self.get_text(item)
                        } for item in data['items']
                    ]

        # return an empty list by default
        return []

    def get_id(self, item):
        return item.get('id', '').replace('https://ror.org/', '')

    def get_text(self, item):
        return '{name} [{id}]'.format(name=item.get('name', ''), id=self.get_id(item))

    def get_search(self, search):
        # reverse get_text to perform the search, remove everything after [
        match = re.match(r'^[^[]+', search)
        if match:
            tokens = match[0].split()
        else:
            tokens = search.split()

        return '+AND+'.join(tokens)
