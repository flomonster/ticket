from algoliasearch_django import AlgoliaIndex

class EventIndex(AlgoliaIndex):
    fields = ('title', 'description', 'start', 'cover')
    settings = {'searchableAttributes': ['name', 'description']}
    index_name = 'Event'

class AssociationIndex(AlgoliaIndex):
    fields = ('name', 'logo')
    settings = {'searchableAttributes': ['name']}
    index_name = 'Association'
