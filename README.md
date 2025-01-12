rdmo-plugins-ror
================

This plugin implements dynamic option set, that queries the expanded-search endpoint of the [ROR API](https://ror.readme.io/docs/rest-api).


Setup
-----

Install the plugin in your RDMO virtual environment using pip (directly from GitHub):

```bash
pip install git+https://github.com/rdmorganiser/rdmo-plugins-ror
```

Add the `rdmo_ror` app to `INSTALLED_APPS` and the plugin to `OPTIONSET_PROVIDERS` in `config/settings/local.py`:

```python
INSTALLED_APPS += ['rdmo_ror']

...

OPTIONSET_PROVIDERS += [
    ('ror', _('ROR Provider'), 'rdmo_ror.providers.RORProvider')
]
```

The option set provider should now be selectable for option sets in your RDMO installation. For a minimal example catalog, see the files in `xml`.

If a selection of a ROR ID should update other fields, you can add a `ROR_PROVIDER_MAP` in your settings, e.g.:

```python
v_PROVIDER_MAP = [
    {
        'ror': 'https://rdmorganiser.github.io/terms/domain/project/partner/ror',
        'acronym': 'https://rdmorganiser.github.io/terms/domain/project/partner/id',
        'name': 'https://rdmorganiser.github.io/terms/domain/project/partner/name',
    }
]
```

In this case, a change to the identifier of a partner (`https://rdmorganiser.github.io/terms/domain/project/partner/ror`) will update their name (`https://rdmorganiser.github.io/terms/domain/project/partner/name`) automatically. `ROR_PROVIDER_MAP` is a list of mappings, since multiple ROR ID could be used and should update different other values.

While not required, you can add a custom `User-Agent` to your requests so that the provider can perform statistical analyses and, if you add an email address, might contact you. This can be done by adding the following to your settings.

```python
ROR_PROVIDER_HEADERS = {
    'User-Agent': 'rdmo.example.com/1.0 (mail@rdmo.example.com) rdmo-plugins-ror/1.0'
}
```
