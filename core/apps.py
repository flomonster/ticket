from django.apps import AppConfig
from core.index import *
import algoliasearch_django as algoliasearch

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        events = self.get_model('Event')
        algoliasearch.register(events, EventIndex)
        associations = self.get_model('Association')
        algoliasearch.register(associations, AssociationIndex)
