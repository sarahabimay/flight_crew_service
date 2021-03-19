from functools import partial

from .crew_repository import CrewRepository
from .flights_repository import FlightsRepository


class EntityFactory:
    def entity(self, entity, location):
        repo_creator = self._get_repo_creator_for(entity)
        if repo_creator:
            return repo_creator(location)
        return None

    def _get_repo_creator_for(self, entity):
        if entity.lower() == 'crew':
            return partial(self._create_repository, CrewRepository)
        elif entity == 'flights':
            return partial(self._create_repository, FlightsRepository)
        return None

    @staticmethod
    def _create_repository(repository_klass, location):
        return repository_klass(location)

