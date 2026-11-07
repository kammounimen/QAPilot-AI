from abc import ABC, abstractmethod


class TestManagementBackend(ABC):
    """Interface commune : FileBackend maintenant, XrayBackend plus tard."""

    @abstractmethod
    def find_by_external_id(self, external_id: str) -> str | None:
        """Retourne la clé du test si elle existe déjà, sinon None."""

    @abstractmethod
    def create_test(self, case: dict) -> str:
        """Crée le test et retourne sa clé."""

    @abstractmethod
    def update_test(self, key: str, case: dict) -> None:
        """Met à jour un test existant."""

    @abstractmethod
    def import_results(self, results: list[dict]) -> str:
        """Importe les résultats d'exécution, retourne un identifiant d'exécution."""
