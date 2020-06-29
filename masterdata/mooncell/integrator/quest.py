from ...utils import Mst
from .common import Integrator


class QuestIG(Integrator):
    def setup(self):
        self.rename_column(Mst.Quest, name='jpName')
        self.add_column(Mst.Quest, cnName='TEXT')

        self.rename_column(Mst.Spot, name='jpName')
        self.add_column(Mst.Spot, cnName='TEXT')

    def integrate(self):
        # TODO: quest
        pass
