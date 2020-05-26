"""
    This type of algorithm have two obligatory functions:

        *initial_allocation*: invoked at the start of the simulation

        *run* invoked according to the assigned temporal distribution.

"""

from yafs.placement import Placement

class UCPlacement(Placement):
    def __init__(self, logger = None, **kwargs):
        self.cache = {}
        self.previous_number_of_nodes = -1
        self.mlt_task = 0
        self.flt_task = 0
        self.dlt_task = 0
        super(UCPlacement, self).__init__(**kwargs)


    """
    This implementation locates the services of the application in the cheapest cloud regardless of where the sources or sinks are located.

    It only runs once, in the initialization.

    """
    def initial_allocation(self, sim, app_name):
        #We find the ID-nodo/resource
        # Recupera a lista de nos com as propriedades definidas. Ex [4, 5]
        id_flt = sim.topology.find_IDs({"type":"flt"})
        id_mlt = sim.topology.find_IDs({"type":"mlt"})
        id_dlt = sim.topology.find_IDs({"type":"dlt"})

        app = sim.apps[app_name]
        services = app.services
        for module in services:
            if module == "FLTTask":
                # faz o deploy somente no primeiro noh da lista
                idDES = sim.deploy_module(app_name,module,services[module],[id_flt[0]])
                self.flt_task = self.flt_task + 1
            if module == "MLTTask":
                idDES = sim.deploy_module(app_name,module,services[module],[id_mlt[0]])
                self.mlt_task = self.mlt_task + 1
            if module == "DLTTask":
                idDES = sim.deploy_module(app_name,module,services[module],[id_dlt[0]])
                self.dlt_task = self.dlt_task + 1
            # if module in self.scaleServices:
                # for rep in range(0, self.scaleServices[module]):
                    # idDES = sim.deploy_module(app_name,module,services[module],id_flt)
        print ("***************QTD DEPLOY DOS SERVICOS MLT**************", self.mlt_task)
        print ("***************QTD DEPLOY DOS SERVICOS FLT**************", self.flt_task)
        print ("***************QTD DEPLOY DOS SERVICOS DLT**************", self.dlt_task)

    #end function