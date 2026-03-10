from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import get_language

import requests

from rdmo.domain.models import Attribute
from rdmo.projects.models import Value
from rdmo.projects.signals import value_created, value_updated


@receiver(value_created, sender=Value)
@receiver(value_updated, sender=Value)
def ror_handler(signal, sender, instance=None, **kwargs):
    lang = get_language()

    # check for ROR_PROVIDER_MAP
    if not getattr(settings, 'ROR_PROVIDER_MAP', None):
        return

    # check if we are importing fixtures
    if kwargs.get('raw'):
        return

    # check if this value instance has an external_id
    if not instance.external_id:
        return

    # loop over ROR_PROVIDER_MAP and check if the value instance attribute is found
    for attribute_map in settings.ROR_PROVIDER_MAP:
        if 'ror' in attribute_map and instance.attribute.uri == attribute_map['ror']:
            # query the orcid api for the record for this orcid
            try:
                url = getattr(settings, 'ROR_PROVIDER_URL', 'https://api.ror.org/v2/').rstrip('/')
                headers = getattr(settings, 'ROR_PROVIDER_HEADERS', {})

                response = requests.get(f'{url}/organizations/{instance.external_id}', headers=headers)
                response.raise_for_status()

                data = response.json()
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
                return

            acronym = next(iter([
                name['value'] for name in data.get('names', []) if 'acronym' in name['types']
            ]), None)

            name = next(iter([
                name['value'] for name in data.get('names', []) if 'label' in name['types'] and name['lang'] == lang
            ]), None) or next(iter([
                name['value'] for name in data.get('names', []) if 'ror_display' in name['types']
            ]), None)

            if acronym and 'acronym' in attribute_map:
                Value.objects.update_or_create(
                    project=instance.project,
                    snapshot=None,
                    attribute=Attribute.objects.get(uri=attribute_map['acronym']),
                    set_prefix=instance.set_prefix,
                    set_index=instance.set_index,
                    defaults={
                        'text': acronym
                    }
                )

            if name and 'name' in attribute_map:
                Value.objects.update_or_create(
                    project=instance.project,
                    snapshot=None,
                    attribute=Attribute.objects.get(uri=attribute_map['name']),
                    set_prefix=instance.set_prefix,
                    set_index=instance.set_index,
                    defaults={
                        'text': name
                    }
                )
