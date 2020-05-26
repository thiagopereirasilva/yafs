import random
import argparse
import time
import numpy as np
import sys as sys
import matplotlib.pyplot as plt
import networkx as nx

from yafs.core import Sim
from yafs.application import Application,Message
from yafs.population import *
from yafs.topology import Topology
from yafs.stats import Stats
from yafs.placement import ClusterPlacement, EdgePlacement, NoPlacementOfModules, Placement
from yafs.distribution import deterministicDistribution, deterministicDistributionStartPoint
from yafs.utils import fractional_selectivity

from UCSelection import MinimunPath, MinPath_RoundRobin
from UCPlacement import  UCPlacement
# isso foi inserido para ler a classe que criei em outro arquivo
sys.path.append(".")

RANDOM_SEED = 1

def create_application():
    # APLICATION
    a = Application(name="VLIoT")
    
    # MODULES (face detection, feature extraction, face recognition)
    a.set_modules([{"Camera":{"Type":Application.TYPE_SOURCE}},
                   {"MLTTask": {"RAM": 256, "Type": Application.TYPE_MODULE}},
                   {"FLTTask": {"RAM": 256, "Type": Application.TYPE_MODULE}},
                   {"DLTTask": {"Type": Application.TYPE_SINK}}
                   ])

    # MESSAGES
    m_cam_mlt = Message("M.Cam", "Camera", "MLTTask", instructions=1*10^6, bytes=2000)
    m_mlt_flt = Message("M.MLT", "MLTTask", "FLTTask", instructions=1*10^6, bytes=2000)
    m_flt_dlt = Message("M.FLT", "FLTTask", "DLTTask", instructions=1*10^6, bytes=2000)

    # Add in the application those messages that come from pure sources (sensors). This distinction allows them to be controlled by the (:mod:`Population`) algorithm
    a.add_source_messages(m_cam_mlt)

    # Este nao eh o caso de usar um service_source - VER EXEMPLO DE VRGAME
    # Um service_source normalmente modela um Module que produz dados de controle, por exemplo.
    # dDistribution = deterministicDistribution(name="Deterministic", time=100)
    # a.add_service_source("Camera", dDistribution, m_mlt_flt)

    # MODULE SERVICES
    a.add_service_module("MLTTask", m_cam_mlt, m_mlt_flt, fractional_selectivity,  threshold=1.0)
    a.add_service_module("FLTTask", m_mlt_flt, m_flt_dlt, fractional_selectivity,  threshold=1.0)
    a.add_service_module("DLTTask", m_flt_dlt)

    return a


def create_json_topology():
    ## MANDATORY FIELDS
    topology_json = {}
    topology_json["entity"] = []
    topology_json["link"] = []

    S_dev = {"id": 0, "type": "source", "model": "camera", "name": "S", "IPT": 10 * 10 ^ 6, "RAM": 100,"COST": 3, "WATT": 30.0}

    U1_dev  = {"id": 1, "type": "mlt", "model": "node", "name": "U1", "IPT": 10* 10 ^ 6, "RAM": 4000,"COST": 3,"WATT":40.0}
    U2_dev  = {"id": 2, "type": "mlt", "model": "node", "name": "U2", "IPT": 10* 10 ^ 6, "RAM": 4000,"COST": 3,"WATT":40.0}
    U3_dev  = {"id": 3, "type": "mlt", "model": "node", "name": "U3", "IPT": 10* 10 ^ 6, "RAM": 4000,"COST": 3,"WATT":40.0}

    V1_dev  = {"id": 4, "type": "flt", "model": "node", "name": "V1", "IPT": 10* 10 ^ 6, "RAM": 4000,"COST": 3,"WATT":20.0}
    V2_dev  = {"id": 5, "type": "flt", "model": "node", "name": "V2", "IPT": 10* 10 ^ 6, "RAM": 4000,"COST": 3,"WATT":20.0}

    T_dev   = {"id": 6, "type": "dlt", "model": "sink", "name": "T", "IPT": 10 * 10 ^ 6, "RAM": 40000,"COST": 10,"WATT":100.0}
    

    link_S_U1 = {"s": 0, "d": 1, "BW": 12, "PR": 12}
    link_S_U2 = {"s": 0, "d": 2, "BW": 8, "PR": 8}
    link_S_U3 = {"s": 0, "d": 3, "BW": 10, "PR": 10}

    link_U1_V1 = {"s": 1, "d": 4, "BW": 12, "PR": 12}
    link_U1_V2 = {"s": 1, "d": 5, "BW": 12, "PR": 12}
    link_U2_V1 = {"s": 2, "d": 4, "BW": 8, "PR": 8}
    link_U2_V2 = {"s": 2, "d": 5, "BW": 8, "PR": 8}
    link_U3_V1 = {"s": 3, "d": 4, "BW": 10, "PR": 10}
    link_U3_V2 = {"s": 3, "d": 5, "BW": 10, "PR": 10}

    link_V1_T = {"s": 4, "d": 6, "BW": 16, "PR": 16}
    link_V2_T = {"s": 5, "d": 6, "BW": 16, "PR": 16}
 
    topology_json["entity"].append(S_dev)
    topology_json["entity"].append(U1_dev)
    topology_json["entity"].append(U2_dev)
    topology_json["entity"].append(U3_dev)
    topology_json["entity"].append(V1_dev)
    topology_json["entity"].append(V2_dev)
    topology_json["entity"].append(T_dev)

    topology_json["link"].append(link_S_U1)
    topology_json["link"].append(link_S_U2)
    topology_json["link"].append(link_S_U3)

    topology_json["link"].append(link_U1_V1)
    topology_json["link"].append(link_U1_V2)
    topology_json["link"].append(link_U2_V1)
    topology_json["link"].append(link_U2_V2)
    topology_json["link"].append(link_U3_V1)
    topology_json["link"].append(link_U3_V2)

    topology_json["link"].append(link_V1_T)
    topology_json["link"].append(link_V2_T)

    return topology_json


# @profile
def main(simulated_time):

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    """
    TOPOLOGY from a json
    """
    t = Topology()
    t_json = create_json_topology()
    t.load(t_json)
    t.write("network.gexf")

    """
    APPLICATION
    """
    app = create_application()

    """
    PLACEMENT algorithm
    """
    # MINHA IMPLEMENTACAO DO ALGORITMO PARA PLACEMENT.
    # UTILIZA A PROPRIEDADE model:node
    placement = UCPlacement(name="UCPlacement")

    # Para criar replicas dos servicos
    placement.scaleService({"MLTTask": 1, "FLTTask":1, "DLTTask":1})

    """
    POPULATION algorithm
    """
    #In ifogsim, during the creation of the application, the Sensors are assigned to the topology, in this case no. As mentioned, YAFS differentiates the adaptive sensors and their topological assignment.
    #In their case, the use a statical assignment.
    pop = Statical("Statical")
    #For each type of sink modules we set a deployment on some type of devices
    #A control sink consists on:
    #  args:
    #     model (str): identifies the device or devices where the sink is linked
    #     number (int): quantity of sinks linked in each device
    #     module (str): identifies the module from the app who receives the messages
    pop.set_sink_control({"model": "sink","number":0,"module":app.get_sink_modules()})

    #In addition, a source includes a distribution function:
    dDistribution = deterministicDistribution(name="Deterministic",time=10)
    # delayDistribution = deterministicDistributionStartPoint(400, 100, name="DelayDeterministic")
    
    # number:quantidade de replicas
    pop.set_src_control({"model": "camera", "number":1,"message": app.get_message("M.Cam"), "distribution": dDistribution})
    # pop.set_src_control({"type": "mlt", "number":1,"message": app.get_message("M.MLT"), "distribution": dDistribution})
    

    """
    SELECTOR algorithm
    """
    #Their "selector" is actually the shortest way, there is not type of orchestration algorithm.
    #This implementation is already created in selector.class,called: First_ShortestPath
    selectorPath = MinimunPath()
    # selectorPath = MinPath_RoundRobin()
    

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(t, default_results_path="Results")
    s.deploy_app(app, placement, pop, selectorPath)
    s.run(stop_time,show_progress_monitor=False)

    s.draw_allocated_topology() # for debugging
    # Tentativa frustrada de melhorar a representacao da topologia e salvar em um arquivo
    # G = s.topology.G
    # pos = nx.spring_layout(G)
    # nx.draw(G, pos, node_color='r', edge_color='b', with_labels=True)
    # # for p in pos:  # raise text positions
    # #     pos[p][1] += 0.07
    # nx.draw_networkx_labels(G, pos)
    # # plt.show()
    # plt.savefig('books_read.png')


if __name__ == '__main__':
    import logging.config
    import os

    logging.config.fileConfig('/home/thiago/YAFS/src/examples/Tutorial/logging.ini')

    start_time = time.time()
    # duracao a simulacao
    simulated_time = 100
    main(simulated_time=simulated_time)

    print("\n--- %s seconds ---" % (time.time() - start_time))

    ### Finally, you can analyse the results:
    print "-"*20
    print "Results:"
    print "-" * 20
    m = Stats(defaultPath="Results") #Same name of the results
    time_loops = [["M.Cam1","M.MLT", "M.FLT"]]
    # TODO: COLOCAR AS OUTRAS MENSAGENS EM time_loops
    m.showResults2(simulated_time, time_loops=time_loops)
    m.df["date"] = m.df.time_in.astype('datetime64[s]')
    m.df.index = m.df.date

    print "Media da latencia a cada 10 segundos"
    print m.df.resample('10s').agg(dict(time_latency='mean'))
    print "\t- Network saturation -"
    print "\t\tAverage waiting messages : %i" % m.average_messages_not_transmitted()
    print "\t\tPeak of waiting messages : %i" % m.peak_messages_not_transmitted()
    print "\t\tTOTAL messages not transmitted: %i" % m.messages_not_transmitted()

    # print "\n\t- Stats of each service deployed -"
    # print m.get_df_modules()
    # print "-------------------"
    # print m.get_df_service_utilization("ProcessingTask",1000)
    # print m.get_df_service_utilization("Sink",1000)
