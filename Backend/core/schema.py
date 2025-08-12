from drf_spectacular.extensions import OpenApiAuthenticationExtension


class APIKeyHeaderScheme(OpenApiAuthenticationExtension):
    target_class = 'core.authentication.HeaderAPIKeyAuthentication'
    name = 'apiKey'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
        }


