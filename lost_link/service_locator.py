class ServiceLocator:
    _services = {}

    @staticmethod
    def register_service(name: str, instance):
        ServiceLocator._services[name] = instance

    @staticmethod
    def get_service(name: str):
        return ServiceLocator._services[name]