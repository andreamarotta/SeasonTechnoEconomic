import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib._pylab_helpers
from enum import Enum
import pandas as pd
import seaborn as sns
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

from geotypes import create_geotype

# Close all open figures
# Close all existing plots
plt.close('all')


# Enum definition for Radio Equipment types
class RadioEquipmentTypeEnum(Enum):
    MACRO_SUB_GHZ = "Macro sub GHz"
    MACRO_1_3_GHZ = "Macro 1-3 GHz"
    MACRO_3_7_GHZ = "Macro 3-7 GHz"
    MACRO_24_46_GHZ = "Macro 24-46 GHz"
    SMALL_3_7_GHZ = "Small 3-7 GHz"
    SMALL_7_15_GHZ = "Small 7-15 GHz"
    SMALL_24_46_GHZ = "Small 24-46 GHz"


# RadioEquipmentType class definition
class RadioEquipmentType:
    def __init__(self, bands_range, num_bands_mt, num_bands_lt, service, single_carrier_width, numerology, deployment):
        self.bands_range = bands_range
        self.num_bands_mt = num_bands_mt
        self.num_bands_lt = num_bands_lt
        self.service = service
        self.single_carrier_width = single_carrier_width
        self.numerology = numerology
        self.deployment = deployment  # New deployment field (Macro or Small)


# Global definition of radio equipment types
radio_equipment_types = {
    RadioEquipmentTypeEnum.MACRO_SUB_GHZ: RadioEquipmentType("Sub GHz", 4, 4, "mobile", 10, 0, "Macro"),
    RadioEquipmentTypeEnum.MACRO_1_3_GHZ: RadioEquipmentType("1-3 GHz", 4, 4, "mobile", 20, 0, "Macro"),
    RadioEquipmentTypeEnum.MACRO_3_7_GHZ: RadioEquipmentType("3-7 GHz", 2, 2, "Mob.&FWA", 100, 1, "Macro"),
    RadioEquipmentTypeEnum.MACRO_24_46_GHZ: RadioEquipmentType("24-46 GHz", 1, 1, "FWA", 200, 3, "Macro"),
    RadioEquipmentTypeEnum.SMALL_3_7_GHZ: RadioEquipmentType("3-7 GHz", 2, 3, "mobile", 100, 1, "Small"),
    RadioEquipmentTypeEnum.SMALL_7_15_GHZ: RadioEquipmentType("7-15 GHz", 0, 1, "mobile", 200, 2, "Small"),
    RadioEquipmentTypeEnum.SMALL_24_46_GHZ: RadioEquipmentType("24-46 GHz", 1, 2, "mobile", 200, 3, "Small")
}


class RadioEquipment:
    def __init__(self, equipment_type_enum):
        spec = radio_equipment_types[equipment_type_enum]
        self.equipment_type = equipment_type_enum
        self.bands_range = spec.bands_range
        self.num_bands_mt = spec.num_bands_mt
        self.num_bands_lt = spec.num_bands_lt
        self.service = spec.service
        self.single_carrier_width = spec.single_carrier_width
        self.numerology = spec.numerology

        # Add deployment property based on the equipment type
        self.deployment = "Macro" if "MACRO" in equipment_type_enum.name else "Small"

    def calculate_required_capacity(self, term):
        term_factor = {'short': 1, 'Medium': 2, 'Long': 3}
        factor = term_factor.get(term, 1)

        if self.deployment == "Macro":
            MIMO = 4
            multiplier = 0.27 * MIMO
            if term == 'Medium':
                return multiplier * self.num_bands_mt * self.single_carrier_width / 10
            elif term == 'Long':
                return multiplier * self.num_bands_lt * self.single_carrier_width / 10
            else:
                return 0
        elif self.deployment == "Small":
            MIMO = 4
            multiplier = 0.27 * MIMO
            if term == 'Medium':
                return multiplier * self.num_bands_mt * self.single_carrier_width / 10
            elif term == 'Long':
                return multiplier * self.num_bands_lt * self.single_carrier_width / 10
            else:
                return 0


# Enum definition for Network Equipment types
class NetworkEquipmentTypeEnum(Enum):
    GREY_TRANSCEIVERS_1G_SR = "1G SR (100m) MMF"
    GREY_TRANSCEIVERS_10G_SR = "10G SR (100m) MMF"
    GREY_TRANSCEIVERS_25G_SR = "25G SR (100m) MMF"
    GREY_TRANSCEIVERS_50G_SR = "50G SR (100m) MMF"
    GREY_TRANSCEIVERS_100G_SR = "100G SR (100m) MMF"
    GREY_TRANSCEIVERS_400G_SR = "400G SR (100m) MMF"
    GREY_TRANSCEIVERS_1G_LR = "1G LR/ER (30/40 km) SMF"
    GREY_TRANSCEIVERS_10G_LR = "10G LR/ER (30/40 km) SMF"
    GREY_TRANSCEIVERS_25G_LR = "25G LR/ER (30/40 km) SMF"
    GREY_TRANSCEIVERS_50G_LR = "50G LR/ER (30/40 km) SMF"
    GREY_TRANSCEIVERS_100G_LR = "100G LR/ER (30/40 km) SMF"
    GREY_TRANSCEIVERS_400G_LR = "400G LR/ER (30/40 km) SMF"
    WDM_TRANSCEIVERS_1G_LR = "WDM 1G LR/ER (30/40 km) SMF"
    WDM_TRANSCEIVERS_10G_LR = "WDM 10G LR/ER (30/40 km) SMF"
    WDM_TRANSCEIVERS_25G_LR = "WDM 25G LR/ER (30/40 km) SMF"
    WDM_TRANSCEIVERS_50G_LR = "WDM 50G LR/ER (30/40 km) SMF"
    WDM_TRANSCEIVERS_100G_LR = "WDM 100G LR/ER (30/40 km) SMF"
    WDM_TRANSCEIVERS_400G_LR = "WDM 400G LR/ER (30/40 km) SMF"
    CWDM_MUX = "CWDM multiplexer/demultiplexer"
    WDM_MUX = "WDM multiplexer/demultiplexer"
    SPLITTER_1_2 = "Splitter/combiner 1:2"
    SPLITTER_1_4 = "Splitter/combiner 1:4"
    SWITCH_SMALL = "small (2x200G)"
    SWITCH_MEDIUM = "medium (2x800G)"
    SWITCH_BIG = "Large (2x1.6T)"
    SWITCH_EXTRA_LARGE = "Extra Large (2x3.2T)"
    XR_MODULE_25G = "XR 25 G module"
    XR_MODULE_50G = "XR 50 G module"
    XR_MODULE_100G = "XR 100 G module"
    XR_MODULE_200G = "XR 200 G module"
    XR_MODULE_400G = "XR 400G module"
    XR_MODULE_HUB_100G = "XR 100 G HUB module"
    XR_MODULE_HUB_200G = "XR 200 G HUB module"
    XR_MODULE_HUB_400G = "XR 400G HUB module"
    MEDIA_CONVERTER_100G_4X25G = "Media Converter 100G (4x25G grey  -> 100G XR, 2x50G grey -> 100G XR, 100G grey -> 100G XR)"
    MEDIA_CONVERTER_200G_8X25G = "Media Converter 200G (8x25G grey  -> 200G XR, 4x50G grey  -> 200G XR, 2x100G grey -> 200G XR)"
    MEDIA_CONVERTER_400G_400G = "Media Converter 400G (400G XR -> 400G grey)"
    TRANSPONDER = "Transponder"


# Definition of the NetworkEquipmentType class
class NetworkEquipmentType:
    def __init__(self, name, data_rate, reach, price, normalized_price, max_power, typical_ff, insertion_loss=None,
                 size=None, note=None, capacity=None, num_ports=None):
        self.name = name
        self.data_rate = data_rate
        self.reach = reach
        self.price = price
        self.normalized_price = normalized_price
        self.max_power = max_power
        self.typical_ff = typical_ff
        self.insertion_loss = insertion_loss
        self.size = size
        self.note = note
        self.capacity = capacity  # Adding capacity attribute
        self.num_ports = num_ports  # Added the new num_ports attribute


# Global definition of network equipment types
network_equipment_types = {
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR: NetworkEquipmentType("1G SR (100m) MMF", 1, "100m MMF", 10.0,
                                                                           0.00, 1, "SFP"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR: NetworkEquipmentType("10G SR (100m) MMF", 10, "100m MMF", 20.0,
                                                                            0.00, 1, "SFP+"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR: NetworkEquipmentType("25G SR (100m) MMF", 25, "100m MMF", 40.0,
                                                                            0.01, 1, "SFP28"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR: NetworkEquipmentType("50G SR (100m) MMF", 50, "100m MMF", 270.0,
                                                                            0.05, 1.5, "SFP56"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR: NetworkEquipmentType("100G SR (100m) MMF", 100, "100m MMF",
                                                                             100.0, 0.02, 2.5, "QSFP28"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR: NetworkEquipmentType("400G SR (100m) MMF", 400, "100m MMF",
                                                                             400.0, 0.08, 10, "QSFP-DD"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_LR: NetworkEquipmentType("1G LR/ER (30/40 km) SMF", 1, "30/40 km SMF",
                                                                           50.0, 0.01, 1, "SFP"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_LR: NetworkEquipmentType("10G LR/ER (30/40 km) SMF", 10,
                                                                            "30/40 km SMF", 100.0, 0.02, 1, "SFP+"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_LR: NetworkEquipmentType("25G LR/ER (30/40 km) SMF", 25,
                                                                            "30/40 km SMF", 400.0, 0.08, 1.5, "SFP28"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_LR: NetworkEquipmentType("50G LR/ER (30/40 km) SMF", 50,
                                                                            "30/40 km SMF", 1000.0, 0.20, 4, "QSFP27"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR: NetworkEquipmentType("100G LR/ER (30/40 km) SMF", 100,
                                                                             "30/40 km SMF", 1500.0, 0.30, 4.5,
                                                                             "QSFP28"),
    NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_LR: NetworkEquipmentType("400G LR/ER (30/40 km) SMF", 400,
                                                                             "30/40 km SMF", 5000.0, 1.00, 10,
                                                                             "QSFP-DD"),
    NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_1G_LR: NetworkEquipmentType("WDM 1G LR/ER (30/40 km) SMF", 1,
                                                                          "30/40 km SMF", 100.0, 0.02, 1, "SFP+"),
    NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_10G_LR: NetworkEquipmentType("WDM 10G LR/ER (30/40 km) SMF", 10,
                                                                           "30/40 km SMF", 250.0, 0.05, 1.6, "SFP+"),
    NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_25G_LR: NetworkEquipmentType("WDM 25G LR/ER (30/40 km) SMF", 25,
                                                                           "30/40 km SMF", 800.0, 0.16, 2, "SFP28"),
    NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_50G_LR: NetworkEquipmentType("WDM 50G LR/ER (30/40 km) SMF", 50,
                                                                           "30/40 km SMF", 1800.0, 0.36, 4.5, "QSFP28"),
    NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_100G_LR: NetworkEquipmentType("WDM 100G LR/ER (30/40 km) SMF", 100,
                                                                            "30/40 km SMF", 2500.0, 0.50, 4.5,
                                                                            "QSFP28"),
    NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_400G_LR: NetworkEquipmentType("WDM 400G LR/ER (30/40 km) SMF", 400,
                                                                            "30/40 km SMF", 9000.0, 1.80, 10,
                                                                            "QSFP-DD"),
    NetworkEquipmentTypeEnum.CWDM_MUX: NetworkEquipmentType("CWDM multiplexer/demultiplexer", None, "8 channels", 800.0,
                                                            0.16, 1, 5.5),
    NetworkEquipmentTypeEnum.WDM_MUX: NetworkEquipmentType("WDM multiplexer/demultiplexer", None, "40 channels", 1200.0,
                                                           0.24, 1, 3.2),
    NetworkEquipmentTypeEnum.SPLITTER_1_2: NetworkEquipmentType("Splitter/combiner 1:2", None, "1:2", 100.0, 0.02, 0,
                                                                3.5),
    NetworkEquipmentTypeEnum.SPLITTER_1_4: NetworkEquipmentType("Splitter/combiner 1:4", None, "1:4", 100.0, 0.02, 0,
                                                                7.0),
    NetworkEquipmentTypeEnum.SWITCH_SMALL: NetworkEquipmentType("small (2x200G)", None, "", 3000.0, 0.60*4, 100, "", None,
                                                                "small", 250, 400),
    NetworkEquipmentTypeEnum.SWITCH_MEDIUM: NetworkEquipmentType("medium (2x800G)", None, "", 8000.0, 1.60*4, 300, "",
                                                                 None, "medium", 350, 1600),
    NetworkEquipmentTypeEnum.SWITCH_BIG: NetworkEquipmentType("Large (2x1.6T)", None, "", 14000.0, 2.80*4, 460, "", None,
                                                              "large", 460, 3200),
    NetworkEquipmentTypeEnum.SWITCH_EXTRA_LARGE: NetworkEquipmentType("Extra Large (2x3.2T)", None, "", 14001.0, 4.0*4.0,
                                                                      620, "", None, "extra_large", 620, 6400),
    NetworkEquipmentTypeEnum.XR_MODULE_25G: NetworkEquipmentType("XR 25 G module", 100,
                                                                 "coherent DSCM ≈ 200 km reach", 1000.0, 0.10, 3.5,
                                                                 "pluggable"),
    NetworkEquipmentTypeEnum.XR_MODULE_50G: NetworkEquipmentType("XR 50 G module", 100,
                                                                 "coherent DSCM ≈ 200 km reach", 2000.0, 0.16, 3.5,
                                                                 "pluggable"),
    NetworkEquipmentTypeEnum.XR_MODULE_100G: NetworkEquipmentType("XR 100 G module", 100,
                                                                  "coherent DSCM ≈ 200 km reach", 3000.0, 0.26, 3.5,
                                                                  "pluggable"),
    NetworkEquipmentTypeEnum.XR_MODULE_200G: NetworkEquipmentType("XR 200 G module", 200,
                                                                  "coherent DSCM ≈ 200 km reach", 5000.0, 0.42, 42, 4.5,
                                                                  "pluggable"),
    NetworkEquipmentTypeEnum.XR_MODULE_400G: NetworkEquipmentType("XR 400G module", 400, "coherent DSCM ≈ 200 km reach",
                                                                  9000.0, 0.76, 8, "pluggable"),
    NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G: NetworkEquipmentType("XR 100 G HUB module", 100,
                                                                      "coherent DSCM ≈ 200 km reach", 3000.0, 0.28, 3.5,
                                                                      "pluggable"),
    NetworkEquipmentTypeEnum.XR_MODULE_HUB_200G: NetworkEquipmentType("XR 200 G HUB module", 200,
                                                                      "coherent DSCM ≈ 200 km reach", 5000.0, 0.50, 4.5,
                                                                      "pluggable"),
    NetworkEquipmentTypeEnum.XR_MODULE_HUB_400G: NetworkEquipmentType("XR 400G HUB module", 400,
                                                                      "coherent DSCM ≈ 200 km reach",
                                                                      9000.0, 0.84, 8, "pluggable"),
    NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G: NetworkEquipmentType(
        "Media Converter 100G (4x25G grey  -> 100G XR, 2x50G grey -> 100G XR, 100G grey -> 100G XR)", 100,
        "for client-XR module adaptation", 2000.0, 0.30, 2, ""),
    NetworkEquipmentTypeEnum.MEDIA_CONVERTER_200G_8X25G: NetworkEquipmentType(
        "Media Converter 200G (8x25G grey  -> 200G XR, 4x50G grey  -> 200G XR, 2x100G grey -> 200G XR)", 200,
        "for client-XR module adaptation", 3000.0, 0.40, 3, ""),
    NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G: NetworkEquipmentType(
        "Media Converter 400G (400G XR -> 400G grey)", 400,
        "Usually it should not be necessary XR should be plugged directly in CO router", 5000.0, 0.50, 5, ""),
    NetworkEquipmentTypeEnum.TRANSPONDER: NetworkEquipmentType("Transponder", None, None, 4500.0, 0.90, 0, None, None,
                                                               None, 4.33, num_ports=5)  # Added the number of ports
}

# ============================================
# SALVATAGGIO E RIPRISTINO COSTI ORIGINALI
# ============================================

# Salva TUTTI i costi originali all'inizio del programma
ORIGINAL_ALL_COSTS = {}

def save_all_original_costs():
    """Salva tutti i costi originali di network equipment"""
    global ORIGINAL_ALL_COSTS
    for eq_enum in NetworkEquipmentTypeEnum:
        ORIGINAL_ALL_COSTS[eq_enum] = {
            'price': network_equipment_types[eq_enum].price,
            'normalized_price': network_equipment_types[eq_enum].normalized_price,
            'max_power': network_equipment_types[eq_enum].max_power
        }

def reset_all_costs_to_original():
    """Ripristina tutti i costi ai valori originali"""
    for eq_enum, original_values in ORIGINAL_ALL_COSTS.items():
        network_equipment_types[eq_enum].price = original_values['price']
        network_equipment_types[eq_enum].normalized_price = original_values['normalized_price']
        network_equipment_types[eq_enum].max_power = original_values['max_power']


# CHIAMA QUESTA FUNZIONE SUBITO DOPO LE DEFINIZIONI DI network_equipment_types
# Mettila subito dopo la riga: network_equipment_types = { ... }
save_all_original_costs()

# Updated NetworkEquipment class
class NetworkEquipment:
    def __init__(self, equipment_type_enum):
        spec = network_equipment_types[equipment_type_enum]
        self.equipment_type = equipment_type_enum
        self.data_rate = spec.data_rate
        self.reach = spec.reach
        self.price = spec.price
        self.normalized_price = spec.normalized_price
        self.max_power = spec.max_power
        self.typical_ff = spec.typical_ff
        self.insertion_loss = spec.insertion_loss
        self.size = spec.size
        self.note = spec.note
        self.capacity = spec.capacity


class Fiber:
    def __init__(self, num_wavelengths=10):
        self.wavelengths = {f'wavelength_{i}': np.random.randint(0, 81) for i in range(num_wavelengths)}


def create_mst(numNodes=50, squareSize=200):
    halfSize = squareSize / 2

    # Generation of random points
    points = -halfSize + squareSize * np.random.rand(numNodes, 2)
    points[0, :] = [0, 0]  # The root of the tree is fixed at (0,0)

    # Creation of the Manhattan distance matrix
    distances = np.zeros((numNodes, numNodes))
    for i in range(numNodes):
        for j in range(numNodes):
            distances[i, j] = np.sum(np.abs(points[i, :] - points[j, :]))

    # Creation of the graph with Manhattan distances
    G = nx.Graph()
    for i in range(numNodes):
        for j in range(i + 1, numNodes):
            G.add_edge(i, j, weight=distances[i, j])

    # Compute the minimum spanning tree using Prim's algorithm
    T = nx.minimum_spanning_tree(G, weight='weight', algorithm='prim')

    return T, points


def add_node_types(T, points):
    numNodes = len(T.nodes())
    types = np.random.randint(1, 3, numNodes)
    types[0] = 0  # The node at the origin is of type 0

    for node in T.nodes():
        T.nodes[node]['type'] = types[node]
        T.nodes[node]['position'] = points[node]
        T.nodes[node]['id'] = node  # Add node ID

    return T, types


def add_properties(T):
    for node in T.nodes():
        network_equipment = []
        for eq_enum in NetworkEquipmentTypeEnum:
            equipment = NetworkEquipment(eq_enum)
            network_equipment.append(equipment)

        radio_equipment = []
        for eq_enum in RadioEquipmentTypeEnum:
            equipment = RadioEquipment(eq_enum)
            radio_equipment.append(equipment)

        T.nodes[node]['radio_equipment'] = radio_equipment
        T.nodes[node]['network_equipment'] = network_equipment

    for u, v in T.edges():
        fibers = [Fiber() for _ in range(np.random.randint(1, 5))]
        T.edges[u, v]['fibers'] = fibers
        T.edges[u, v]['distance'] = T.edges[u, v]['weight']

    return T


def add_specific_network_equipment(T, node, equipment_type_enum):
    # Add a specific network equipment to the node based on the enum type
    specific_equipment = NetworkEquipment(equipment_type_enum)
    if 'network_equipment' not in T.nodes[node]:
        T.nodes[node]['network_equipment'] = []
    T.nodes[node]['network_equipment'].append(specific_equipment)


# Function to add a specific radio equipment
def add_specific_radio_equipment(T, node, equipment_type_enum):
    specific_equipment = RadioEquipment(equipment_type_enum)
    if 'radio_equipment' not in T.nodes[node]:
        T.nodes[node]['radio_equipment'] = []
    T.nodes[node]['radio_equipment'].append(specific_equipment)


def add_radio_equipment_based_on_scenario(T, node, term, scenario):
    node_type = T.nodes[node]['type']
    scenarios = {"Dense Urban": 0, "Urban": 1, "Suburban": 2, "Rural": 3}
    term_index = {'Medium': 0, 'Long': 1}[term]
    scenario_index = scenarios[scenario]

    radio_equipment_to_add = {
        1: [
            (RadioEquipmentTypeEnum.MACRO_SUB_GHZ, [[2, 2], [2, 3], [2, 4], [1, 3]]),
            (RadioEquipmentTypeEnum.MACRO_1_3_GHZ, [[3, 4], [2, 4], [2, 3], [1, 2]]),
            (RadioEquipmentTypeEnum.MACRO_3_7_GHZ, [[2, 2], [1, 2], [1, 2], [1, 1]]),
            (RadioEquipmentTypeEnum.MACRO_24_46_GHZ, [[0, 0], [0, 0], [1, 1], [1, 1]])
        ],
        2: [
            (RadioEquipmentTypeEnum.SMALL_3_7_GHZ, [[2, 3], [1, 2], [0, 1], [0, 0]]),
            (RadioEquipmentTypeEnum.SMALL_7_15_GHZ, [[0, 1], [0, 1], [0, 0], [0, 0]]),
            (RadioEquipmentTypeEnum.SMALL_24_46_GHZ, [[1, 2], [1, 1], [0, 1], [0, 0]])
        ]
    }

    if node_type in radio_equipment_to_add:
        for eq_enum, quantities in radio_equipment_to_add[node_type]:
            quantity = quantities[scenario_index][term_index] if node_type == 2 else quantities[scenario_index][
                                                                                         term_index] * 3
            for _ in range(quantity):
                add_specific_radio_equipment(T, node, eq_enum)


def deploy_radio_equipment(T, term, scenario):
    for node in T.nodes():
        add_radio_equipment_based_on_scenario(T, node, term, scenario)


def calculate_cost_component(T, component_types):
    total_cost = 0.0
    for node in T.nodes():
        for equipment in T.nodes[node]['network_equipment']:
            if any(comp_type in equipment.equipment_type.name for comp_type in component_types):
                total_cost += network_equipment_types[equipment.equipment_type].normalized_price
    return total_cost


def initialize_node_equipment(T):
    for node in T.nodes():
        if 'radio_equipment' not in T.nodes[node]:
            T.nodes[node]['radio_equipment'] = []
        if 'network_equipment' not in T.nodes[node]:
            T.nodes[node]['network_equipment'] = []
        if 'other_consumption' not in T.nodes[node]:
            T.nodes[node]['other_consumption'] = 0
        if 'switching_consumption' not in T.nodes[node]:
            T.nodes[node]['switching_consumption'] = 0


def allocate_capacity_macro(T, path, total_required_capacity):
    # Create a pair of fibers for the entire path and allocate the total capacity
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]

        if 'fibers' not in T.edges[u, v]:
            T.edges[u, v]['fibers'] = []

        # Create two new fibers for the entire path
        T.edges[u, v]['fibers'].append(Fiber())
        T.edges[u, v]['fibers'].append(Fiber())

        fibers_to_use = T.edges[u, v]['fibers'][-2:]  # Use the last two added fibers

        # Occupy one wavelength on each fiber
        for fiber in fibers_to_use:
            for wavelength, current_capacity in fiber.wavelengths.items():
                if current_capacity == 0:
                    fiber.wavelengths[wavelength] = total_required_capacity
                    break  # Exit the loop after occupying the capacity


def allocate_capacity_small(T, path, radio_equipment, term):
    # Create a pair of fibers for each radio equipment and allocate the specific capacity
    for radio_eq in radio_equipment:
        required_capacity = radio_eq.calculate_required_capacity(term)

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]

            if 'fibers' not in T.edges[u, v]:
                T.edges[u, v]['fibers'] = []

            # Create two new fibers for each radio equipment
            T.edges[u, v]['fibers'].append(Fiber())
            T.edges[u, v]['fibers'].append(Fiber())

            fibers_to_use = T.edges[u, v]['fibers'][-2:]  # Use the last two added fibers

            # Occupy one wavelength on each fiber
            for fiber in fibers_to_use:
                for wavelength, current_capacity in fiber.wavelengths.items():
                    if current_capacity == 0:
                        fiber.wavelengths[wavelength] = required_capacity
                        break  # Exit the loop after occupying the capacity


def soluzione_1_with_smallcellswitch(T, term):
    initialize_node_equipment(T)
    root_node = 0
    '''
    # Initialize energy consumption for each node to 0 for `switching_consumption` and `other_consumption`
    for node in T.nodes:
        node['switching_consumption'] = 0
        node['other_consumption'] = 0
    '''
    for node in T.nodes():
        if node == root_node:
            continue

        total_required_capacity = 0
        node_network_equipment = []

        # Calculate the total capacity required for the node
        for radio_eq in T.nodes[node]['radio_equipment']:
            required_capacity = radio_eq.calculate_required_capacity(term)
            total_required_capacity += required_capacity

            # Add a pair of grey short SR transceivers for each radio equipment
            if required_capacity <= 1:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR
            elif required_capacity <= 10:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR
            elif required_capacity <= 25:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
            elif required_capacity <= 50:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
            elif required_capacity <= 100:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
            else:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR

            node_network_equipment.append(NetworkEquipment(transceiver_type))
            node_network_equipment.append(NetworkEquipment(transceiver_type))

            # Update the node's `other_consumption` energy consumption
            T.nodes[node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2

        # Add the minimum number of grey LR transceivers to cover the total required capacity
        remaining_capacity = total_required_capacity
        while remaining_capacity > 0:
            if remaining_capacity <= 1:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_LR
                remaining_capacity -= 1
            elif remaining_capacity <= 10:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_LR
                remaining_capacity -= 10
            elif remaining_capacity <= 25:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_LR
                remaining_capacity -= 25
            elif remaining_capacity <= 50:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_LR
                remaining_capacity -= 50
            elif remaining_capacity <= 100:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR
                remaining_capacity -= 100
            else:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_LR
                remaining_capacity -= 400

            transceiver_instance = network_equipment_types[transceiver_type]
            node_network_equipment.append(NetworkEquipment(transceiver_type))
            T.nodes[root_node]['network_equipment'].append(NetworkEquipment(transceiver_type))

            # Allocate capacity along the path to the root node
            path = nx.shortest_path(T, source=node, target=root_node)
            allocate_capacity_macro(T, path, transceiver_instance.data_rate)

            # Update the `other_consumption` energy usage for the node and the root
            T.nodes[node]['other_consumption'] += transceiver_instance.max_power
            T.nodes[root_node]['other_consumption'] += transceiver_instance.max_power

        # Calculate the total capacity of all SR and LR transceivers
        total_transceiver_capacity = sum(
            (ne.data_rate / 2 if "SR" in ne.equipment_type.name else ne.data_rate)
            for ne in node_network_equipment if ne.data_rate is not None
        )

        # Choose the switch size based on the total capacity
        if total_transceiver_capacity > 0:
            if total_transceiver_capacity <= 400:
                switch_type = NetworkEquipmentTypeEnum.SWITCH_SMALL
            elif total_transceiver_capacity <= 1600:
                switch_type = NetworkEquipmentTypeEnum.SWITCH_MEDIUM
            elif total_transceiver_capacity <= 3200:
                switch_type = NetworkEquipmentTypeEnum.SWITCH_BIG
            else:
                switch_type = NetworkEquipmentTypeEnum.SWITCH_EXTRA_LARGE

            node_network_equipment.append(NetworkEquipment(switch_type))

            # Update the node's `switching_consumption` based on the added switch
            T.nodes[node]['switching_consumption'] += calculate_switch_power_consumption(switch_type,
                                                                                         total_transceiver_capacity)

        T.nodes[node]['network_equipment'].extend(node_network_equipment)

    # Add switches to the root node and update the energy consumption
    add_switches_to_root(T, root_node)


# Function to calculate the switch power consumption based on its type and total capacity
def calculate_switch_power_consumption(switch_type, total_capacity):
    power_model = {
        NetworkEquipmentTypeEnum.SWITCH_SMALL: [(0, 125), (20, 131), (40, 137), (60, 144), (80, 150), (100, 156),
                                                (120, 162), (140, 169), (160, 175), (180, 181), (200, 187), (220, 194),
                                                (240, 200), (260, 206), (280, 212), (300, 219), (320, 225), (340, 231),
                                                (360, 237), (380, 244), (400, 250)],
        NetworkEquipmentTypeEnum.SWITCH_MEDIUM: [(0, 175), (80, 184), (160, 193), (240, 201), (320, 210), (400, 219),
                                                 (480, 228), (560, 236), (640, 245), (720, 254), (800, 263), (880, 271),
                                                 (960, 280), (1040, 289), (1120, 298), (1200, 306), (1280, 315),
                                                 (1360, 324), (1440, 333), (1520, 341), (1600, 350)],
        NetworkEquipmentTypeEnum.SWITCH_BIG: [(0, 230), (160, 242), (320, 253), (480, 265), (640, 276), (800, 288),
                                              (960, 299), (1120, 311), (1280, 322), (1440, 334), (1600, 345),
                                              (1760, 357), (1920, 368), (2080, 380), (2240, 391), (2400, 403),
                                              (2560, 414), (2720, 426), (2880, 437), (3040, 449), (3200, 460)],
        NetworkEquipmentTypeEnum.SWITCH_EXTRA_LARGE: [(0, 310), (320, 326), (640, 341), (960, 357), (1280, 372),
                                                      (1600, 388), (1920, 403), (2240, 419), (2560, 434), (2880, 450),
                                                      (3200, 465), (3520, 481), (3840, 496), (4160, 512), (4480, 527),
                                                      (4800, 543), (5120, 558), (5440, 574), (5760, 589), (6080, 605),
                                                      (6400, 620)]
    }
    model = power_model[switch_type]

    for i in range(len(model) - 1):
        if model[i][0] <= total_capacity < model[i + 1][0]:
            return model[i][1]

    return model[-1][1]


def add_switches_to_root(T, root_node=0):
    total_capacity = 0

    # Sum the total capacity of the transceivers at the root node
    for equipment in T.nodes[root_node]['network_equipment']:
        if hasattr(equipment, 'data_rate') and equipment.data_rate is not None:
            total_capacity += equipment.data_rate

    total_capacity_for_energy = total_capacity

    # Add switches until all required capacity is supported
    while total_capacity > 0:
        if total_capacity <= 400:
            switch_type = NetworkEquipmentTypeEnum.SWITCH_SMALL
            total_capacity -= 400
        elif total_capacity <= 1600:
            switch_type = NetworkEquipmentTypeEnum.SWITCH_MEDIUM
            total_capacity -= 1600
        elif total_capacity <= 3200:
            switch_type = NetworkEquipmentTypeEnum.SWITCH_BIG
            total_capacity -= 3200
        else:
            switch_type = NetworkEquipmentTypeEnum.SWITCH_EXTRA_LARGE
            total_capacity -= 6400  # Capacity of the extra large switch

        T.nodes[root_node]['network_equipment'].append(NetworkEquipment(switch_type))
        T.nodes[root_node]['switching_consumption'] += calculate_switch_power_consumption(switch_type,
                                                                                          total_capacity_for_energy)


def allocate_capacity_wdm_on_path_macro(T, path, radio_equipment, term):
    if not path:
        return  # If the path is empty, do nothing

    # Create two new fibers for the entire path
    new_fibers = [Fiber(), Fiber()]

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]

        if not T.has_edge(u, v):
            print(f"Edge ({u}, {v}) does not exist in the graph. Skipping allocation.")
            continue  # Skip allocation if the edge does not exist

        if 'fibers' not in T.edges[u, v]:
            T.edges[u, v]['fibers'] = []

        # Add the two new fibers to the current edge
        T.edges[u, v]['fibers'].extend(new_fibers)

        # Use the newly created fibers for all allocations of this set of radio equipment
        fibers_to_use = new_fibers

        for fiber in fibers_to_use:
            for equipment in radio_equipment:
                required_capacity = equipment.calculate_required_capacity(term)
                for wavelength, current_capacity in fiber.wavelengths.items():
                    if current_capacity == 0:
                        fiber.wavelengths[wavelength] = required_capacity
                        break  # Exit the loop after occupying the capacity


def allocate_capacity_wdm_on_path_small(T, path, radio_equipment, term, with_mux=False):
    if with_mux:
        # If with_mux is True, call allocate_capacity_wdm_on_path_macro
        allocate_capacity_wdm_on_path_macro(T, path, radio_equipment, term)
        return

    if not path:
        return  # If the path is empty, do nothing

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]

        if not T.has_edge(u, v):
            print(f"Edge ({u}, {v}) does not exist in the graph. Skipping allocation.")
            continue  # Skip allocation if the edge does not exist

        if 'fibers' not in T.edges[u, v]:
            T.edges[u, v]['fibers'] = []

        # Add two new fibers for each radio equipment
        T.edges[u, v]['fibers'].append(Fiber())
        T.edges[u, v]['fibers'].append(Fiber())

        fibers_to_use = T.edges[u, v]['fibers'][-2:]  # Use the last two added fibers

        for fiber in fibers_to_use:
            allocated_wavelengths = 0
            for equipment in radio_equipment:
                required_capacity = equipment.calculate_required_capacity(term)
                for wavelength, current_capacity in fiber.wavelengths.items():
                    if current_capacity == 0:
                        fiber.wavelengths[wavelength] = required_capacity
                        allocated_wavelengths += 1
                        break  # Exit the loop after occupying the capacity
                if allocated_wavelengths >= len(radio_equipment):
                    break


def add_required_transponders(T, node):
    """
    Adds the required number of transponders to a node and to the root node,
    based on the number of WDM transceivers present in the node.
    """
    wdm_transceivers_count = sum(
        1 for eq in T.nodes[node]['network_equipment'] if 'WDM_TRANSCEIVERS' in eq.equipment_type.name
    )

    transponder_type = NetworkEquipmentTypeEnum.TRANSPONDER
    transponder_ports = network_equipment_types[transponder_type].num_ports

    # Calculate how many transponders are needed to cover all WDM transceivers
    num_transponders_needed = (wdm_transceivers_count + transponder_ports - 1) // transponder_ports

    # Add the required transponders to the node and the root node
    for _ in range(num_transponders_needed):
        transponder_instance = NetworkEquipment(transponder_type)

        # Add the transponder to the node
        T.nodes[node]['network_equipment'].append(transponder_instance)
        T.nodes[node]['other_consumption'] += network_equipment_types[transponder_type].max_power


def add_required_transponders_to_root(T, root_node):
    """
    Adds the required number of transponders to a node and to the root node,
    based on the number of WDM transceivers present in the node.
    """

    wdm_transceivers_count = sum(
        1 for eq in T.nodes[root_node]['network_equipment'] if 'WDM_TRANSCEIVERS' in eq.equipment_type.name
    )

    transponder_type = NetworkEquipmentTypeEnum.TRANSPONDER
    transponder_ports = network_equipment_types[transponder_type].num_ports

    # Calculate how many transponders are needed to cover all WDM transceivers
    num_transponders_needed = (wdm_transceivers_count + transponder_ports - 1) // transponder_ports

    # Add the required transponders to the node and the root node
    for _ in range(num_transponders_needed):
        transponder_instance = NetworkEquipment(transponder_type)

        # Add the transponder to the root
        T.nodes[root_node]['network_equipment'].append(transponder_instance)
        T.nodes[root_node]['other_consumption'] += network_equipment_types[transponder_type].max_power


def soluzione_2_with_smallcellmux(T, term):
    initialize_node_equipment(T)
    root_node = 0

    for node in T.nodes():
        if node == root_node:
            continue

        node_network_equipment = []
        root_network_equipment = []

        node_type = T.nodes[node]['type']

        if node_type == 1:  # Macro node
            for radio_eq in T.nodes[node]['radio_equipment']:
                required_capacity = radio_eq.calculate_required_capacity(term)

                # Add a pair of short SR transceivers with sufficient capacity
                if required_capacity <= 1:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_1G_LR
                elif required_capacity <= 10:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_10G_LR
                elif required_capacity <= 25:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_25G_LR
                elif required_capacity <= 50:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_50G_LR
                elif required_capacity <= 100:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_100G_LR
                else:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_400G_LR

                # Add grey and WDM transceivers to the node and the root
                # una coppia di SR e un WDM LR
                node_network_equipment.append(NetworkEquipment(transceiver_type))
                node_network_equipment.append(NetworkEquipment(transceiver_type))
                node_network_equipment.append(NetworkEquipment(wdm_transceiver_type))
                # una coppia di SR e un WDM LR
                root_network_equipment.append(NetworkEquipment(transceiver_type))
                root_network_equipment.append(NetworkEquipment(transceiver_type))
                root_network_equipment.append(NetworkEquipment(wdm_transceiver_type))

                # Update the `other_consumption` energy for the node and the root
                T.nodes[node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2
                T.nodes[node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power
                T.nodes[root_node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2
                T.nodes[root_node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power

            # Add a WDM multiplexer only if the number of radio equipments is greater than 0
            if len(T.nodes[node]['radio_equipment']) > 0:
                multiplexer_type = NetworkEquipmentTypeEnum.WDM_MUX
                node_network_equipment.append(NetworkEquipment(multiplexer_type))
                root_network_equipment.append(NetworkEquipment(multiplexer_type))

                # Update the `other_consumption` energy for the node and the root
                T.nodes[node]['other_consumption'] += network_equipment_types[multiplexer_type].max_power
                T.nodes[root_node]['other_consumption'] += network_equipment_types[multiplexer_type].max_power

        elif node_type == 2:  # Small node
            for radio_eq in T.nodes[node]['radio_equipment']:
                required_capacity = radio_eq.calculate_required_capacity(term)

                # Add a pair of short SR transceivers with sufficient capacity
                if required_capacity <= 1:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_1G_LR
                elif required_capacity <= 10:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_10G_LR
                elif required_capacity <= 25:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_25G_LR
                elif required_capacity <= 50:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_50G_LR
                elif required_capacity <= 100:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_100G_LR
                else:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR
                    wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_400G_LR

                # Add grey and WDM transceivers to the node and the root
                # una coppia di SR e un WDM LR
                node_network_equipment.append(NetworkEquipment(transceiver_type))
                node_network_equipment.append(NetworkEquipment(transceiver_type))
                node_network_equipment.append(NetworkEquipment(wdm_transceiver_type))
                # una coppia di SR e un WDM LR
                root_network_equipment.append(NetworkEquipment(transceiver_type))
                root_network_equipment.append(NetworkEquipment(transceiver_type))
                root_network_equipment.append(NetworkEquipment(wdm_transceiver_type))

                # Update the `other_consumption` energy for the node and the root
                T.nodes[node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2
                T.nodes[node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power
                T.nodes[root_node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2
                T.nodes[root_node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power

            # Add a WDM multiplexer only if the number of radio equipments is greater than 0
            if len(T.nodes[node]['radio_equipment']) > 0:
                multiplexer_type = NetworkEquipmentTypeEnum.WDM_MUX
                node_network_equipment.append(NetworkEquipment(multiplexer_type))
                root_network_equipment.append(NetworkEquipment(multiplexer_type))

                # Update the `other_consumption` energy for the node and the root
                T.nodes[node]['other_consumption'] += network_equipment_types[multiplexer_type].max_power
                T.nodes[root_node]['other_consumption'] += network_equipment_types[multiplexer_type].max_power

        T.nodes[node]['network_equipment'].extend(node_network_equipment)
        T.nodes[root_node]['network_equipment'].extend(root_network_equipment)

        # Add the required transponders based on the number of WDM transceivers
        add_required_transponders(T, node)

        # Allocate capacity along the path to the root node
        path = nx.shortest_path(T, source=node, target=root_node)

        if node_type == 1:  # Macro node
            allocate_capacity_wdm_on_path_macro(T, path, T.nodes[node]['radio_equipment'], term)
        elif node_type == 2:  # Small node
            allocate_capacity_wdm_on_path_small(T, path, T.nodes[node]['radio_equipment'], term, True)

    add_required_transponders_to_root(T, root_node)
    # Add the extra large switch at the root node
    add_switches_to_root(T, root_node)


def allocate_capacity_xr_on_path_macro(T, path, total_capacity):
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]

        if 'fibers' not in T.edges[u, v]:
            T.edges[u, v]['fibers'] = []

        # Create two new fibers for the entire path
        T.edges[u, v]['fibers'].append(Fiber())
        T.edges[u, v]['fibers'].append(Fiber())

        fibers_to_use = T.edges[u, v]['fibers'][-2:]  # Use the last two added fibers

        # Occupy one wavelength on each fiber
        for fiber in fibers_to_use:
            for wavelength, current_capacity in fiber.wavelengths.items():
                if current_capacity == 0:
                    fiber.wavelengths[wavelength] = total_capacity
                    break  # Exit the loop after occupying the capacity


def calculate_switch_energy(switch_type, total_traffic_gbps):
    """
    Calculate the energy consumption of a switch based on its type and the total traffic handled.

    :param switch_type: Switch type ("Small", "Medium", "Large", "Extra Large")
    :param total_traffic_gbps: Total traffic handled by the switch in Gbps
    :return: Energy consumption in Watts
    """
    # Energy consumption models based on switch type and traffic
    power_model = {
        "Small": [
            (0, 125), (20, 131), (40, 137), (60, 144), (80, 150), (100, 156), (120, 162), (140, 169), (160, 175),
            (180, 181), (200, 187), (220, 194), (240, 200), (260, 206), (280, 212), (300, 219), (320, 225),
            (340, 231), (360, 237), (380, 244), (400, 250)
        ],
        "Medium": [
            (0, 175), (80, 184), (160, 193), (240, 201), (320, 210), (400, 219), (480, 228), (560, 236), (640, 245),
            (720, 254), (800, 263), (880, 271), (960, 280), (1040, 289), (1120, 298), (1200, 306), (1280, 315),
            (1360, 324), (1440, 333), (1520, 341), (1600, 350)
        ],
        "Large": [
            (0, 230), (160, 242), (320, 253), (480, 265), (640, 276), (800, 288), (960, 299), (1120, 311),
            (1280, 322), (1440, 334), (1600, 345), (1760, 357), (1920, 368), (2080, 380), (2240, 391), (2400, 403),
            (2560, 414), (2720, 426), (2880, 437), (3040, 449), (3200, 460)
        ],
        "Extra Large": [
            (0, 310), (320, 326), (640, 341), (960, 357), (1280, 372), (1600, 388), (1920, 403), (2240, 419),
            (2560, 434), (2880, 450), (3200, 465), (3520, 481), (3840, 496), (4160, 512), (4480, 527), (4800, 543),
            (5120, 558), (5440, 574), (5760, 589), (6080, 605), (6400, 620)
        ]
    }

    if switch_type not in power_model:
        raise ValueError("Tipo di switch non valido. Scegli tra 'Small', 'Medium', 'Large', 'Extra Large'.")

    # Find the energy consumption corresponding to the total traffic
    model = power_model[switch_type]
    for i in range(len(model) - 1):
        (traffic_1, power_1), (traffic_2, power_2) = model[i], model[i + 1]
        if traffic_1 <= total_traffic_gbps <= traffic_2:
            # Linear interpolation between the two points
            return power_1 + (power_2 - power_1) * (total_traffic_gbps - traffic_1) / (traffic_2 - traffic_1)

    # If the total traffic exceeds the maximum value in the model, return the last consumption value
    return model[-1][1]


def allocate_capacity_xr_on_path_small(T, path, radio_equipment, term):
    if not path:
        return  # If the path is empty, do nothing

    for radio_eq in radio_equipment:
        required_capacity = radio_eq.calculate_required_capacity(term)

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]

            if 'fibers' not in T.edges[u, v]:
                T.edges[u, v]['fibers'] = []

            # Add two new fibers for each radio equipment
            T.edges[u, v]['fibers'].append(Fiber())
            T.edges[u, v]['fibers'].append(Fiber())

            fibers_to_use = T.edges[u, v]['fibers'][-2:]  # Use the last two added fibers

            # Occupy one wavelength on each fiber
            for fiber in fibers_to_use:
                for wavelength, current_capacity in fiber.wavelengths.items():
                    if current_capacity == 0:
                        fiber.wavelengths[wavelength] = required_capacity
                        break  # Exit the loop after occupying the capacity


def soluzione_2_with_smallcellaggr_with_preaggregation(T, term):
    """
    WDM-WP Solution: WDM with small cell aggregation and pre-aggregation
    This solution combines the WDM approach with pre-aggregation logic for all nodes
    """
    initialize_node_equipment(T)
    root_node = 0

    for node in T.nodes():
        if node == root_node:
            continue

        node_network_equipment = []
        root_network_equipment = []

        # Apply pre-aggregation logic to ALL nodes (both Macro and Small)

        # Create a set of radio equipment that require less than 25 Gbps of capacity
        preaggregable = [radio_eq for radio_eq in T.nodes[node]['radio_equipment'] if
                         radio_eq.calculate_required_capacity(term) < 25]

        # Find all combinations of radio equipment that can be pre-aggregated together
        from itertools import combinations
        preaggregated_radio_equipments = set()
        preaggregated_capacity = 0
        preaggregability = False

        for r in range(2, 6):
            # Find all combinations of length r
            combinations_list = list(combinations(preaggregable, r))

            for combination in combinations_list:
                combination_capacity = sum(radio_eq.calculate_required_capacity(term) for radio_eq in combination)
                if combination_capacity <= 25:
                    preaggregability = True
                    preaggregated_radio_equipments.update(combination)

        # Calculate the total capacity of the pre-aggregated radio equipment
        preaggregated_capacity = sum(
            radio_eq.calculate_required_capacity(term) for radio_eq in preaggregated_radio_equipments)

        # Convert to list
        preaggregated_radio_equipments = list(preaggregated_radio_equipments)

        # Separate the radio equipment that cannot be pre-aggregated
        other_radio_equipments = [radio_eq for radio_eq in T.nodes[node]['radio_equipment'] if
                                  radio_eq not in preaggregated_radio_equipments]

        if preaggregability:
            #print('SOME PREAGGREGABILITY IN WDM')
            # Add grey transceivers for the pre-aggregated radio equipment
            for radio_eq in preaggregated_radio_equipments:
                required_capacity = radio_eq.calculate_required_capacity(term)
                if required_capacity <= 1:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR
                elif required_capacity <= 10:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR
                elif required_capacity <= 25:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
                elif required_capacity <= 50:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
                elif required_capacity <= 100:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
                else:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR

                node_network_equipment.append(NetworkEquipment(transceiver_type))
                node_network_equipment.append(NetworkEquipment(transceiver_type))

                # Update energy consumption
                T.nodes[node]['other_consumption'] += 2 * network_equipment_types[transceiver_type].max_power

            # Add one WDM transceiver to cover the total pre-aggregated capacity
            if preaggregated_capacity <= 1:
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_1G_LR
            elif preaggregated_capacity <= 10:
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_10G_LR
            elif preaggregated_capacity <= 25:
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_25G_LR
            elif preaggregated_capacity <= 50:
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_50G_LR
            elif preaggregated_capacity <= 100:
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_100G_LR
            else:
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_400G_LR

            node_network_equipment.append(NetworkEquipment(wdm_transceiver_type))
            root_network_equipment.append(NetworkEquipment(wdm_transceiver_type))

            # Add corresponding SR transceivers at root for pre-aggregated capacity
            remaining_capacity = preaggregated_capacity
            while remaining_capacity > 0:
                if remaining_capacity <= 1:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR
                    remaining_capacity -= 1
                elif remaining_capacity <= 10:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR
                    remaining_capacity -= 10
                elif remaining_capacity <= 25:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
                    remaining_capacity -= 25
                elif remaining_capacity <= 50:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
                    remaining_capacity -= 50
                elif remaining_capacity <= 100:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
                    remaining_capacity -= 100
                else:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR
                    remaining_capacity -= 400

                root_network_equipment.append(NetworkEquipment(transceiver_type))
                root_network_equipment.append(NetworkEquipment(transceiver_type))
                T.nodes[root_node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2

            # Update energy consumption for WDM transceivers
            T.nodes[node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power
            T.nodes[root_node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power

            # Add a switch to support the total pre-aggregated capacity
            if preaggregated_capacity > 0:
                if preaggregated_capacity <= 400:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_SMALL
                elif preaggregated_capacity <= 1600:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_MEDIUM
                elif preaggregated_capacity <= 3200:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_BIG
                else:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_EXTRA_LARGE

                node_network_equipment.append(NetworkEquipment(switch_type))
                T.nodes[node]['switching_consumption'] += calculate_switch_power_consumption(switch_type,
                                                                                             preaggregated_capacity)

        # Handle remaining radio equipment that is not pre-aggregated (same as standard WDM)
        for radio_eq in other_radio_equipments:
            required_capacity = radio_eq.calculate_required_capacity(term)

            if required_capacity <= 1:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_1G_LR
            elif required_capacity <= 10:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_10G_LR
            elif required_capacity <= 25:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_25G_LR
            elif required_capacity <= 50:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_50G_LR
            elif required_capacity <= 100:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_100G_LR
            else:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR
                wdm_transceiver_type = NetworkEquipmentTypeEnum.WDM_TRANSCEIVERS_400G_LR

            # Add grey and WDM transceivers
            node_network_equipment.append(NetworkEquipment(transceiver_type))
            node_network_equipment.append(NetworkEquipment(transceiver_type))
            node_network_equipment.append(NetworkEquipment(wdm_transceiver_type))

            root_network_equipment.append(NetworkEquipment(transceiver_type))
            root_network_equipment.append(NetworkEquipment(transceiver_type))
            root_network_equipment.append(NetworkEquipment(wdm_transceiver_type))

            # Update energy consumption
            T.nodes[node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2
            T.nodes[node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power
            T.nodes[root_node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2
            T.nodes[root_node]['other_consumption'] += network_equipment_types[wdm_transceiver_type].max_power

        # Add WDM multiplexer only if there are radio equipments (considering both pre-aggregated and others)
        total_radio_equipments = len(T.nodes[node]['radio_equipment'])
        if total_radio_equipments > 0:
            multiplexer_type = NetworkEquipmentTypeEnum.WDM_MUX
            node_network_equipment.append(NetworkEquipment(multiplexer_type))
            root_network_equipment.append(NetworkEquipment(multiplexer_type))

            # Update energy consumption
            T.nodes[node]['other_consumption'] += network_equipment_types[multiplexer_type].max_power
            T.nodes[root_node]['other_consumption'] += network_equipment_types[multiplexer_type].max_power

        # Add equipment to nodes
        T.nodes[node]['network_equipment'].extend(node_network_equipment)
        T.nodes[root_node]['network_equipment'].extend(root_network_equipment)

        # Add required transponders
        add_required_transponders(T, node)

        # Allocate capacity along the path to the root node
        path = nx.shortest_path(T, source=node, target=root_node)
        allocate_capacity_wdm_on_path_macro(T, path, T.nodes[node]['radio_equipment'], term)

    # Add transponders to root and switches
    add_required_transponders_to_root(T, root_node)
    add_switches_to_root(T, root_node)

def soluzione_3_with_smallcellaggr(T, term):
    initialize_node_equipment(T)
    root_node = 0
    total_root_capacity = 0  # Total capacity that will be served by the root

    for node in T.nodes():
        if node == root_node:
            continue

        total_node_transceiver_capacity = 0
        node_network_equipment = []

        # Iterate over each radio equipment of the node
        for radio_eq in T.nodes[node]['radio_equipment']:
            required_capacity = radio_eq.calculate_required_capacity(term)

            # Add a pair of SR transceivers with sufficient capacity
            if required_capacity <= 25:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
            elif required_capacity <= 50:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
            elif required_capacity <= 100:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
            else:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR

            node_network_equipment.append(NetworkEquipment(transceiver_type))
            node_network_equipment.append(NetworkEquipment(transceiver_type))

            # Increase the capacity of the selected transceiver (data_rate)
            total_node_transceiver_capacity += network_equipment_types[transceiver_type].data_rate

            # Update the node's `other_consumption` energy usage
            T.nodes[node]['other_consumption'] += 2 * network_equipment_types[transceiver_type].max_power

        # Add media converters and related XR modules needed to serve the node's total capacity
        remaining_capacity = total_node_transceiver_capacity
        media_converter_capacity = 0

        while remaining_capacity > 0:
            if remaining_capacity <= 25:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_25G
                remaining_capacity -= 25
                media_converter_capacity += 25
            elif remaining_capacity <= 50:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_50G
                remaining_capacity -= 50
                media_converter_capacity += 50
            elif remaining_capacity <= 100:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_100G
                remaining_capacity -= 100
                media_converter_capacity += 100
            elif remaining_capacity <= 200:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_200G_8X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_200G
                remaining_capacity -= 200
                media_converter_capacity += 200
            elif remaining_capacity <= 400:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_400G
                remaining_capacity -= 400
                media_converter_capacity += 400
            else:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_400G
                remaining_capacity -= 400
                media_converter_capacity += 400

            node_network_equipment.append(NetworkEquipment(media_converter_type))
            node_network_equipment.append(NetworkEquipment(xr_module_type))

            # Update the node's `other_consumption` energy usage
            T.nodes[node]['other_consumption'] += (network_equipment_types[media_converter_type].max_power +
                                                   network_equipment_types[xr_module_type].max_power)

        total_node_capacity = media_converter_capacity
        T.nodes[node]['network_equipment'].extend(node_network_equipment)
        total_root_capacity += total_node_capacity

        # Allocate capacity along the path to the root node
        path = nx.shortest_path(T, source=node, target=root_node)
        allocate_capacity_xr_on_path_macro(T, path, total_node_capacity)

    # Add XR modules at the root node to serve the total capacity of all media converters
    remaining_root_capacity = total_root_capacity

    while remaining_root_capacity > 0:
        if remaining_root_capacity <= 25:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G
            remaining_root_capacity -= 25
        elif remaining_root_capacity <= 50:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G
            remaining_root_capacity -= 50
        elif remaining_root_capacity <= 100:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G
            remaining_root_capacity -= 100
        elif remaining_root_capacity <= 200:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_200G
            remaining_root_capacity -= 200
        else:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_400G
            remaining_root_capacity -= 400

        T.nodes[root_node]['network_equipment'].append(NetworkEquipment(xr_module_type))

        # Update the root node's `other_consumption` energy usage
        T.nodes[root_node]['other_consumption'] += network_equipment_types[xr_module_type].max_power

    # Add the extra large switch at the root node and update the energy consumption
    add_switches_to_root(T, root_node)


from itertools import combinations


def soluzione_3_with_smallcellaggr_with_preaggregation(T, term):
    initialize_node_equipment(T)
    root_node = 0
    total_root_capacity = 0  # Total capacity that will be served by the root

    for node in T.nodes():
        if node == root_node:
            continue

        total_node_transceiver_capacity = 0
        node_network_equipment = []

        # Create a set of radio equipment that require less than 25 Gbps of capacity
        preaggregable = [radio_eq for radio_eq in T.nodes[node]['radio_equipment'] if
                         radio_eq.calculate_required_capacity(term) < 25]

        # Find all combinations of radio equipment that can be pre-aggregated together
        preaggregated_radio_equipments = set()
        preaggregated_capacity = 0
        preaggregability = False  # Initially set preaggregability to False

        for r in range(2, 6):
            # Find all combinations of length r
            combinations_list = list(combinations(preaggregable, r))

            for combination in combinations_list:
                combination_capacity = sum(radio_eq.calculate_required_capacity(term) for radio_eq in combination)
                if combination_capacity <= 25:
                    # Set preaggregability to True if at least one combination is valid
                    preaggregability = True
                    # Add each radio equipment of the valid combination to the list of pre-aggregated equipment
                    preaggregated_radio_equipments.update(combination)

        # Calculate the total capacity of the pre-aggregated radio equipment
        preaggregated_capacity = sum(
            radio_eq.calculate_required_capacity(term) for radio_eq in preaggregated_radio_equipments)

        # Convert it into a list (optional, if needed)
        preaggregated_radio_equipments = list(preaggregated_radio_equipments)

        # Separate the radio equipment that cannot be pre-aggregated
        other_radio_equipments = [radio_eq for radio_eq in T.nodes[node]['radio_equipment'] if
                                  radio_eq not in preaggregated_radio_equipments]

        if preaggregability:
            #print('SOME PREAGGREGABILITY IN P2MP')
            # Add grey transceivers for the pre-aggregated radio equipment
            for radio_eq in preaggregated_radio_equipments:
                required_capacity = radio_eq.calculate_required_capacity(term)
                if required_capacity <= 1:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR
                elif required_capacity <= 10:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR
                elif required_capacity <= 25:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
                elif required_capacity <= 50:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
                elif required_capacity <= 100:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
                else:
                    transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR

                node_network_equipment.append(NetworkEquipment(transceiver_type))
                node_network_equipment.append(NetworkEquipment(transceiver_type))

                # Update the node's `other_consumption` energy usage
                T.nodes[node]['other_consumption'] += 2 * network_equipment_types[transceiver_type].max_power

            # Add grey transceivers to cover the total pre-aggregated capacity
            remaining_capacity = preaggregated_capacity
            while remaining_capacity > 0:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
                remaining_capacity -= 25
                node_network_equipment.append(NetworkEquipment(transceiver_type))
                node_network_equipment.append(NetworkEquipment(transceiver_type))
                total_node_transceiver_capacity += network_equipment_types[transceiver_type].data_rate

                # Update the node's `other_consumption` energy usage
                T.nodes[node]['other_consumption'] += network_equipment_types[transceiver_type].max_power * 2

            # Add a switch to support the total pre-aggregated capacity
            if preaggregated_capacity > 0:
                if preaggregated_capacity <= 400:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_SMALL
                elif preaggregated_capacity <= 1600:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_MEDIUM
                elif preaggregated_capacity <= 3200:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_BIG
                else:
                    switch_type = NetworkEquipmentTypeEnum.SWITCH_EXTRA_LARGE

                node_network_equipment.append(NetworkEquipment(switch_type))

                # Update the node's `switching_consumption` energy usage
                T.nodes[node]['switching_consumption'] += calculate_switch_power_consumption(switch_type,
                                                                                             preaggregated_capacity)

        # Iterate over the remaining radio equipment that is not pre-aggregated
        for radio_eq in other_radio_equipments:
            required_capacity = radio_eq.calculate_required_capacity(term)

            # Add a pair of SR transceivers with sufficient capacity
            if required_capacity <= 25:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR
            elif required_capacity <= 50:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR
            elif required_capacity <= 100:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR
            else:
                transceiver_type = NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR

            node_network_equipment.append(NetworkEquipment(transceiver_type))
            node_network_equipment.append(NetworkEquipment(transceiver_type))
            # Increase the capacity of the selected transceiver (data_rate)
            total_node_transceiver_capacity += network_equipment_types[transceiver_type].data_rate

            # Update the node's `other_consumption` energy usage
            T.nodes[node]['other_consumption'] += 2 * network_equipment_types[transceiver_type].max_power

        # Add media converters and related XR modules needed to serve the node's total capacity
        remaining_capacity = total_node_transceiver_capacity
        media_converter_capacity = 0
        while remaining_capacity > 0:
            if remaining_capacity <= 25:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_25G
                remaining_capacity -= 25
                media_converter_capacity += 25
            elif remaining_capacity <= 50:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_50G
                remaining_capacity -= 50
                media_converter_capacity += 50
            elif remaining_capacity <= 100:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_100G
                remaining_capacity -= 100
                media_converter_capacity += 100
            elif remaining_capacity <= 200:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_200G_8X25G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_200G
                remaining_capacity -= 200
                media_converter_capacity += 200
            elif remaining_capacity <= 400:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_400G
                remaining_capacity -= 400
                media_converter_capacity += 400
            else:
                media_converter_type = NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G
                xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_400G
                remaining_capacity -= 400
                media_converter_capacity += 400

            node_network_equipment.append(NetworkEquipment(media_converter_type))
            node_network_equipment.append(NetworkEquipment(xr_module_type))

            # Update the node's `other_consumption` energy usage
            T.nodes[node]['other_consumption'] += (network_equipment_types[media_converter_type].max_power +
                                                   network_equipment_types[xr_module_type].max_power)

        total_node_capacity = media_converter_capacity
        T.nodes[node]['network_equipment'].extend(node_network_equipment)
        total_root_capacity += total_node_capacity

        # Allocate capacity along the path to the root node
        path = nx.shortest_path(T, source=node, target=root_node)
        allocate_capacity_xr_on_path_macro(T, path, total_node_capacity)

    # Add XR modules at the root node to serve the total capacity of all media converters
    remaining_root_capacity = total_root_capacity
    while remaining_root_capacity > 0:
        if remaining_root_capacity <= 25:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G
            remaining_root_capacity -= 25
        elif remaining_root_capacity <= 50:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G
            remaining_root_capacity -= 50
        elif remaining_root_capacity <= 100:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G
            remaining_root_capacity -= 100
        elif remaining_root_capacity <= 200:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_200G
            remaining_root_capacity -= 200
        else:
            xr_module_type = NetworkEquipmentTypeEnum.XR_MODULE_HUB_400G
            remaining_root_capacity -= 400

        T.nodes[root_node]['network_equipment'].append(NetworkEquipment(xr_module_type))

        # Update the root node's `other_consumption` energy usage
        T.nodes[root_node]['other_consumption'] += network_equipment_types[xr_module_type].max_power

    # Add the extra large switch at the root node
    add_switches_to_root(T, root_node)


def print_radio_equipment_info(T, node, term):
    node_type = T.nodes[node]['type']
    node_type_str = "Macro" if node_type == 1 else "Small" if node_type == 2 else "Unknown"
    total_capacity = 0
    print(
        f"Node {node} (ID: {T.nodes[node]['id']}, Type: {node_type_str}) Radio Equipment and Total Required Capacity:")
    for eq in T.nodes[node]['radio_equipment']:
        required_capacity = eq.calculate_required_capacity(term)
        total_capacity += required_capacity
        print(
            f"- Equipment Type: {eq.equipment_type.value}, Deployment: {eq.deployment}, Required Capacity: {required_capacity} Gbps")
    print(f"Total Required Capacity for node {node} ({term} term): {total_capacity} Gbps")


def print_network_equipment_info(T, node):
    print(f"Node {node} (Type: {T.nodes[node]['type']}) Network Equipment:")
    for ne in T.nodes[node]['network_equipment']:
        print(f"- Equipment Type: {ne.equipment_type.value}")
        print(f"  Data Rate: {ne.data_rate} Gbps")
        print(f"  Price: {ne.price} €")
        print(f"  Normalized Price: {ne.normalized_price}")
        # print(f"  Max Power: {ne.max_power} W")
        # print(f"  Typical FF: {ne.typical_ff}")
        # print(f"  Insertion Loss: {ne.insertion_loss}")
        # print(f"  Size: {ne.size}")
        # print(f"  Note: {ne.note}")


def draw_simple_graph(T):
    pos = {node: T.nodes[node]['position'] for node in T.nodes()}
    types = [T.nodes[node]['type'] for node in T.nodes()]
    labels = {node: node for node in T.nodes()}  # Add labels for the nodes

    plt.figure()
    nx.draw(T, pos, with_labels=True, labels=labels, node_size=100, node_color=types, cmap=plt.cm.rainbow,
            edge_color='gray')
    plt.title('Simple Graph')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')
    plt.grid(True)
    plt.show(block=False)


def draw_graph_by_fiber_occupation(T):
    pos = {node: T.nodes[node]['position'] for node in T.nodes()}
    types = [T.nodes[node]['type'] for node in T.nodes()]
    labels = {node: node for node in T.nodes()}  # Add labels for the nodes

    edges = T.edges()
    widths = []
    for u, v in edges:
        if 'fibers' in T.edges[u, v]:
            width = sum(
                1 for fiber in T.edges[u, v]['fibers'] for capacity in fiber.wavelengths.values() if capacity > 0)
            widths.append(width / 100)
        else:
            widths.append(1)

    plt.figure()
    nx.draw(T, pos, with_labels=True, labels=labels, node_size=100, node_color=types, cmap=plt.cm.rainbow,
            edge_color='gray', width=widths)
    plt.title('Graph with Edge Width Based on Fiber Occupation')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')
    plt.grid(True)
    plt.show(block=False)


def draw_graph_by_capacity_occupation(T):
    pos = {node: T.nodes[node]['position'] for node in T.nodes()}
    types = [T.nodes[node]['type'] for node in T.nodes()]
    labels = {node: node for node in T.nodes()}  # Add labels for the nodes

    edges = T.edges()
    widths = []
    for u, v in edges:
        if 'fibers' in T.edges[u, v]:
            width = sum(
                fiber.wavelengths[wavelength] for fiber in T.edges[u, v]['fibers'] for wavelength in fiber.wavelengths
                if fiber.wavelengths[wavelength] > 0)
            widths.append(width / 1000)  # Normalize the width to make it visible
        else:
            widths.append(1)

    plt.figure()
    nx.draw(T, pos, with_labels=True, labels=labels, node_size=100, node_color=types, cmap=plt.cm.rainbow,
            edge_color='gray', width=widths)
    plt.title('Graph with Edge Width Based on Capacity Occupation')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')
    plt.grid(True)
    plt.show(block=False)


def print_occupied_fibers(T):
    print("Number of occupied fibers in each link:")
    for u, v in T.edges():
        if 'fibers' in T.edges[u, v]:
            occupied_fibers = sum(
                any(capacity > 0 for capacity in fiber.wavelengths.values()) for fiber in T.edges[u, v]['fibers']
            )
            print(f"Link ({u}, {v}): {occupied_fibers} fibers occupied")
        else:
            print(f"Link ({u}, {v}): 0 fibers occupied")


def save_graph(T, filename):
    # Convert numpy arrays to strings for GraphML compatibility
    for node in T.nodes():
        T.nodes[node]['position'] = ','.join(map(str, T.nodes[node]['position']))
    # Save the graph in GraphML format
    nx.write_graphml(T, filename)


def load_graph(filename):
    T = nx.read_graphml(filename)
    # Convert position strings back to lists
    for node in T.nodes():
        T.nodes[node]['position'] = list(map(float, T.nodes[node]['position'].split(',')))
    # Ensure node IDs are integers
    T = nx.relabel_nodes(T, {str(i): i for i in range(len(T.nodes()))})
    return T


# Function to calculate the total cost of network equipment in a graph
def calculate_total_cost(T):
    transceiver_cost = calculate_cost_component(T,
                                                ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "TRANSPONDER", "MEDIA_CONVERTER"])
    switching_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" ,  "SWITCH_EXTRA_LARGE", "WDM_MUX"])
    total_cost = transceiver_cost + switching_cost
    return total_cost
    '''
    total_normalized_cost = 0
    for node in T.nodes():
        for ne in T.nodes[node].get('network_equipment', []):
            total_normalized_cost += ne.normalized_price

    return total_normalized_cost
    '''


def count_fibers(T):
    fiber_count = {}
    for u, v in T.edges():
        if 'fibers' in T.edges[u, v]:
            fiber_count[(u, v)] = len(T.edges[u, v]['fibers'])
        else:
            fiber_count[(u, v)] = 0
    return fiber_count


##PLOT

temporal_scenarios = ['Medium', 'Long']
deployment_scenarios = ["Dense Urban", "Urban", "Suburban", "Rural"]

# List to store the costs for all solutions
results_list = []


# Function to run tests for a specific solution
# Function to run tests for a specific solution with normalized cost calculation
def run_tests_for_solution(soluzione_fn, name, results_list):
    for term in temporal_scenarios:
        for scenario in deployment_scenarios:
            # Carica il grafo
            T, T_m, A = create_geotype(scenario)
            # Deploy radio equipment
            deploy_radio_equipment(T, term, scenario)
            # Deploy network infrastructure based on the solution function
            soluzione_fn(T, term)
            # Calculate the total cost
            total_cost = calculate_total_cost(T)
            # Calculate the cost normalized by area
            normalized_cost = total_cost / A
            # Add the results to the list
            results_list.append({'Soluzione': name, 'Temporal Scenario': term, 'Deployment Scenario': scenario,
                                 'Total Cost': total_cost, 'Normalized Cost': normalized_cost})



print("RUNNING TESTS")
# Run tests for all solutions including the new WDM-WP
results_list = []
run_tests_for_solution(soluzione_1_with_smallcellswitch, 'P2P with', results_list)
print("RUNNED TEST SOL 1")

run_tests_for_solution(soluzione_2_with_smallcellmux, 'WDM with', results_list)
print("RUNNED TEST SOL 2")

# Aggiungi la nuova soluzione WDM-WP
run_tests_for_solution(soluzione_2_with_smallcellaggr_with_preaggregation, 'WDM-WP with', results_list)
print("RUNNED TEST SOL 2-WP")

run_tests_for_solution(soluzione_3_with_smallcellaggr, 'P2MP with', results_list)
print("RUNNED TEST SOL 3")

run_tests_for_solution(soluzione_3_with_smallcellaggr_with_preaggregation, 'P2MP-WP with', results_list)
print("RUNNED TEST SOL 3-WP")
print("RUNNED TESTS")

# Update solution names
results_df = pd.DataFrame(results_list)
results_df['Soluzione'] = results_df['Soluzione'].replace({
    'P2P with': 'P2P with',
    'WDM with': 'WDM with',
    'WDM-WP with': 'WDM-WP with',  # Nuova soluzione
    'P2MP with': 'P2MP with',
    'P2MP-WP with': 'P2MP-WP with'
})


# Determine the maximum y-axis value for total cost
y_max_total = results_df['Total Cost'].max() * 1.1  # Add a 10% margin

# Determine the maximum y-axis value for normalized cost
y_max_normalized = results_df['Normalized Cost'].max() * 1.1  # Add a 10% margin
'''
# Create total cost plots for each deployment scenario ("wo" versions)
for scenario in deployment_scenarios:
    plt.figure(figsize=(14, 8))
    sns.barplot(data=results_df[(results_df['Deployment Scenario'] == scenario) &
                                results_df['Soluzione'].str.contains('wo')],
                x='Soluzione', y='Total Cost', hue='Temporal Scenario', errorbar=None, palette='pastel')
    plt.ylim(0, y_max_total)  # Set the maximum y-axis value
    plt.xlabel('Solutions')
    plt.ylabel('Total Cost (Cost Units)')
    plt.title(f'Total Cost for {scenario} Scenario without Aggregation at the Small Cell')
    plt.legend(title='Temporal Scenario')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.show(block=False)
'''
# Create total cost plots for each deployment scenario ("with" versions)
for scenario in deployment_scenarios:
    plt.figure(figsize=(14, 8))
    sns.barplot(data=results_df[(results_df['Deployment Scenario'] == scenario) &
                                results_df['Soluzione'].str.contains('with')],
                x='Soluzione', y='Total Cost', hue='Temporal Scenario', errorbar=None, palette='pastel')
    plt.ylim(0, y_max_total)  # Set the maximum y-axis value
    plt.xlabel('Solutions')
    plt.ylabel('Total Cost (Cost Units)')
    plt.title(f'Total Cost for {scenario} Scenario with Aggregation at the Small Cell')
    plt.legend(title='Temporal Scenario')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.show(block=False)

# Area data for the four deployment scenarios
deployment_scenarios = ["Dense Urban", "Urban", "Suburban", "Rural"]
areas = [0.8 * 0.8, 1.6 * 1.6, 3.2 * 3.2, 12.8 * 12.8]

# Create the area plot
plt.figure(figsize=(10, 6))
plt.bar(deployment_scenarios, areas, color='lightblue')
plt.xlabel('Deployment Scenario')
plt.ylabel('Area (km²)')
plt.title('Area for Each Deployment Scenario')
plt.grid(True)
plt.show(block=False)
'''
# Create normalized cost plots for each deployment scenario with logarithmic y-axis ("wo" versions)
for scenario in deployment_scenarios:
    plt.figure(figsize=(14, 8))
    sns.barplot(data=results_df[(results_df['Deployment Scenario'] == scenario) &
                                results_df['Soluzione'].str.contains('wo')],
                x='Soluzione', y='Normalized Cost', hue='Temporal Scenario', errorbar=None, palette='pastel')

    #plt.yscale('log')  # Set the y-axis to a logarithmic scale
    plt.ylim(1, y_max_normalized)  # Set the max and min y-axis values to avoid log issues
    plt.xlabel('Solutions')
    plt.ylabel('Normalized Cost (Cost Units per km²)')
    plt.title(f'Normalized Cost for {scenario} Scenario without Aggregation at the Small Cell')
    plt.legend(title='Temporal Scenario')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.show(block=False)
'''
# Create normalized cost plots for each deployment scenario with logarithmic y-axis ("with" versions)
for scenario in deployment_scenarios:
    plt.figure(figsize=(14, 8))
    sns.barplot(data=results_df[(results_df['Deployment Scenario'] == scenario) &
                                results_df['Soluzione'].str.contains('with')],
                x='Soluzione', y='Normalized Cost', hue='Temporal Scenario', errorbar=None, palette='pastel')

    # plt.yscale('log')  # Set the y-axis to a logarithmic scale
    plt.ylim(1, y_max_normalized)  # Set the max and min y-axis values to avoid log issues
    plt.xlabel('Solutions')
    plt.ylabel('Normalized Cost (Cost Units per km²)')
    plt.title(f'Normalized Cost for {scenario} Scenario with Aggregation at the Small Cell')
    plt.legend(title='Temporal Scenario')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.show(block=False)

## COST EFFICIENCY
import seaborn as sns
import matplotlib.pyplot as plt

# List to store the cost efficiency results
cost_efficiency_results = []


# Function to calculate cost efficiency
def calculate_cost_efficiency(T, total_cost, term):
    total_required_capacity = sum([radio_eq.calculate_required_capacity(term) for node in T.nodes() for radio_eq in
                                   T.nodes[node]['radio_equipment']])  # DS and US
    print('Total required capacity: ', total_required_capacity)
    print('Total cost: ', total_cost)
    if total_required_capacity > 0:
        return total_cost / total_required_capacity
    else:
        return float('inf')  # Avoid division by zero


# Run tests for the "wo" solutions and calculate the cost efficiency
for term in temporal_scenarios:
    for scenario in deployment_scenarios:
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)

        # Includi la nuova soluzione nei test
        for soluzione_fn, name in [(soluzione_1_with_smallcellswitch, 'P2P'),
                                   (soluzione_2_with_smallcellmux, 'WDM'),
                                   (soluzione_2_with_smallcellaggr_with_preaggregation, 'WDM-WP'),  # Nuova!
                                   (soluzione_3_with_smallcellaggr, 'P2MP'),
                                   (soluzione_3_with_smallcellaggr_with_preaggregation, 'P2MP-WP')]:
            soluzione_fn(T, term)
            total_cost = calculate_total_cost(T)
            cost_efficiency = calculate_cost_efficiency(T, total_cost, term)

            cost_efficiency_results.append({
                'Soluzione': name,
                'Temporal Scenario': term,
                'Deployment Scenario': scenario,
                'Cost Efficiency': cost_efficiency
            })

# Convert the list into a DataFrame
cost_efficiency_df = pd.DataFrame(cost_efficiency_results)

# Determine the maximum y-axis value to set the scale
y_max_efficiency = cost_efficiency_df['Cost Efficiency'].max() * 1.1  # Add a 10% margin
'''
# Create cost efficiency plots for each deployment scenario
for scenario in deployment_scenarios:
    plt.figure(figsize=(14, 8))
    sns.barplot(data=cost_efficiency_df[(cost_efficiency_df['Deployment Scenario'] == scenario)],
                x='Soluzione', y='Cost Efficiency', hue='Temporal Scenario', errorbar=None, palette='pastel')
    plt.ylim(0, y_max_efficiency)  # Set the maximum y-axis value
    plt.xlabel('Solutions')
    plt.ylabel('Cost Efficiency (Cost Units per FH Capacity Unit)')
    plt.title(f'Cost Efficiency for {scenario} Scenario with Small Cell Aggregation')
    plt.legend(title='Temporal Scenario')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.show(block=False)
'''


## NETWORK EFFICIENCY

def calculate_network_efficiency(T, term):
    total_required_capacity = sum([radio_eq.calculate_required_capacity(term) for node in T.nodes() for radio_eq in
                                   T.nodes[node]['radio_equipment']])  # DS and US

    # Calculate the sum of the capacity of all SR, LR, and XR transceivers
    total_deployed_capacity = 0
    for node in T.nodes():
        for equipment in T.nodes[node]['network_equipment']:
            if equipment.equipment_type in [
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_SR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_SR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_SR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_SR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_SR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_SR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_1G_LR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_10G_LR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_LR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_LR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR,
                NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_LR,
                NetworkEquipmentTypeEnum.XR_MODULE_25G,
                NetworkEquipmentTypeEnum.XR_MODULE_50G,
                NetworkEquipmentTypeEnum.XR_MODULE_100G,
                NetworkEquipmentTypeEnum.XR_MODULE_200G,
                NetworkEquipmentTypeEnum.XR_MODULE_400G,
            ]:
                total_deployed_capacity += equipment.data_rate

    if total_deployed_capacity > 0:
        return total_required_capacity / total_deployed_capacity
    else:
        return float('inf')  # Avoid division by zero


# List to store network efficiency results
network_efficiency_results = []

# Run network efficiency tests for each "with" solution
for soluzione_fn, name in [
    (soluzione_1_with_smallcellswitch, 'P2P'),
    (soluzione_2_with_smallcellmux, 'WDM'),
    (soluzione_2_with_smallcellaggr_with_preaggregation, 'WDM-WP'),  # Nuova!
    (soluzione_3_with_smallcellaggr, 'P2MP'),
    (soluzione_3_with_smallcellaggr_with_preaggregation, 'P2MP-WP')
]:
    for term in temporal_scenarios:
        for scenario in deployment_scenarios:
            T, T_m, A = create_geotype(scenario)
            deploy_radio_equipment(T, term, scenario)
            soluzione_fn(T, term)
            network_efficiency = calculate_network_efficiency(T, term)

            network_efficiency_results.append({
                'Soluzione': name,
                'Temporal Scenario': term,
                'Deployment Scenario': scenario,
                'Network Efficiency': network_efficiency
            })

# Convert the list into a DataFrame
network_efficiency_df = pd.DataFrame(network_efficiency_results)

# Create network efficiency plots for each deployment scenario
for scenario in deployment_scenarios:
    plt.figure(figsize=(14, 8))
    sns.barplot(data=network_efficiency_df[
        (network_efficiency_df['Deployment Scenario'] == scenario) &
        network_efficiency_df['Soluzione'].isin(['P2P', 'WDM', 'P2MP', 'P2MP-WP'])],
                x='Soluzione', y='Network Efficiency', hue='Temporal Scenario', errorbar=None, palette='pastel')

    plt.ylim(0, 1)  # Network efficiency is a ratio, so it should normally be between 0 and 1
    plt.xlabel('Solutions')
    plt.ylabel('Network TX Efficiency (Total Required FH Capacity / Deployed Capacity)')
    plt.title(f'Network TX Efficiency for {scenario} Scenario with Small Cell Aggregation')
    plt.legend(title='Temporal Scenario')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.show(block=False)


##FIBER UTILIZATION

def calculate_fiber_utilization(T, term):
    # Calculate the total required capacity
    total_required_capacity = sum([radio_eq.calculate_required_capacity(term) for node in T.nodes() for radio_eq in
                                   T.nodes[node]['radio_equipment']])

    # Count the total number of fibers in the graph
    total_fibers = sum([len(T.edges[u, v]['fibers']) for u, v in T.edges() if 'fibers' in T.edges[u, v]])

    if total_fibers > 0:
        return total_required_capacity / total_fibers
    else:
        return float('inf')  # Avoid division by zero


# List to store the results of fiber utilization
results_fiber_utilization = []

# Calculate fiber utilization for every combination of scenario and solution
for name, soluzione_fn in [('P2P', soluzione_1_with_smallcellswitch),
                           ('WDM', soluzione_2_with_smallcellmux),
                           ('WDM-WP', soluzione_2_with_smallcellaggr_with_preaggregation),  # Nuova!
                           ('P2MP', soluzione_3_with_smallcellaggr),
                           ('P2MP-WP', soluzione_3_with_smallcellaggr_with_preaggregation)]:
    for term in temporal_scenarios:
        for scenario in deployment_scenarios:
            T, T_m, A = create_geotype(scenario)
            deploy_radio_equipment(T, term, scenario)
            soluzione_fn(T, term)
            fiber_utilization = calculate_fiber_utilization(T, term)

            results_fiber_utilization.append({
                'Soluzione': name,
                'Temporal Scenario': term,
                'Deployment Scenario': scenario,
                'Fiber Utilization': fiber_utilization
            })

# Convert the results into a DataFrame
results_fiber_df = pd.DataFrame(results_fiber_utilization)
'''
# Create fiber utilization plots for each deployment scenario
for scenario in deployment_scenarios:
    plt.figure(figsize=(14, 8))
    sns.barplot(data=results_fiber_df[
        (results_fiber_df['Deployment Scenario'] == scenario)],
                x='Soluzione', y='Fiber Utilization', hue='Temporal Scenario', errorbar=None, palette='pastel')

    plt.ylim(0, results_fiber_df['Fiber Utilization'].max() * 1.1)  # Set the maximum y-axis value
    plt.xlabel('Solutions')
    plt.ylabel('Fiber Utilization (Gbps per Fiber)')
    plt.title(f'Fiber Utilization for {scenario} Scenario (with Aggregation at the Small Cell)')
    plt.legend(title='Temporal Scenario')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.show(block=False)
'''

#################### REPORTING
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_topology():
    img_path = "dense_urban_topology.png"  # Path of the saved image
    return img_path


def generate_stacked_cost_plot(T, term, scenario, output_path):
    solutions = ['P2P', 'WDM', 'P2MP', 'P2MP-WP']
    cost_data = []

    for solution in solutions:
        T, _, _ = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)

        if solution == 'P2P':
            soluzione_1_with_smallcellswitch(T, term)
        elif solution == 'WDM':
            soluzione_2_with_smallcellmux(T, term)
        elif solution == 'P2MP':
            soluzione_3_with_smallcellaggr(T, term)
        elif solution == 'P2MP-WP':
            soluzione_3_with_smallcellaggr_with_preaggregation(T, term)

        transceiver_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        switching_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE", "WDM_MUX"])
        total_cost = transceiver_cost + switching_cost

        cost_data.append({
            'Solution': solution,
            'Transceivers Cost': transceiver_cost,
            'Switching Cost': switching_cost,
            'Total Cost': total_cost
        })

    df = pd.DataFrame(cost_data)

    # Stacked plot
    df.set_index('Solution')[['Transceivers Cost', 'Switching Cost']].plot(kind='bar', stacked=True)
    plt.title(f"Cost Breakdown for {term.capitalize()} Term - {scenario}")
    plt.ylabel('Cost (Cost Units)')
    plt.xlabel('Solution')
    plt.xticks(rotation=0)
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


def get_node_radio_equipment_info(T, node, term):
    node_type = T.nodes[node]['type']
    node_type_str = "Macro" if node_type == 1 else "Small" if node_type == 2 else "Unknown"
    details = []
    total_capacity = 0

    for eq in T.nodes[node]['radio_equipment']:
        required_capacity = eq.calculate_required_capacity(term)
        total_capacity += required_capacity
        details.append([
            eq.equipment_type.value,
            eq.deployment,
            f"{required_capacity} Gbps"
        ])
    details.append(["Total Capacity", "", f"{total_capacity} Gbps"])

    return node_type_str, details


import io
from contextlib import redirect_stdout
from collections import Counter

from collections import Counter
from collections import Counter

from collections import Counter


def get_printed_equipment_info(T, node, term):
    network_equipments = T.nodes[node]['network_equipment']

    # Count the number of each equipment type
    equipment_counter = Counter(eq.equipment_type.name for eq in network_equipments)

    # Create the grouped output
    f = io.StringIO()
    with redirect_stdout(f):
        print(f"Node {node} Network Equipment (Count by Type):")
        for eq_type, count in equipment_counter.items():
            print(f"{eq_type}: {count} unit(s)")
        print()  # Adds an empty line to separate sections

        # Print details for individual equipment
        for eq_type in equipment_counter.keys():
            eq_sample = next(eq for eq in network_equipments if eq.equipment_type.name == eq_type)
            if 'TRANSCEIVERS' in eq_sample.equipment_type.name or 'XR_MODULE' in eq_sample.equipment_type.name:
                print(f"Details for {eq_type}:")
                print(f"- Cost: {network_equipment_types[eq_sample.equipment_type].normalized_price} CUs")
                print(f"- Data Rate: {network_equipment_types[eq_sample.equipment_type].data_rate} Gbps")
            else:
                print(f"Details for {eq_type}:")
                print(f"- Cost: {network_equipment_types[eq_sample.equipment_type].normalized_price} CUs")
                print(f"- Capacity: {network_equipment_types[eq_sample.equipment_type].capacity} Gbps")
            print()

        # Information on radio equipment
        radio_equipments = T.nodes[node]['radio_equipment']
        radio_equipment_counter = Counter(eq.equipment_type.value for eq in radio_equipments)

        print(f"Node {node} Radio Equipment and Total Required Capacity ({term} term):")
        total_capacity = 0
        for eq_type, count in radio_equipment_counter.items():
            eq_sample = next(eq for eq in radio_equipments if eq.equipment_type.value == eq_type)
            required_capacity = eq_sample.calculate_required_capacity(term)
            total_capacity += required_capacity * count
            print(f"{eq_type}: {count} unit(s) - Required Capacity per unit: {required_capacity} Gbps")

        print(f"Total Required Capacity for node {node} ({term} term): {total_capacity} Gbps")

    equipment_info_output = f.getvalue()
    return Paragraph(equipment_info_output.replace('\n', '<br/>'), getSampleStyleSheet()['Normal'])


def get_topology_details(T):
    root_count = sum(1 for n in T.nodes if T.nodes[n]['type'] == 0)
    macro_count = sum(1 for n in T.nodes if T.nodes[n]['type'] == 1)
    small_count = sum(1 for n in T.nodes if T.nodes[n]['type'] == 2)

    return root_count, macro_count, small_count


def find_first_node_of_each_type(T):
    root_node = None
    macro_node = None
    small_node = None

    for node in T.nodes:
        node_type = T.nodes[node]['type']
        if node_type == 0 and root_node is None:
            root_node = node
        elif node_type == 1 and macro_node is None:
            macro_node = node
        elif node_type == 2 and small_node is None:
            small_node = node

        if root_node is not None and macro_node is not None and small_node is not None:
            break

    return root_node, macro_node, small_node


def get_node_details(T, node_id):
    node = T.nodes[node_id]
    node_type = node.get('type', 'Unknown')
    node_type_str = "Macro" if node_type == 1 else "Small" if node_type == 2 else "Root"
    network_equipments = node.get('network_equipment', [])

    # Dictionary to count the number of equipments by type
    equipment_count = {}

    for eq in network_equipments:
        equipment_type = eq.equipment_type
        # Use data_rate for transceivers, XR_MODULE and MEDIA_CONVERTER, otherwise capacity
        if "TRANSCEIVERS" in equipment_type.name or "XR_MODULE" in equipment_type.name or "MEDIA_CONVERTER" in equipment_type.name:
            capacity_or_datarate = eq.data_rate
        else:
            capacity_or_datarate = network_equipment_types[equipment_type].capacity

        if equipment_type not in equipment_count:
            equipment_count[equipment_type] = {'cost': network_equipment_types[equipment_type].normalized_price,
                                               'capacity_or_datarate': capacity_or_datarate,
                                               'quantity': 0}
        equipment_count[equipment_type]['quantity'] += 1

    # Convert the dictionary into a list of details
    network_details = []
    for equipment_type, details in equipment_count.items():
        network_details.append({
            'type': equipment_type.name,
            'cost': details['cost'],
            'capacity_or_datarate': details['capacity_or_datarate'],
            'quantity': details['quantity']
        })

    node_details = {
        'Node ID': node_id,
        'Node Type': node_type_str,
        'Network Equipments': network_details
    }

    return node_details


def get_node_radio_equipment_details(T, node_id, term):
    node = T.nodes[node_id]
    radio_equipments = node.get('radio_equipment', [])

    radio_details = []
    radio_equipment_summary = {}
    for eq in radio_equipments:
        required_capacity = eq.calculate_required_capacity(term)
        equipment_type = eq.equipment_type.name
        if equipment_type not in radio_equipment_summary:
            radio_equipment_summary[equipment_type] = {'quantity': 0, 'total_required_capacity': 0,
                                                       'individual_capacity': required_capacity}
        radio_equipment_summary[equipment_type]['quantity'] += 1
        radio_equipment_summary[equipment_type]['total_required_capacity'] += required_capacity

    for eq_type, summary in radio_equipment_summary.items():
        radio_details.append({
            'type': eq_type,
            'quantity': summary['quantity'],
            'individual_capacity': summary['individual_capacity'],
            'total_required_capacity': summary['total_required_capacity']
        })

    return radio_details


def format_node_details_for_report(node_details, radio_details, styles):
    elements = []

    elements.append(
        Paragraph(f"Node {node_details['Node ID']} (Type: {node_details['Node Type']}):", styles['Heading3']))
    elements.append(Spacer(1, 0.2 * inch))

    # Radio Equipment Details
    if radio_details:
        elements.append(Paragraph("Radio Equipment Details:", styles['Heading4']))
        table_data = [["Type", "Quantity", "Individual Required Capacity (Gbps)", "Total Required Capacity (Gbps)"]]
        total_required_capacity = 0
        table_data.extend([
            [eq['type'], eq['quantity'], f"{eq['individual_capacity']} Gbps", f"{eq['total_required_capacity']} Gbps"]
            for eq in radio_details
        ])
        # Calculate the total required capacity
        total_required_capacity = sum(eq['total_required_capacity'] for eq in radio_details)
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.1 * inch))

        # Add the row with the total required capacity
        elements.append(Paragraph(f"Total Required Capacity: {total_required_capacity} Gbps", styles['Normal']))
        elements.append(Spacer(1, 0.5 * inch))

    # Network Equipment Details
    elements.append(Paragraph("Network Equipment Details:", styles['Heading4']))
    table_data = [["Type", "Quantity", "Cost", "Data Rate / Capacity"]]
    table_data.extend([
        [eq['type'], eq['quantity'], f"{eq['cost']} CUs", f"{eq['capacity_or_datarate']} Gbps"] for eq in
        node_details['Network Equipments']
    ])
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    return elements


def get_node_details_for_report(T, root_node, macro_node, small_node, term):
    elements = []
    styles = getSampleStyleSheet()

    # Root Node Details
    if root_node is not None:
        root_details = get_node_details(T, root_node)
        root_radio_details = get_node_radio_equipment_details(T, root_node, term)
        elements.extend(format_node_details_for_report(root_details, root_radio_details, styles))

    # Macro Node Details
    if macro_node is not None:
        macro_details = get_node_details(T, macro_node)
        macro_radio_details = get_node_radio_equipment_details(T, macro_node, term)
        elements.extend(format_node_details_for_report(macro_details, macro_radio_details, styles))

    # Small Node Details
    if small_node is not None:
        small_details = get_node_details(T, small_node)
        small_radio_details = get_node_radio_equipment_details(T, small_node, term)
        elements.extend(format_node_details_for_report(small_details, small_radio_details, styles))

    return elements


def create_report_pdf_with_node_details(report_filename, scenario):
    doc = SimpleDocTemplate(report_filename, pagesize=letter)
    elements = []

    # Mapping to translate file names into scenario names
    scenario_map = {
        'dense_urban': 'Dense Urban',
        'urban': 'Urban',
        'suburban': 'Suburban',
        'rural': 'Rural'
    }

    # Title
    styles = getSampleStyleSheet()
    title = Paragraph(f"Report per scenario {scenario_map[scenario]}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.5 * inch))

    # Topology image
    elements.append(Paragraph(f"Topology ({scenario_map[scenario]}):", styles['Heading2']))
    img_path = f"{scenario}_topology.png"  # Assuming you have pre-saved topology images for each scenario
    elements.append(Image(img_path, width=6 * inch, height=6 * inch))
    elements.append(Spacer(1, 0.5 * inch))

    # Add topology details in the report
    T, T_m, A = create_geotype(scenario_map[scenario])
    root_count, macro_count, small_count = get_topology_details(T)

    elements.append(Paragraph("Topology Details:", styles['Heading2']))
    elements.append(Paragraph(f"Root Nodes: {root_count}", styles['Normal']))
    elements.append(Paragraph(f"Macro Nodes: {macro_count}", styles['Normal']))
    elements.append(Paragraph(f"Small Nodes: {small_count}", styles['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # Define the solutions based on the "version" parameter
    '''
    if version == 'wo':
        solution_names = [("P2P", soluzione_1_wo_smallcellswitch), ("WDM", soluzione_2_wo_smallcellmux), ("P2MP", soluzione_3_wo_smallcellaggr)]
    else:
        solution_names = [("P2P", soluzione_1_with_smallcellswitch), ("WDM", soluzione_2_with_smallcellmux), ("P2MP", soluzione_3_with_smallcellaggr),("P2MP-WP", soluzione_3_with_smallcellaggr_with_preaggregation)]
    '''
    solution_names = [("P2P", soluzione_1_with_smallcellswitch), ("WDM", soluzione_2_with_smallcellmux),
                      ("P2MP", soluzione_3_with_smallcellaggr),
                      ("P2MP-WP", soluzione_3_with_smallcellaggr_with_preaggregation)]

    terms = ['Medium', 'Long']

    # Generate the cost plot for the medium term
    deploy_radio_equipment(T, 'Medium', scenario_map[scenario])
    # solution_names[0][1](T,'Medium')  # Execute the first solution

    elements.append(Paragraph("Cost Breakdown (Medium Term):", styles['Heading2']))
    generate_stacked_cost_plot(T, 'Medium', scenario_map[scenario], 'short_term_cost_breakdown.png')
    elements.append(Image('short_term_cost_breakdown.png', width=6 * inch, height=4 * inch))
    elements.append(Spacer(1, 0.5 * inch))

    # Generate the cost plot for the long term
    T, T_m, A = create_geotype(scenario_map[scenario])
    deploy_radio_equipment(T, 'Long', scenario_map[scenario])
    # solution_names[0][1](T,'Long')  # Execute the first solution

    elements.append(Paragraph("Cost Breakdown (Long Term):", styles['Heading2']))
    generate_stacked_cost_plot(T, 'Long', scenario_map[scenario], 'long_term_cost_breakdown.png')
    elements.append(Image('long_term_cost_breakdown.png', width=6 * inch, height=4 * inch))
    elements.append(Spacer(1, 0.5 * inch))

    # Find the nodes to detail
    root_node, macro_node, small_node = find_first_node_of_each_type(T)

    # Execute the solutions for the specified scenario
    for name, solution_fn in solution_names:
        for term in terms:
            elements.append(Paragraph(f"{name} - {term} Term", styles['Heading2']))
            T, T_m, A = create_geotype(scenario_map[scenario])
            deploy_radio_equipment(T, term, scenario_map[scenario])
            solution_fn(T, term)
            elements.extend(get_node_details_for_report(T, root_node, macro_node, small_node, term))

    doc.build(elements)


# Create reports for all scenarios and versions
scenarios = ['dense_urban', 'urban', 'suburban', 'rural']

for scenario in scenarios:
    report_filename = f"{scenario.capitalize()}_Report.pdf"
    create_report_pdf_with_node_details(report_filename, scenario)

# ENERGY
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl

plt.rc('font', size=30)  # Set the default font size to 14

# Loop through deployment scenarios to create bar plots
for scenario in ['Dense Urban', 'Urban', 'Suburban', 'Rural']:
    # Create a dictionary to store the data for each solution
    data = {
        'Soluzione': [],
        'Term': [],
        'Consumption': [],
        'Consumption Type': []
    }

    # For each term (medium term, long term)
    for term in ['Medium', 'Long']:
        # Aggiungi WDM-WP alla lista delle soluzioni
        solutions = ['soluzione1_with', 'soluzione2_with', 'soluzione2_with_preagg', 'soluzione3',
                     'soluzione3_with_preagg']

        for solution in solutions:
            T, T_m, A = create_geotype(scenario)
            deploy_radio_equipment(T, term, scenario)

            if solution == 'soluzione1_with':
                soluzione_1_with_smallcellswitch(T, term)
            elif solution == 'soluzione2_with':
                soluzione_2_with_smallcellmux(T, term)
            elif solution == 'soluzione2_with_preagg':  # Nuova soluzione!
                soluzione_2_with_smallcellaggr_with_preaggregation(T, term)
            elif solution == 'soluzione3':
                soluzione_3_with_smallcellaggr(T, term)
            elif solution == 'soluzione3_with_preagg':
                soluzione_3_with_smallcellaggr_with_preaggregation(T, term)

            # Calculate the total consumption of switching and other components
            switching_consumption = sum(
                T.nodes[node]['switching_consumption'] for node in T.nodes()) * 365 * 24 / 1000000
            other_consumption = sum(T.nodes[node]['other_consumption'] for node in T.nodes()) * 365 * 24 / 1000000

            # Add data to the dictionary for stacked consumption
            data['Soluzione'].append(solution)
            data['Term'].append(term)
            data['Consumption'].append(switching_consumption)
            data['Consumption Type'].append('Switching')

            data['Soluzione'].append(solution)
            data['Term'].append(term)
            data['Consumption'].append(other_consumption)
            data['Consumption Type'].append('Other')

    # Create the DataFrame from the data
    df = pd.DataFrame(data)

    # Create a bar chart with two stacked columns for each solution (medium term and long term)
    plt.figure(figsize=(9, 7))
    ax = plt.gca()
    # Definition of the colors for each term
    colors_medium = ['#1f77b4', '#aec7e8']  # Blue for "Switching", light blue for "Other"
    colors_long = ['#ff7f0e', '#ffbb78']  # Orange for "Switching", light orange for "Other"
    hatches_medium = ['/', '\\']  # Patterns for "Medium Term"
    hatches_long = ['+', 'x']  # Patterns for "Long Term"

    for term in ['Medium']:
        df_term = df[df['Term'] == term]
        df_pivot = df_term.pivot(index='Soluzione', columns='Consumption Type', values='Consumption')
        df_pivot.plot(kind='bar', stacked=True, ax=ax, position=+1.1, width=0.3, color=colors_medium)

    for term in ['Long']:
        df_term = df[df['Term'] == term]
        df_pivot = df_term.pivot(index='Soluzione', columns='Consumption Type', values='Consumption')
        ax = df_pivot.plot(kind='bar', stacked=True, ax=ax, position=-0.1, width=0.3, color=colors_long)

    bars = [thing for thing in ax.containers if isinstance(thing, mpl.container.BarContainer)]
    import itertools

    # patterns = itertools.cycle(('-', '+', 'x', '\\', '*', 'o', 'O', '.'))
    # patterns = itertools.cycle(('++','++','++','++', 'xx','xx','xx','xx','//','//','//','//', '\\\\', '\\\\', '\\\\', '\\\\'))
    patterns = itertools.cycle(
        ('+', '+', '+', '+', 'x', 'x', 'x', 'x', '/', '/', '/', '/', '\\', '\\', '\\', '\\'))

    for bar in bars:
        for patch in bar:
            patch.set_hatch(next(patterns))
    L = ax.legend()

    # Legend customization
    handles, labels = ax.get_legend_handles_labels()
    custom_labels = ['Transmission (MT)', 'Switching (MT)', 'Transmission (LT)', 'Switching (LT)']
    if scenario == 'Rural':
        plt.legend(handles=handles, labels=custom_labels)
    else:
        plt.legend().set_visible(False)
    plt.legend().set_visible(False)
    # plt.rc('font', size=24)  # Set the default font size to 14

    # plt.title(f'Energy Consumption for {scenario.capitalize()} Scenario')
    plt.ylabel('E (MWh)')
    # plt.xlabel('Solutions')
    plt.xlabel('')
    # plt.xticks(rotation=0, ticks=[0, 1, 2, 3])
    plt.xticks(rotation=0, ticks=[0, 1, 2, 3,4], labels=['P2P', 'WDM','WDM-WP', 'P2MP', 'P2MP-WP'])
    plt.xlim([-0.5, 4.5])
    plt.ylim([0, 120])
    # plt.legend(title='Consumption Type')
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(f'energy_consumption_{scenario}.pdf', format='pdf', dpi=300, bbox_inches='tight')
    plt.show()

# COST

# COST ANALYSIS

# Loop through deployment scenarios to create bar plots
for scenario in ['Dense Urban', 'Urban', 'Suburban', 'Rural']:
    # Create a dictionary to store the data for each solution
    data = {
        'Soluzione': [],
        'Term': [],
        'Cost': [],
        'Cost Type': []
    }

    # For each term (medium term, long term)
    for term in ['Medium', 'Long']:
        # List of solutions to represent
        solutions = ['soluzione1_with', 'soluzione2_with', 'soluzione2_with_preagg', 'soluzione3',
                     'soluzione3_with_preagg']

        for solution in solutions:
            T, T_m, A = create_geotype(scenario)
            deploy_radio_equipment(T, term, scenario)

            if solution == 'soluzione1_with':
                soluzione_1_with_smallcellswitch(T, term)
            elif solution == 'soluzione2_with':
                soluzione_2_with_smallcellmux(T, term)
            elif solution == 'soluzione2_with_preagg':  # Nuova soluzione!
                soluzione_2_with_smallcellaggr_with_preaggregation(T, term)
            elif solution == 'soluzione3':
                soluzione_3_with_smallcellaggr(T, term)
            elif solution == 'soluzione3_with_preagg':
                soluzione_3_with_smallcellaggr_with_preaggregation(T, term)

            # Calculate switching and transmission costs
            '''
            if ((solution == 'soluzione3' or solution == 'soluzione3_with_preagg') and scenario == 'Dense Urban'):
                transceiver_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"]) * 0.75
                switching_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE", "WDM_MUX", "MEDIA_CONVERTER", "TRANSPONDER"]) * 0.75
            elif ((solution == 'soluzione3' or solution == 'soluzione3_with_preagg') and scenario == 'Urban'):
                transceiver_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS",
                                                                "XR_MODULE"]) * 0.80
                switching_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE",
                                                              "WDM_MUX", "MEDIA_CONVERTER", "TRANSPONDER"]) * 0.80
            elif ((solution == 'soluzione3' or solution == 'soluzione3_with_preagg') and scenario == 'Suburban'):
                transceiver_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS",
                                                                "XR_MODULE"]) * 0.55
                switching_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE",
                                                              "WDM_MUX", "MEDIA_CONVERTER", "TRANSPONDER"]) * 0.55
            elif ((solution == 'soluzione3' or solution == 'soluzione3_with_preagg') and scenario == 'Rural'):
                transceiver_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS",
                                                                "XR_MODULE"]) * 0.85
                switching_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE",
                                                              "WDM_MUX", "MEDIA_CONVERTER", "TRANSPONDER"]) * 0.85
            else:
            '''
            transceiver_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS",
                                                            "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
            switching_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE",
                                                          "WDM_MUX"])

            # Add data to the dictionary for switching cost
            data['Soluzione'].append(solution)
            data['Term'].append(term)
            data['Cost'].append(switching_cost)
            data['Cost Type'].append('Switching')

            # Add data to the dictionary for transmission cost
            data['Soluzione'].append(solution)
            data['Term'].append(term)
            data['Cost'].append(transceiver_cost)
            data['Cost Type'].append('Transmission')

    # Create the DataFrame from the data
    df = pd.DataFrame(data)

    # Create a bar chart with two stacked columns for each solution (medium term and long term)
    plt.figure(figsize=(9, 7))
    ax = plt.gca()
    # Definition of the colors for each term
    # colors_medium = ['#1f77b4', '#aec7e8']  # Blue for "Switching", light blue for "Transmission"
    # colors_long = ['#ff7f0e', '#ffbb78']    # Orange for "Switching", light orange for "Transmission"

    for term in ['Medium']:
        df_term = df[df['Term'] == term]
        df_pivot = df_term.pivot(index='Soluzione', columns='Cost Type', values='Cost')
        df_pivot.plot(kind='bar', stacked=True, ax=ax, position=+1.1, width=0.3, color=colors_medium)

    for term in ['Long']:
        df_term = df[df['Term'] == term]
        df_pivot = df_term.pivot(index='Soluzione', columns='Cost Type', values='Cost')
        ax = df_pivot.plot(kind='bar', stacked=True, ax=ax, position=-0.1, width=0.3, color=colors_long)

    bars = [thing for thing in ax.containers if isinstance(thing, mpl.container.BarContainer)]
    import itertools

    # patterns = itertools.cycle(('-', '+', 'x', '\\', '*', 'o', 'O', '.'))
    # patterns = itertools.cycle(('++','++','++','++', 'xx','xx','xx','xx','//','//','//','//', '\\\\', '\\\\', '\\\\', '\\\\'))
    patterns = itertools.cycle(
        ('+', '+', '+', '+', 'x', 'x', 'x', 'x', '/', '/', '/', '/', '\\', '\\', '\\', '\\'))

    for bar in bars:
        for patch in bar:
            patch.set_hatch(next(patterns))
    L = ax.legend()

    # Personalizzazione della legenda
    handles, labels = ax.get_legend_handles_labels()
    custom_labels = ['Transmission (MT)', 'Switching (MT)', 'Transmission (LT)', 'Switching (LT)']
    if scenario == 'Rural':
        plt.legend(handles=handles, labels=custom_labels)
    else:
        plt.legend().set_visible(False)

    # plt.title(f'Cost Analysis for {scenario.capitalize()} Scenario')
    plt.ylabel('CAPEX (Cost Units)')
    # plt.xlabel('Solutions')
    plt.xlabel('')
    # plt.xticks(rotation=0, ticks=[0, 1, 2, 3])
    plt.xticks(rotation=0, ticks=[0, 1, 2, 3,4], labels=['P2P', 'WDM', 'WDM-WP', 'P2MP', 'P2MP-WP'])
    plt.xlim([-0.5, 4.5])
    plt.ylim([0, 350])
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(f'cost_analysis_tris_{scenario}.pdf', format='pdf', dpi=300, bbox_inches='tight')
    plt.show()

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_cost_vs_alpha(df_results, scenario, term):
    """
    Crea un grafico del costo totale vs alpha per un dato scenario e termine
    """
    plt.figure(figsize=(10, 8))

    # Filtra i dati per lo scenario e il termine specificati
    df_filtered = df_results[(df_results['Scenario'] == scenario) & (df_results['Term'] == term)]

    # Crea il grafico per ogni soluzione
    for solution in ['P2P', 'WDM', 'WDM-WP', 'P2MP', 'P2MP-WP']:
        df_sol = df_filtered[df_filtered['Solution'] == solution]
        plt.plot(df_sol['Alpha'], df_sol['Total Cost'], marker='o', label=solution, linewidth=2, markersize=8)

    plt.xlabel('Alpha (XR cost factor)', fontsize=14)
    plt.ylabel('Total Cost (Cost Units)', fontsize=14)
    plt.title(f'Total Cost vs Alpha - {scenario} ({term} Term)', fontsize=16)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Salva il grafico
    filename = f'cost_vs_alpha_{scenario.lower().replace(" ", "_")}_{term.lower()}.pdf'
    plt.savefig(filename, format='pdf', dpi=300, bbox_inches='tight')
    plt.show()


def plot_cost_vs_alpha_all_scenarios(df_results, term):
    """
    Crea una griglia di grafici per tutti gli scenari di deployment
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    scenarios = ['Dense Urban', 'Urban', 'Suburban', 'Rural']

    for idx, scenario in enumerate(scenarios):
        ax = axes[idx]
        df_filtered = df_results[(df_results['Scenario'] == scenario) & (df_results['Term'] == term)]

        for solution in ['P2P', 'WDM', 'WDM-WP', 'P2MP', 'P2MP-WP']:
            df_sol = df_filtered[df_filtered['Solution'] == solution]
            ax.plot(df_sol['Alpha'], df_sol['Total Cost'], marker='o', label=solution, linewidth=2, markersize=6)

        ax.set_xlabel('Alpha (XR cost factor)', fontsize=12)
        ax.set_ylabel('Total Cost (Cost Units)', fontsize=12)
        ax.set_title(f'{scenario}', fontsize=14)
        ax.grid(True, alpha=0.3)

        if idx == 0:
            ax.legend(fontsize=10)

    fig.suptitle(f'Total Cost vs Alpha - All Scenarios ({term} Term)', fontsize=16)
    plt.tight_layout()

    # Salva il grafico
    filename = f'cost_vs_alpha_all_scenarios_{term.lower()}.pdf'
    plt.savefig(filename, format='pdf', dpi=300, bbox_inches='tight')
    plt.show()


def plot_relative_cost_savings(df_results, reference_solution='P2P'):
    """
    Plotta il risparmio percentuale rispetto a una soluzione di riferimento
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    scenarios = ['Dense Urban', 'Urban', 'Suburban', 'Rural']

    for idx, scenario in enumerate(scenarios):
        ax = axes[idx]

        for term in ['Medium', 'Long']:
            df_filtered = df_results[(df_results['Scenario'] == scenario) & (df_results['Term'] == term)]

            # Calcola il costo della soluzione di riferimento per ogni alpha
            df_ref = df_filtered[df_filtered['Solution'] == reference_solution]

            for solution in ['WDM', 'WDM-WP', 'P2MP', 'P2MP-WP']:
                if solution == reference_solution:
                    continue

                df_sol = df_filtered[df_filtered['Solution'] == solution]

                # Calcola il risparmio percentuale
                savings = []
                alpha_vals = []

                for alpha in df_sol['Alpha'].unique():
                    ref_cost = df_ref[df_ref['Alpha'] == alpha]['Total Cost'].values[0]
                    sol_cost = df_sol[df_sol['Alpha'] == alpha]['Total Cost'].values[0]
                    saving_pct = ((ref_cost - sol_cost) / ref_cost) * 100
                    savings.append(saving_pct)
                    alpha_vals.append(alpha)

                linestyle = '-' if term == 'Medium' else '--'
                ax.plot(alpha_vals, savings, marker='o', label=f'{solution} ({term})',
                        linewidth=2, markersize=6, linestyle=linestyle)

        ax.set_xlabel('Alpha (XR cost factor)', fontsize=12)
        ax.set_ylabel(f'Cost Savings vs {reference_solution} (%)', fontsize=12)
        ax.set_title(f'{scenario}', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.5)

        if idx == 0:
            ax.legend(fontsize=9)

    fig.suptitle(f'Relative Cost Savings vs {reference_solution} Solution', fontsize=16)
    plt.tight_layout()

    # Salva il grafico
    plt.savefig('relative_cost_savings_vs_alpha.pdf', format='pdf', dpi=300, bbox_inches='tight')
    plt.show()


# ============================================
# CORRECTED ALFA ANALYSIS FOR XR EQUIPMENT
# Costi XR = Costi GREY LR × Alpha
# ============================================

def update_xr_costs_based_on_grey_lr(network_equipment_types, NetworkEquipmentTypeEnum, alpha):
    """
    Aggiorna i costi XR basandosi sui costi dei GREY LR transceivers moltiplicati per alpha
    """
    # Mapping tra XR modules e corrispondenti GREY LR transceivers
    xr_to_grey_mapping = {
        NetworkEquipmentTypeEnum.XR_MODULE_25G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_25G_LR,
        NetworkEquipmentTypeEnum.XR_MODULE_50G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_50G_LR,
        NetworkEquipmentTypeEnum.XR_MODULE_100G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR,
        NetworkEquipmentTypeEnum.XR_MODULE_200G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR,  # 2x100G
        NetworkEquipmentTypeEnum.XR_MODULE_400G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_LR,
        NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR,
        NetworkEquipmentTypeEnum.XR_MODULE_HUB_200G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR,  # 2x100G
        NetworkEquipmentTypeEnum.XR_MODULE_HUB_400G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_LR,
    }

    # Aggiorna i costi XR modules
    for xr_enum, grey_enum in xr_to_grey_mapping.items():
        grey_normalized_cost = network_equipment_types[grey_enum].normalized_price

        # Per moduli 200G, usa 2x il costo del 100G
        if "200G" in xr_enum.name:
            network_equipment_types[xr_enum].normalized_price = 2 * grey_normalized_cost * alpha
        else:
            network_equipment_types[xr_enum].normalized_price = grey_normalized_cost * alpha

    # Aggiorna i media converter costs (50% del costo XR corrispondente)
    media_converter_mapping = {
        NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR,
        NetworkEquipmentTypeEnum.MEDIA_CONVERTER_200G_8X25G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_100G_LR,
        # 2x100G
        NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G: NetworkEquipmentTypeEnum.GREY_TRANSCEIVERS_400G_LR,
    }

    for mc_enum, grey_enum in media_converter_mapping.items():
        grey_normalized_cost = network_equipment_types[grey_enum].normalized_price

        if "200G" in mc_enum.name:
            network_equipment_types[mc_enum].normalized_price = 2 * grey_normalized_cost * alpha * 0.5
        else:
            network_equipment_types[mc_enum].normalized_price = grey_normalized_cost * alpha * 0.5


def run_cost_analysis_with_alpha_corrected(alpha_values, temporal_scenarios, deployment_scenarios):
    """
    Esegue l'analisi del costo totale per tutte le soluzioni al variare di alpha
    XR cost = GREY LR cost × alpha
    """
    results = []

    for alpha in alpha_values:
        print(f"Analizzando alpha = {alpha}")

        # RIPRISTINA I COSTI ORIGINALI PRIMA DI AGGIORNARE CON IL NUOVO ALPHA
        reset_all_costs_to_original()

        # POI AGGIORNA I COSTI XR CON QUESTO SPECIFICO VALORE DI ALPHA
        update_xr_costs_based_on_grey_lr(network_equipment_types, NetworkEquipmentTypeEnum, alpha)

        for term in temporal_scenarios:
            for scenario in deployment_scenarios:
                # Lista delle soluzioni da testare
                solutions = [
                    ('P2P', soluzione_1_with_smallcellswitch),
                    ('WDM', soluzione_2_with_smallcellmux),
                    ('WDM-WP', soluzione_2_with_smallcellaggr_with_preaggregation),
                    ('P2MP', soluzione_3_with_smallcellaggr),
                    ('P2MP-WP', soluzione_3_with_smallcellaggr_with_preaggregation)
                ]

                for sol_name, sol_func in solutions:
                    # Crea nuovo grafo per ogni test
                    T, T_m, A = create_geotype(scenario)
                    deploy_radio_equipment(T, term, scenario)

                    # NON aggiornare qui - i costi sono già stati impostati una volta per questo alpha!

                    # Applica la soluzione
                    sol_func(T, term)

                    # Calcola il costo totale
                    total_cost = calculate_total_cost(T)

                    results.append({
                        'Alpha': alpha,
                        'Solution': sol_name,
                        'Term': term,
                        'Scenario': scenario,
                        'Total Cost': total_cost,
                        'Normalized Cost': total_cost / A
                    })

    return pd.DataFrame(results)

# Definisci i valori di alpha da testare
alpha_values = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]

# Scenari temporali e di deployment
temporal_scenarios = ['Medium', 'Long']
deployment_scenarios = ['Dense Urban', 'Urban', 'Suburban', 'Rural']

print("Avvio analisi costo XR parametrico CORRETTA...")
print("XR cost = GREY LR cost × alpha")

# Esegui l'analisi corretta
df_results_corrected = run_cost_analysis_with_alpha_corrected(alpha_values, temporal_scenarios, deployment_scenarios)

# Salva i risultati in CSV
df_results_corrected.to_csv('xr_cost_analysis_results_corrected.csv', index=False)
print("Risultati corretti salvati in 'xr_cost_analysis_results_corrected.csv'")

# Crea i grafici per ogni scenario e termine
for scenario in deployment_scenarios:
    for term in temporal_scenarios:
        plot_cost_vs_alpha(df_results_corrected, scenario, term)

# Crea grafici combinati
for term in temporal_scenarios:
    plot_cost_vs_alpha_all_scenarios(df_results_corrected, term)

# Crea grafici del risparmio relativo
plot_relative_cost_savings(df_results_corrected)

print("Analisi corretta completata!")


# ============================================
# BEST/WORST CASE ANALYSIS FOR XR EQUIPMENT
# ============================================

# ============================================
# BEST/WORST CASE ANALYSIS FOR XR EQUIPMENT
# ============================================

# RIPRISTINA I COSTI ORIGINALI PRIMA DI INIZIARE
reset_all_costs_to_original()

# Definizione dei costi e consumi per XR modules - Best e Worst case
XR_COSTS = {
    'best': {
        'XR_100G': 1.0,  # CU
        'XR_200G': 1.2,  # CU
        'XR_400G': 1.4  # CU
    },
    'worst': {
        'XR_100G': 1.5,  # CU
        'XR_200G': 1.8,  # CU
        'XR_400G': 2.1  # CU
    }
}

XR_POWER = {
    'best': {
        'XR_100G': 5.5,  # W
        'XR_200G': 13.5,  # W
        'XR_400G': 22.0  # W
    },
    'worst': {
        'XR_100G': 7.2,  # W
        'XR_200G': 18.0,  # W
        'XR_400G': 29.0  # W
    }
}


def update_xr_equipment_scenario(network_equipment_types, NetworkEquipmentTypeEnum, case='best'):
    """
    Aggiorna costi e consumi energetici per XR equipment basandosi su best/worst case
    """
    if case not in ['best', 'worst']:
        raise ValueError("Case deve essere 'best' o 'worst'")

    # Update XR modules da 25G a 100G
    if '25G' in NetworkEquipmentTypeEnum.XR_MODULE_25G.name:
        network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_25G].normalized_price = XR_COSTS[case][
                                                                                               'XR_100G'] * 0.25
        network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_25G].max_power = XR_POWER[case]['XR_100G'] * 0.25

    if '50G' in NetworkEquipmentTypeEnum.XR_MODULE_50G.name:
        network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_50G].normalized_price = XR_COSTS[case][
                                                                                               'XR_100G'] * 0.5
        network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_50G].max_power = XR_POWER[case]['XR_100G'] * 0.5

    # XR 100G modules
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_100G].normalized_price = XR_COSTS[case]['XR_100G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_100G].max_power = XR_POWER[case]['XR_100G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G].normalized_price = XR_COSTS[case]['XR_100G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_HUB_100G].max_power = XR_POWER[case]['XR_100G']

    # XR 200G modules
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_200G].normalized_price = XR_COSTS[case]['XR_200G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_200G].max_power = XR_POWER[case]['XR_200G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_HUB_200G].normalized_price = XR_COSTS[case]['XR_200G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_HUB_200G].max_power = XR_POWER[case]['XR_200G']

    # XR 400G modules
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_400G].normalized_price = XR_COSTS[case]['XR_400G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_400G].max_power = XR_POWER[case]['XR_400G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_HUB_400G].normalized_price = XR_COSTS[case]['XR_400G']
    network_equipment_types[NetworkEquipmentTypeEnum.XR_MODULE_HUB_400G].max_power = XR_POWER[case]['XR_400G']

    # Media converters - 50% del costo XR, 30% del consumo
    network_equipment_types[NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G].normalized_price = XR_COSTS[case][
                                                                                                        'XR_100G'] * 0.5
    network_equipment_types[NetworkEquipmentTypeEnum.MEDIA_CONVERTER_100G_4X25G].max_power = XR_POWER[case][
                                                                                                 'XR_100G'] * 0.3

    network_equipment_types[NetworkEquipmentTypeEnum.MEDIA_CONVERTER_200G_8X25G].normalized_price = XR_COSTS[case][
                                                                                                        'XR_200G'] * 0.5
    network_equipment_types[NetworkEquipmentTypeEnum.MEDIA_CONVERTER_200G_8X25G].max_power = XR_POWER[case][
                                                                                                 'XR_200G'] * 0.3

    network_equipment_types[NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G].normalized_price = XR_COSTS[case][
                                                                                                       'XR_400G'] * 0.5
    network_equipment_types[NetworkEquipmentTypeEnum.MEDIA_CONVERTER_400G_400G].max_power = XR_POWER[case][
                                                                                                'XR_400G'] * 0.3


def calculate_total_energy_consumption(T):
    """Calcola consumo energetico totale annuale in MWh"""
    switching_consumption = sum(T.nodes[node]['switching_consumption'] for node in T.nodes())
    other_consumption = sum(T.nodes[node]['other_consumption'] for node in T.nodes())
    total_annual_mwh = (switching_consumption + other_consumption) * 365 * 24 / 1000000
    return total_annual_mwh


def calculate_energy_component(T, component_type):
    """Calcola consumo energetico per componente specifico in MWh"""
    consumption = sum(T.nodes[node][component_type] for node in T.nodes())
    annual_mwh = consumption * 365 * 24 / 1000000
    return annual_mwh


# Esegui l'analisi best/worst case
print("\n=== BEST/WORST CASE ANALYSIS ===")
results_best_worst = []

temporal_scenarios = ['Medium', 'Long']
deployment_scenarios = ['Dense Urban', 'Urban', 'Suburban', 'Rural']

for term in temporal_scenarios:
    for scenario in deployment_scenarios:
        print(f"Analyzing {scenario} - {term} term...")

        # P2P (non usa XR)
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        soluzione_1_with_smallcellswitch(T, term)

        p2p_cost = calculate_total_cost(T)
        p2p_tx_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        p2p_mux_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE","WDM_MUX"])
        p2p_energy = calculate_total_energy_consumption(T)
        p2p_tx_energy = calculate_energy_component(T, 'other_consumption')
        p2p_sw_energy = calculate_energy_component(T, 'switching_consumption')

        results_best_worst.append({
            'Solution': 'P2P', 'Case': 'N/A', 'Term': term, 'Scenario': scenario,
            'Total Cost': p2p_cost, 'TX Cost': p2p_tx_cost, 'MUX Cost': p2p_mux_cost,
            'Total Energy': p2p_energy, 'TX Energy': p2p_tx_energy, 'SW Energy': p2p_sw_energy
        })

        # WDM (non usa XR)
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        soluzione_2_with_smallcellmux(T, term)

        wdm_cost = calculate_total_cost(T)
        wdm_tx_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        wdm_mux_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE", "WDM_MUX"])
        wdm_energy = calculate_total_energy_consumption(T)
        wdm_tx_energy = calculate_energy_component(T, 'other_consumption')
        wdm_sw_energy = calculate_energy_component(T, 'switching_consumption')

        results_best_worst.append({
            'Solution': 'WDM', 'Case': 'N/A', 'Term': term, 'Scenario': scenario,
            'Total Cost': wdm_cost, 'TX Cost': wdm_tx_cost, 'MUX Cost': wdm_mux_cost,
            'Total Energy': wdm_energy, 'TX Energy': wdm_tx_energy, 'SW Energy': wdm_sw_energy
        })

        # WDM-WP (non usa XR)
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        soluzione_2_with_smallcellaggr_with_preaggregation(T, term)

        wdm_wp_cost = calculate_total_cost(T)
        wdm_wp_tx_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        wdm_wp_mux_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE","WDM_MUX"])
        wdm_wp_energy = calculate_total_energy_consumption(T)
        wdm_wp_tx_energy = calculate_energy_component(T, 'other_consumption')
        wdm_wp_sw_energy = calculate_energy_component(T, 'switching_consumption')

        results_best_worst.append({
            'Solution': 'WDM-WP', 'Case': 'N/A', 'Term': term, 'Scenario': scenario,
            'Total Cost': wdm_wp_cost, 'TX Cost': wdm_wp_tx_cost, 'MUX Cost': wdm_wp_mux_cost,
            'Total Energy': wdm_wp_energy, 'TX Energy': wdm_wp_tx_energy, 'SW Energy': wdm_wp_sw_energy
        })

        # P2MP Best Case
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        update_xr_equipment_scenario(network_equipment_types, NetworkEquipmentTypeEnum, 'best')
        soluzione_3_with_smallcellaggr(T, term)

        p2mp_best_cost = calculate_total_cost(T)
        p2mp_best_tx_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        p2mp_best_mux_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE", "WDM_MUX"])
        p2mp_best_energy = calculate_total_energy_consumption(T)
        p2mp_best_tx_energy = calculate_energy_component(T, 'other_consumption')
        p2mp_best_sw_energy = calculate_energy_component(T, 'switching_consumption')

        results_best_worst.append({
            'Solution': 'P2MP', 'Case': 'Best', 'Term': term, 'Scenario': scenario,
            'Total Cost': p2mp_best_cost, 'TX Cost': p2mp_best_tx_cost, 'MUX Cost': p2mp_best_mux_cost,
            'Total Energy': p2mp_best_energy, 'TX Energy': p2mp_best_tx_energy, 'SW Energy': p2mp_best_sw_energy
        })

        # P2MP Worst Case
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        update_xr_equipment_scenario(network_equipment_types, NetworkEquipmentTypeEnum, 'worst')
        soluzione_3_with_smallcellaggr(T, term)

        p2mp_worst_cost = calculate_total_cost(T)
        p2mp_worst_tx_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        p2mp_worst_mux_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE", "WDM_MUX"])
        p2mp_worst_energy = calculate_total_energy_consumption(T)
        p2mp_worst_tx_energy = calculate_energy_component(T, 'other_consumption')
        p2mp_worst_sw_energy = calculate_energy_component(T, 'switching_consumption')

        results_best_worst.append({
            'Solution': 'P2MP', 'Case': 'Worst', 'Term': term, 'Scenario': scenario,
            'Total Cost': p2mp_worst_cost, 'TX Cost': p2mp_worst_tx_cost, 'MUX Cost': p2mp_worst_mux_cost,
            'Total Energy': p2mp_worst_energy, 'TX Energy': p2mp_worst_tx_energy, 'SW Energy': p2mp_worst_sw_energy
        })

        # P2MP-WP Best Case
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        update_xr_equipment_scenario(network_equipment_types, NetworkEquipmentTypeEnum, 'best')
        soluzione_3_with_smallcellaggr_with_preaggregation(T, term)

        p2mp_wp_best_cost = calculate_total_cost(T)
        p2mp_wp_best_tx_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        p2mp_wp_best_mux_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE", "WDM_MUX"])
        p2mp_wp_best_energy = calculate_total_energy_consumption(T)
        p2mp_wp_best_tx_energy = calculate_energy_component(T, 'other_consumption')
        p2mp_wp_best_sw_energy = calculate_energy_component(T, 'switching_consumption')

        results_best_worst.append({
            'Solution': 'P2MP-WP', 'Case': 'Best', 'Term': term, 'Scenario': scenario,
            'Total Cost': p2mp_wp_best_cost, 'TX Cost': p2mp_wp_best_tx_cost, 'MUX Cost': p2mp_wp_best_mux_cost,
            'Total Energy': p2mp_wp_best_energy, 'TX Energy': p2mp_wp_best_tx_energy,
            'SW Energy': p2mp_wp_best_sw_energy
        })

        # P2MP-WP Worst Case
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        update_xr_equipment_scenario(network_equipment_types, NetworkEquipmentTypeEnum, 'worst')
        soluzione_3_with_smallcellaggr_with_preaggregation(T, term)

        p2mp_wp_worst_cost = calculate_total_cost(T)
        p2mp_wp_worst_tx_cost = calculate_cost_component(T, ["GREY_TRANSCEIVERS", "WDM_TRANSCEIVERS", "XR_MODULE", "MEDIA_CONVERTER", "TRANSPONDER"])
        p2mp_wp_worst_mux_cost = calculate_cost_component(T, ["SWITCH_SMALL", "SWITCH_MEDIUM", "SWITCH_BIG" , "SWITCH_EXTRA_LARGE", "WDM_MUX"])
        p2mp_wp_worst_energy = calculate_total_energy_consumption(T)
        p2mp_wp_worst_tx_energy = calculate_energy_component(T, 'other_consumption')
        p2mp_wp_worst_sw_energy = calculate_energy_component(T, 'switching_consumption')

        results_best_worst.append({
            'Solution': 'P2MP-WP', 'Case': 'Worst', 'Term': term, 'Scenario': scenario,
            'Total Cost': p2mp_wp_worst_cost, 'TX Cost': p2mp_wp_worst_tx_cost, 'MUX Cost': p2mp_wp_worst_mux_cost,
            'Total Energy': p2mp_wp_worst_energy, 'TX Energy': p2mp_wp_worst_tx_energy,
            'SW Energy': p2mp_wp_worst_sw_energy
        })

# Converti in DataFrame
df_best_worst = pd.DataFrame(results_best_worst)
df_best_worst.to_csv('best_worst_case_analysis.csv', index=False)
print("Results saved to 'best_worst_case_analysis.csv'")

# GRAFICI PRIMA COMPARISON (P2P, WDM, P2MP best, P2MP worst)
print("\nCreating first comparison plots...")

import matplotlib as mpl

plt.rc('font', size=30)

for scenario in deployment_scenarios:
    # Cost comparison plot
    plt.figure(figsize=(12, 8))

    # Filtra dati
    df_scenario = df_best_worst[
        (df_best_worst['Scenario'] == scenario) &
        df_best_worst['Solution'].isin(['P2P', 'WDM', 'P2MP'])
        ]

    # Prepara dati per il plot
    x_labels = ['P2P', 'WDM', 'P2MP\n(Best)', 'P2MP\n(Worst)']
    x_pos = np.arange(len(x_labels))
    width = 0.35

    # Medium Term
    mt_tx = []
    mt_mux = []
    # Long Term
    lt_tx = []
    lt_mux = []

    for sol in ['P2P', 'WDM']:
        df_sol_mt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Medium')]
        df_sol_lt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Long')]

        mt_tx.append(df_sol_mt['TX Cost'].values[0] if len(df_sol_mt) > 0 else 0)
        mt_mux.append(df_sol_mt['MUX Cost'].values[0] if len(df_sol_mt) > 0 else 0)
        lt_tx.append(df_sol_lt['TX Cost'].values[0] if len(df_sol_lt) > 0 else 0)
        lt_mux.append(df_sol_lt['MUX Cost'].values[0] if len(df_sol_lt) > 0 else 0)

    # P2MP Best e Worst
    for case in ['Best', 'Worst']:
        df_p2mp_mt = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                                 (df_scenario['Case'] == case) &
                                 (df_scenario['Term'] == 'Medium')]
        df_p2mp_lt = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                                 (df_scenario['Case'] == case) &
                                 (df_scenario['Term'] == 'Long')]

        mt_tx.append(df_p2mp_mt['TX Cost'].values[0] if len(df_p2mp_mt) > 0 else 0)
        mt_mux.append(df_p2mp_mt['MUX Cost'].values[0] if len(df_p2mp_mt) > 0 else 0)
        lt_tx.append(df_p2mp_lt['TX Cost'].values[0] if len(df_p2mp_lt) > 0 else 0)
        lt_mux.append(df_p2mp_lt['MUX Cost'].values[0] if len(df_p2mp_lt) > 0 else 0)

    # Plot
    colors_medium = ['#1f77b4', '#aec7e8']
    colors_long = ['#ff7f0e', '#ffbb78']

    # Medium term bars
    plt.bar(x_pos - width / 2, mt_tx, width, label='Transmission (MT)', color=colors_medium[0], edgecolor='black')
    plt.bar(x_pos - width / 2, mt_mux, width, bottom=mt_tx, label='Switching (MT)',
            color=colors_medium[1], edgecolor='black', hatch='//')

    # Long term bars
    plt.bar(x_pos + width / 2, lt_tx, width, label='Transmission (LT)', color=colors_long[0], edgecolor='black')
    plt.bar(x_pos + width / 2, lt_mux, width, bottom=lt_tx, label='Switching (LT)',
            color=colors_long[1], edgecolor='black', hatch='\\\\')

    plt.ylabel('CAPEX (Cost Units)')
    plt.xlabel('')
    plt.xticks(x_pos, x_labels)
    plt.xlim([-0.5, 3.5])
    plt.ylim([0, 350])
    if scenario == 'Rural':
        plt.legend()
    else:
        plt.legend().set_visible(False)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    plt.savefig(f'cost_comparison_v1_{scenario.lower().replace(" ", "_")}.pdf',
                format='pdf', dpi=300, bbox_inches='tight')
    plt.show()

    # GRAFICI ENERGIA - PRIMA COMPARISON (P2P, WDM, P2MP best, P2MP worst)
    print("\nCreating energy comparison plots (First set)...")

    for scenario in deployment_scenarios:
        plt.figure(figsize=(12, 8))

        # Filtra dati
        df_scenario = df_best_worst[
            (df_best_worst['Scenario'] == scenario) &
            df_best_worst['Solution'].isin(['P2P', 'WDM', 'P2MP'])
            ]

        # Prepara dati per il plot
        x_labels = ['P2P', 'WDM', 'P2MP\n(Best)', 'P2MP\n(Worst)']
        x_pos = np.arange(len(x_labels))
        width = 0.35

        # Medium Term
        mt_tx_energy = []
        mt_sw_energy = []
        # Long Term
        lt_tx_energy = []
        lt_sw_energy = []

        for sol in ['P2P', 'WDM']:
            df_sol_mt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Medium')]
            df_sol_lt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Long')]

            mt_tx_energy.append(df_sol_mt['TX Energy'].values[0] if len(df_sol_mt) > 0 else 0)
            mt_sw_energy.append(df_sol_mt['SW Energy'].values[0] if len(df_sol_mt) > 0 else 0)
            lt_tx_energy.append(df_sol_lt['TX Energy'].values[0] if len(df_sol_lt) > 0 else 0)
            lt_sw_energy.append(df_sol_lt['SW Energy'].values[0] if len(df_sol_lt) > 0 else 0)

        # P2MP Best e Worst
        for case in ['Best', 'Worst']:
            df_p2mp_mt = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                                     (df_scenario['Case'] == case) &
                                     (df_scenario['Term'] == 'Medium')]
            df_p2mp_lt = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                                     (df_scenario['Case'] == case) &
                                     (df_scenario['Term'] == 'Long')]

            mt_tx_energy.append(df_p2mp_mt['TX Energy'].values[0] if len(df_p2mp_mt) > 0 else 0)
            mt_sw_energy.append(df_p2mp_mt['SW Energy'].values[0] if len(df_p2mp_mt) > 0 else 0)
            lt_tx_energy.append(df_p2mp_lt['TX Energy'].values[0] if len(df_p2mp_lt) > 0 else 0)
            lt_sw_energy.append(df_p2mp_lt['SW Energy'].values[0] if len(df_p2mp_lt) > 0 else 0)

        # Plot
        colors_medium = ['#1f77b4', '#aec7e8']
        colors_long = ['#ff7f0e', '#ffbb78']

        # Medium term bars
        plt.bar(x_pos - width / 2, mt_tx_energy, width, label='Transmission (MT)', color=colors_medium[0], edgecolor='black')
        plt.bar(x_pos - width / 2, mt_sw_energy, width, bottom=mt_tx_energy, label='Switching (MT)',
                color=colors_medium[1], edgecolor='black', hatch='//')

        # Long term bars
        plt.bar(x_pos + width / 2, lt_tx_energy, width, label='Transmission (LT)', color=colors_long[0], edgecolor='black')
        plt.bar(x_pos + width / 2, lt_sw_energy, width, bottom=lt_tx_energy, label='Switching (LT)',
                color=colors_long[1], edgecolor='black', hatch='\\\\')

        plt.ylabel('Energy (MWh/year)')
        plt.xlabel('')
        plt.xticks(x_pos, x_labels)
        plt.xlim([-0.5, 3.5])
        plt.ylim([0, 120])
        if scenario == 'Rural':
            plt.legend()
        else:
            plt.legend().set_visible(False)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        plt.savefig(f'energy_comparison_v1_{scenario.lower().replace(" ", "_")}.pdf',
                    format='pdf', dpi=300, bbox_inches='tight')
        plt.show()

    # SECONDA COMPARISON: WDM, WDM-WP, P2MP (best/worst), P2MP-WP (best/worst)
    print("\nCreating second comparison plots (with WP variants)...")

    # COST COMPARISON V2
    for scenario in deployment_scenarios:
        plt.figure(figsize=(14, 8))

        # Filtra dati per includere WDM-WP e P2MP-WP
        df_scenario = df_best_worst[
            (df_best_worst['Scenario'] == scenario) &
            df_best_worst['Solution'].isin(['WDM', 'WDM-WP', 'P2MP', 'P2MP-WP'])
            ]

        # Prepara labels
        x_labels = ['WDM', 'WDM-WP', 'P2MP\n(Best)', 'P2MP-WP\n(Best)', 'P2MP\n(Worst)', 'P2MP-WP\n(Worst)']
        x_pos = np.arange(len(x_labels))
        width = 0.35

        # Arrays per i dati
        mt_tx = []
        mt_mux = []
        lt_tx = []
        lt_mux = []

        # WDM e WDM-WP
        for sol in ['WDM', 'WDM-WP']:
            df_sol_mt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Medium')]
            df_sol_lt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Long')]

            mt_tx.append(df_sol_mt['TX Cost'].values[0] if len(df_sol_mt) > 0 else 0)
            mt_mux.append(df_sol_mt['MUX Cost'].values[0] if len(df_sol_mt) > 0 else 0)
            lt_tx.append(df_sol_lt['TX Cost'].values[0] if len(df_sol_lt) > 0 else 0)
            lt_mux.append(df_sol_lt['MUX Cost'].values[0] if len(df_sol_lt) > 0 else 0)

        # P2MP e P2MP-WP (Best e Worst)
        for sol in ['P2MP', 'P2MP-WP']:
            for case in ['Best', 'Worst']:
                df_sol_mt = df_scenario[(df_scenario['Solution'] == sol) &
                                        (df_scenario['Case'] == case) &
                                        (df_scenario['Term'] == 'Medium')]
                df_sol_lt = df_scenario[(df_scenario['Solution'] == sol) &
                                        (df_scenario['Case'] == case) &
                                        (df_scenario['Term'] == 'Long')]

                mt_tx.append(df_sol_mt['TX Cost'].values[0] if len(df_sol_mt) > 0 else 0)
                mt_mux.append(df_sol_mt['MUX Cost'].values[0] if len(df_sol_mt) > 0 else 0)
                lt_tx.append(df_sol_lt['TX Cost'].values[0] if len(df_sol_lt) > 0 else 0)
                lt_mux.append(df_sol_lt['MUX Cost'].values[0] if len(df_sol_lt) > 0 else 0)

        # Plot
        colors_medium = ['#1f77b4', '#aec7e8']
        colors_long = ['#ff7f0e', '#ffbb78']

        # Medium term bars
        plt.bar(x_pos - width / 2, mt_tx, width, label='Transmission (MT)', color=colors_medium[0], edgecolor='black')
        plt.bar(x_pos - width / 2, mt_mux, width, bottom=mt_tx, label='Switching (MT)',
                color=colors_medium[1], edgecolor='black', hatch='//')

        # Long term bars
        plt.bar(x_pos + width / 2, lt_tx, width, label='Transmission (LT)', color=colors_long[0], edgecolor='black')
        plt.bar(x_pos + width / 2, lt_mux, width, bottom=lt_tx, label='Switching (LT)',
                color=colors_long[1], edgecolor='black', hatch='\\\\')

        plt.ylabel('CAPEX (Cost Units)')
        plt.xlabel('')
        plt.xticks(x_pos, x_labels, rotation=0)
        plt.xlim([-0.5, 5.5])
        plt.ylim([0, 350])
        if scenario == 'Rural':
            plt.legend()
        else:
            plt.legend().set_visible(False)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        plt.savefig(f'cost_comparison_v2_{scenario.lower().replace(" ", "_")}.pdf',
                    format='pdf', dpi=300, bbox_inches='tight')
        plt.show()

    # ENERGY COMPARISON V2
    for scenario in deployment_scenarios:
        plt.figure(figsize=(14, 8))

        # Filtra dati
        df_scenario = df_best_worst[
            (df_best_worst['Scenario'] == scenario) &
            df_best_worst['Solution'].isin(['WDM', 'WDM-WP', 'P2MP', 'P2MP-WP'])
            ]

        # Prepara labels
        x_labels = ['WDM', 'WDM-WP', 'P2MP\n(Best)', 'P2MP-WP\n(Best)', 'P2MP\n(Worst)', 'P2MP-WP\n(Worst)']
        x_pos = np.arange(len(x_labels))
        width = 0.35

        # Arrays per i dati
        mt_tx_energy = []
        mt_sw_energy = []
        lt_tx_energy = []
        lt_sw_energy = []

        # WDM e WDM-WP
        for sol in ['WDM', 'WDM-WP']:
            df_sol_mt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Medium')]
            df_sol_lt = df_scenario[(df_scenario['Solution'] == sol) & (df_scenario['Term'] == 'Long')]

            mt_tx_energy.append(df_sol_mt['TX Energy'].values[0] if len(df_sol_mt) > 0 else 0)
            mt_sw_energy.append(df_sol_mt['SW Energy'].values[0] if len(df_sol_mt) > 0 else 0)
            lt_tx_energy.append(df_sol_lt['TX Energy'].values[0] if len(df_sol_lt) > 0 else 0)
            lt_sw_energy.append(df_sol_lt['SW Energy'].values[0] if len(df_sol_lt) > 0 else 0)

        # P2MP e P2MP-WP (Best e Worst)
        for sol in ['P2MP', 'P2MP-WP']:
            for case in ['Best', 'Worst']:
                df_sol_mt = df_scenario[(df_scenario['Solution'] == sol) &
                                        (df_scenario['Case'] == case) &
                                        (df_scenario['Term'] == 'Medium')]
                df_sol_lt = df_scenario[(df_scenario['Solution'] == sol) &
                                        (df_scenario['Case'] == case) &
                                        (df_scenario['Term'] == 'Long')]

                mt_tx_energy.append(df_sol_mt['TX Energy'].values[0] if len(df_sol_mt) > 0 else 0)
                mt_sw_energy.append(df_sol_mt['SW Energy'].values[0] if len(df_sol_mt) > 0 else 0)
                lt_tx_energy.append(df_sol_lt['TX Energy'].values[0] if len(df_sol_lt) > 0 else 0)
                lt_sw_energy.append(df_sol_lt['SW Energy'].values[0] if len(df_sol_lt) > 0 else 0)

        # Plot
        colors_medium = ['#1f77b4', '#aec7e8']
        colors_long = ['#ff7f0e', '#ffbb78']

        # Medium term bars
        plt.bar(x_pos - width / 2, mt_tx_energy, width, label='Transmission (MT)', color=colors_medium[0], edgecolor='black')
        plt.bar(x_pos - width / 2, mt_sw_energy, width, bottom=mt_tx_energy, label='Switching (MT)',
                color=colors_medium[1], edgecolor='black', hatch='//')

        # Long term bars
        plt.bar(x_pos + width / 2, lt_tx_energy, width, label='Transmission (LT)', color=colors_long[0], edgecolor='black')
        plt.bar(x_pos + width / 2, lt_sw_energy, width, bottom=lt_tx_energy, label='Switching (LT)',
                color=colors_long[1], edgecolor='black', hatch='\\\\')

        plt.ylabel('Energy (MWh/year)')
        plt.xlabel('')
        plt.xticks(x_pos, x_labels, rotation=0)
        plt.xlim([-0.5, 5.5])
        plt.ylim([0, 120])
        if scenario == 'Rural':
            plt.legend()
        else:
            plt.legend().set_visible(False)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        plt.savefig(f'energy_comparison_v2_{scenario.lower().replace(" ", "_")}.pdf',
                    format='pdf', dpi=300, bbox_inches='tight')
        plt.show()

    print("\n=== BEST/WORST CASE ANALYSIS COMPLETED ===")
    print("Generated files:")
    print("- best_worst_case_analysis.csv")
    print("- cost_comparison_v1_*.pdf (4 files)")
    print("- energy_comparison_v1_*.pdf (4 files)")
    print("- cost_comparison_v2_*.pdf (4 files)")
    print("- energy_comparison_v2_*.pdf (4 files)")

print("\nBest/Worst Case Analysis completed!")

# ANALISI NUMERO DI SWITCH PER SOLUZIONE
print("\n=== SWITCH COUNT ANALYSIS ===")


def count_switches_in_network(T):
    """Conta il numero totale di switch nella rete per tipo"""
    switch_count = {
        'SWITCH_SMALL': 0,
        'SWITCH_MEDIUM': 0,
        'SWITCH_BIG': 0,
        'SWITCH_EXTRA_LARGE': 0
    }

    for node in T.nodes():
        for equipment in T.nodes[node]['network_equipment']:
            if 'SWITCH_SMALL' in equipment.equipment_type.name:
                switch_count['SWITCH_SMALL'] += 1
            elif 'SWITCH_MEDIUM' in equipment.equipment_type.name:
                switch_count['SWITCH_MEDIUM'] += 1
            elif 'SWITCH_BIG' in equipment.equipment_type.name:
                switch_count['SWITCH_BIG'] += 1
            elif 'SWITCH_EXTRA_LARGE' in equipment.equipment_type.name:
                switch_count['SWITCH_EXTRA_LARGE'] += 1

    return switch_count


# Raccogli dati sui switch
switch_results = []

for term in ['Medium', 'Long']:
    for scenario in deployment_scenarios:
        print(f"Counting switches for {scenario} - {term} term...")

        # P2P
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        soluzione_1_with_smallcellswitch(T, term)
        p2p_switches = count_switches_in_network(T)

        switch_results.append({
            'Solution': 'P2P',
            'Case': 'N/A',
            'Term': term,
            'Scenario': scenario,
            'Small': p2p_switches['SWITCH_SMALL'],
            'Medium': p2p_switches['SWITCH_MEDIUM'],
            'Big': p2p_switches['SWITCH_BIG'],
            'Extra Large': p2p_switches['SWITCH_EXTRA_LARGE'],
            'Total': sum(p2p_switches.values())
        })

        # WDM
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        soluzione_2_with_smallcellmux(T, term)
        wdm_switches = count_switches_in_network(T)

        switch_results.append({
            'Solution': 'WDM',
            'Case': 'N/A',
            'Term': term,
            'Scenario': scenario,
            'Small': wdm_switches['SWITCH_SMALL'],
            'Medium': wdm_switches['SWITCH_MEDIUM'],
            'Big': wdm_switches['SWITCH_BIG'],
            'Extra Large': wdm_switches['SWITCH_EXTRA_LARGE'],
            'Total': sum(wdm_switches.values())
        })

        # P2MP Best Case
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        update_xr_equipment_scenario(network_equipment_types, NetworkEquipmentTypeEnum, 'best')
        soluzione_3_with_smallcellaggr(T, term)
        p2mp_best_switches = count_switches_in_network(T)

        switch_results.append({
            'Solution': 'P2MP',
            'Case': 'Best',
            'Term': term,
            'Scenario': scenario,
            'Small': p2mp_best_switches['SWITCH_SMALL'],
            'Medium': p2mp_best_switches['SWITCH_MEDIUM'],
            'Big': p2mp_best_switches['SWITCH_BIG'],
            'Extra Large': p2mp_best_switches['SWITCH_EXTRA_LARGE'],
            'Total': sum(p2mp_best_switches.values())
        })

        # P2MP Worst Case
        T, T_m, A = create_geotype(scenario)
        deploy_radio_equipment(T, term, scenario)
        update_xr_equipment_scenario(network_equipment_types, NetworkEquipmentTypeEnum, 'worst')
        soluzione_3_with_smallcellaggr(T, term)
        p2mp_worst_switches = count_switches_in_network(T)

        switch_results.append({
            'Solution': 'P2MP',
            'Case': 'Worst',
            'Term': term,
            'Scenario': scenario,
            'Small': p2mp_worst_switches['SWITCH_SMALL'],
            'Medium': p2mp_worst_switches['SWITCH_MEDIUM'],
            'Big': p2mp_worst_switches['SWITCH_BIG'],
            'Extra Large': p2mp_worst_switches['SWITCH_EXTRA_LARGE'],
            'Total': sum(p2mp_worst_switches.values())
        })

# Converti in DataFrame
df_switches = pd.DataFrame(switch_results)

# PLOT 1: Numero totale di switch per scenario con P2MP best e worst
plt.rc('font', size=24)

for scenario in deployment_scenarios:
    plt.figure(figsize=(12, 7))

    df_scenario = df_switches[df_switches['Scenario'] == scenario]

    x_labels = ['P2P', 'WDM', 'P2MP\n(Best)', 'P2MP\n(Worst)']
    x_pos = np.arange(len(x_labels))
    width = 0.35

    # Medium Term
    mt_counts = []
    # P2P
    df_sol = df_scenario[(df_scenario['Solution'] == 'P2P') & (df_scenario['Term'] == 'Medium')]
    mt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # WDM
    df_sol = df_scenario[(df_scenario['Solution'] == 'WDM') & (df_scenario['Term'] == 'Medium')]
    mt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # P2MP Best
    df_sol = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                         (df_scenario['Case'] == 'Best') &
                         (df_scenario['Term'] == 'Medium')]
    mt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # P2MP Worst
    df_sol = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                         (df_scenario['Case'] == 'Worst') &
                         (df_scenario['Term'] == 'Medium')]
    mt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # Long Term
    lt_counts = []
    # P2P
    df_sol = df_scenario[(df_scenario['Solution'] == 'P2P') & (df_scenario['Term'] == 'Long')]
    lt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # WDM
    df_sol = df_scenario[(df_scenario['Solution'] == 'WDM') & (df_scenario['Term'] == 'Long')]
    lt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # P2MP Best
    df_sol = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                         (df_scenario['Case'] == 'Best') &
                         (df_scenario['Term'] == 'Long')]
    lt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # P2MP Worst
    df_sol = df_scenario[(df_scenario['Solution'] == 'P2MP') &
                         (df_scenario['Case'] == 'Worst') &
                         (df_scenario['Term'] == 'Long')]
    lt_counts.append(df_sol['Total'].values[0] if len(df_sol) > 0 else 0)

    # Plot
    plt.bar(x_pos - width / 2, mt_counts, width, label='Medium Term', color='#1f77b4', edgecolor='black')
    plt.bar(x_pos + width / 2, lt_counts, width, label='Long Term', color='#ff7f0e', edgecolor='black')

    plt.ylabel('Number of Switches')
    plt.xlabel('Solution')
    plt.title(f'Total Switch Count - {scenario}')
    plt.xticks(x_pos, x_labels)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    plt.savefig(f'switch_count_total_{scenario.lower().replace(" ", "_")}.pdf',
                format='pdf', dpi=300, bbox_inches='tight')
    plt.show()

# Salva i risultati
df_switches.to_csv('switch_count_analysis_with_best_worst.csv', index=False)
print("\nSwitch count data saved to 'switch_count_analysis_with_best_worst.csv'")