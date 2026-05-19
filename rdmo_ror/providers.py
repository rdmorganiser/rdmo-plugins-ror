import re

from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import get_language

import requests

from rdmo.options.providers import Provider


class RorProvider(Provider):
    search = True
    refresh = True

    def get_options(self, project, search=None, user=None, site=None):
        if search:
            url = getattr(settings, 'ROR_PROVIDER_URL', 'https://api.ror.org/v2/').rstrip('/')
            headers = getattr(settings, 'ROR_PROVIDER_HEADERS', {})

            response = requests.get(
                url + '/organizations',
                params={
                    'query': self.get_search(search),
                },
                headers=headers,
            )

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                pass
            else:
                if data.get('items'):
                    return [
                        {
                            'id': self.get_id(item),
                            'text': self.get_text(item),
                            'help': self.get_help(item),
                        }
                        for item in data['items']
                    ]

        # return an empty list by default
        return []

    def get_id(self, item):
        return item.get('id', '').replace('https://ror.org/', '')

    def get_text(self, item):
        ror_id = item['id']
        ror_name = self.get_name(item) if getattr(settings, 'ROR_STORE_NAME', True) else ''
        ror_img = static('ror/img/ROR.png')
        ror_link = f'<a href="{ror_id}"><img height="16" src="{ror_img}" alt="ROR logo" /> {ror_id}</a>'
        return f'{ror_name} {ror_link}' if ror_name else ror_link

    def get_name(self, item):
        lang = get_language()

        label_list = [
            name['value'] for name in item.get('names', []) if 'label' in name['types'] and name['lang'] == lang
        ]  # fmt: skip
        ror_display_list = [
            name['value'] for name in item.get('names', []) if 'ror_display' in name['types']
        ]  # fmt: skip

        return next(iter(label_list), None) or next(iter(ror_display_list), None)

    def get_help(self, item):
        return '' if getattr(settings, 'ROR_STORE_NAME', True) else f'[{self.get_name(item)}]'

    def get_search(self, search):
        # reverse get_text to perform the search, remove everything after [
        match = re.match(r'^[^[]+', search)
        if match:
            tokens = match[0].split()
        else:
            tokens = search.split()

        return '+AND+'.join(tokens)
