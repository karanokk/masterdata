from .common import Integrator


class MissionIG(Integrator):
    def setup(self):
        self.rename_column('mstQuest', name='jpName')
        self.add_column('mstQuest', cnName='TEXT')

        self.rename_column('mstSpot', name='jpName')
        self.add_column('mstSpot', cnName='TEXT')

    def integrate(self):
        # TODO: mission
        pass
