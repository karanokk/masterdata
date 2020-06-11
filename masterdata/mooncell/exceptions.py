class MooncellError(Exception):
    pass


class IntegrationError(MooncellError):
    pass


class MismatchedData(IntegrationError):
    def __init__(self, mc_data, mst_data):
        self.mc_data = mc_data
        self.mst_data = mst_data
