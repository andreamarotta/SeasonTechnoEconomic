import matplotlib.pyplot as plt
import networkx as nx

def create_dense_urban_geotype():
    # Definizione dei nodi con il tipo e le coordinate
    nodes = {
        0: {'type': 0, 'position': (0, 0)},       # Nodo root
        1: {'type': 1, 'position': (-199.5, 199.5)},  # Macro celle
        2: {'type': 1, 'position': (199.5, 199.5)},
        3: {'type': 1, 'position': (0, 0)},
        4: {'type': 1, 'position': (-199.5, -199.5)},
        5: {'type': 1, 'position': (199.5, -199.5)},
        6: {'type': 2, 'position': (-133, 332.5)},    # Small cells
        7: {'type': 2, 'position': (133, 332.5)},
        8: {'type': 2, 'position': (0, 266)},
        9: {'type': 2, 'position': (-199.5, 199.5)},
        10: {'type': 2, 'position': (199.5, 199.5)},
        11: {'type': 2, 'position': (-266, 133)},
        12: {'type': 2, 'position': (-133, 133)},
        13: {'type': 2, 'position': (0, 133)},
        14: {'type': 2, 'position': (133, 133)},
        15: {'type': 2, 'position': (-332.5, 0)},
        16: {'type': 2, 'position': (-133, 0)},
        17: {'type': 2, 'position': (0, 0)},
        18: {'type': 2, 'position': (133, 0)},
        19: {'type': 2, 'position': (332.5, 0)},
        20: {'type': 2, 'position': (266, -133)},
        21: {'type': 2, 'position': (133, -133)},
        22: {'type': 2, 'position': (266, 133)},
        23: {'type': 2, 'position': (-133, -133)},
        24: {'type': 2, 'position': (0, -133)},
        25: {'type': 2, 'position': (-266, -133)},
        26: {'type': 2, 'position': (-199.5, -199.5)},
        27: {'type': 2, 'position': (199.5, -199.5)},
        28: {'type': 2, 'position': (0, -266)},
        29: {'type': 2, 'position': (133, -332.5)},
        30: {'type': 2, 'position': (-133, -332.5)}
    }

    # Funzione per calcolare la distanza di Manhattan tra due punti
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # Creazione del grafo con archi Manhattan
    G = nx.Graph()

    # Aggiunta dei nodi al grafo
    for key, value in nodes.items():
        G.add_node(key, **value, id=key)

    # Aggiunta degli archi Manhattan al grafo
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            p1 = nodes[i]['position']
            p2 = nodes[j]['position']
            distance = manhattan_distance(p1, p2)
            edges.append((i, j, distance))

    G.add_weighted_edges_from(edges)

    # Creazione del minimo albero coprente
    T = nx.minimum_spanning_tree(G)

    # Copia del grafo T per creare T_m
    T_m = T.copy()

    # Aggiunta dei nodi di tipo 4 (corner nodes) nel grafo T_m
    for (u, v) in list(T_m.edges()):
        pos_u = T_m.nodes[u]['position']
        pos_v = T_m.nodes[v]['position']

        # Se necessario, aggiungi un nodo di tipo 4 per creare un angolo
        if pos_u[0] != pos_v[0] and pos_u[1] != pos_v[1]:
            corner = (pos_u[0], pos_v[1])  # Crea un angolo
            corner_id = len(T_m.nodes)
            T_m.add_node(corner_id, type=4, position=corner, id=corner_id)  # Aggiungi il nodo di tipo 4
            T_m.add_edge(u, corner_id, weight=manhattan_distance(pos_u, corner))
            T_m.add_edge(corner_id, v, weight=manhattan_distance(corner, pos_v))
            T_m.remove_edge(u, v)  # Rimuovi l'arco diagonale

    return T, T_m


def create_urban_geotype():
    # Definizione dei nodi con il tipo e le coordinate
    nodes = {
        0: {'type': 0, 'position': (0, 0)},       # Nodo root

        1: {'type': 1, 'position': (-600, 600)},  # Macro celle
        2: {'type': 1, 'position': (600, 600)},
        3: {'type': 1, 'position': (0, 400)},
        4: {'type': 1, 'position': (-400, 0)},
        5: {'type': 1, 'position': (0, 0)},
        6: {'type': 1, 'position': (400, 0)},
        7: {'type': 1, 'position': (0, -400)},
        8: {'type': 1, 'position': (-600, -600)},
        9: {'type': 1, 'position': (600, -600)},

        10: {'type': 2, 'position': (-600, 600)},    # Small cells
        11: {'type': 2, 'position': (-200, 600)},
        12: {'type': 2, 'position': (200, 600)},
        13: {'type': 2, 'position': (600, 600)},

        14: {'type': 2, 'position': (-400, 400)},
        15: {'type': 2, 'position': (0, 400)},
        16: {'type': 2, 'position': (400, 400)},

        17: {'type': 2, 'position': (-600, 200)},
        18: {'type': 2, 'position': (-200, 200)},
        19: {'type': 2, 'position': (200, 200)},
        20: {'type': 2, 'position': (600, 200)},

        21: {'type': 2, 'position': (-400, 0)},
        22: {'type': 2, 'position': (0, 0)},
        23: {'type': 2, 'position': (400, 0)},

        24: {'type': 2, 'position': (-600, -200)},
        25: {'type': 2, 'position': (-200, -200)},
        26: {'type': 2, 'position': (200, -200)},
        27: {'type': 2, 'position': (600, -200)},

        28: {'type': 2, 'position': (-400, -400)},
        29: {'type': 2, 'position': (0, -400)},
        30: {'type': 2, 'position': (400, -400)},

        31: {'type': 2, 'position': (-600, -600)},
        32: {'type': 2, 'position': (-200, -600)},
        33: {'type': 2, 'position': (200, -600)},
        34: {'type': 2, 'position': (600, -600)},
    }

    # Funzione per calcolare la distanza di Manhattan tra due punti
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # Creazione del grafo con archi Manhattan
    G = nx.Graph()

    # Aggiunta dei nodi al grafo
    for key, value in nodes.items():
        G.add_node(key, **value, id=key)

    # Aggiunta degli archi Manhattan al grafo
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            p1 = nodes[i]['position']
            p2 = nodes[j]['position']
            distance = manhattan_distance(p1, p2)
            edges.append((i, j, distance))

    G.add_weighted_edges_from(edges)

    # Creazione del minimo albero coprente
    T = nx.minimum_spanning_tree(G)

    # Copia del grafo T per creare T_m
    T_m = T.copy()

    # Aggiunta dei nodi di tipo 4 (corner nodes) nel grafo T_m
    for (u, v) in list(T_m.edges()):
        pos_u = T_m.nodes[u]['position']
        pos_v = T_m.nodes[v]['position']

        # Se necessario, aggiungi un nodo di tipo 4 per creare un angolo
        if pos_u[0] != pos_v[0] and pos_u[1] != pos_v[1]:
            corner = (pos_u[0], pos_v[1])  # Crea un angolo
            corner_id = len(T_m.nodes)
            T_m.add_node(corner_id, type=4, position=corner, id=corner_id)  # Aggiungi il nodo di tipo 4
            T_m.add_edge(u, corner_id, weight=manhattan_distance(pos_u, corner))
            T_m.add_edge(corner_id, v, weight=manhattan_distance(corner, pos_v))
            T_m.remove_edge(u, v)  # Rimuovi l'arco diagonale

    return T, T_m



def create_suburban_geotype():
    # Definizione dei nodi con il tipo e le coordinate
    nodes = {
        0: {'type': 0, 'position': (0, 0)},       # Nodo root

        1: {'type': 1, 'position': (-1066, 1066)},  # Macro celle
        2: {'type': 1, 'position': (0, 1066)},
        3: {'type': 1, 'position': (1066, 1066)},
        4: {'type': 1, 'position': (-1066, 0)},
        5: {'type': 1, 'position': (0, 0)},
        6: {'type': 1, 'position': (1066, 0)},
        7: {'type': 1, 'position': (-1066, -1066)},
        8: {'type': 1, 'position': (0, -1066)},
        9: {'type': 1, 'position': (1066, -1066)},

        10: {'type': 2, 'position': (-1066, 1066)},  # Small celle
        11: {'type': 2, 'position': (0, 1066)},
        12: {'type': 2, 'position': (1066, 1066)},

        13: {'type': 2, 'position': (-533, 533)},
        14: {'type': 2, 'position': (0, 533)},
        15: {'type': 2, 'position': (533, 533)},

        16: {'type': 2, 'position': (-1066, 0)},
        17: {'type': 2, 'position': (-533, 0)},
        18: {'type': 2, 'position': (0, 0)},
        19: {'type': 2, 'position': (533, 0)},
        20: {'type': 2, 'position': (1066, 0)},

        21: {'type': 2, 'position': (-533, -533)},
        22: {'type': 2, 'position': (0, -533)},
        23: {'type': 2, 'position': (533, -533)},

        24: {'type': 2, 'position': (-1066, -1066)},
        25: {'type': 2, 'position': (0, -1066)},
        26: {'type': 2, 'position': (1066, -1066)},



    }

    # Funzione per calcolare la distanza di Manhattan tra due punti
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # Creazione del grafo con archi Manhattan
    G = nx.Graph()

    # Aggiunta dei nodi al grafo
    for key, value in nodes.items():
        G.add_node(key, **value, id=key)

    # Aggiunta degli archi Manhattan al grafo
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            p1 = nodes[i]['position']
            p2 = nodes[j]['position']
            distance = manhattan_distance(p1, p2)
            edges.append((i, j, distance))

    G.add_weighted_edges_from(edges)

    # Creazione del minimo albero coprente
    T = nx.minimum_spanning_tree(G)

    # Copia del grafo T per creare T_m
    T_m = T.copy()

    # Aggiunta dei nodi di tipo 4 (corner nodes) nel grafo T_m
    for (u, v) in list(T_m.edges()):
        pos_u = T_m.nodes[u]['position']
        pos_v = T_m.nodes[v]['position']

        # Se necessario, aggiungi un nodo di tipo 4 per creare un angolo
        if pos_u[0] != pos_v[0] and pos_u[1] != pos_v[1]:
            corner = (pos_u[0], pos_v[1])  # Crea un angolo
            corner_id = len(T_m.nodes)
            T_m.add_node(corner_id, type=4, position=corner, id=corner_id)  # Aggiungi il nodo di tipo 4
            T_m.add_edge(u, corner_id, weight=manhattan_distance(pos_u, corner))
            T_m.add_edge(corner_id, v, weight=manhattan_distance(corner, pos_v))
            T_m.remove_edge(u, v)  # Rimuovi l'arco diagonale

    return T, T_m


def create_rural_geotype():
    # Definizione dei nodi con il tipo e le coordinate
    nodes = {
        0: {'type': 0, 'position': (0, 0)},       # Nodo root

        1: {'type': 1, 'position': (-3200, 3200)},  # Macro celle
        2: {'type': 1, 'position': (3200, 3200)},
        3: {'type': 1, 'position': (0, 0)},
        4: {'type': 1, 'position': (-3200, -3200)},
        5: {'type': 1, 'position': (3200, -3200)},


        6: {'type': 2, 'position': (0, 533)},  # Small celle
        7: {'type': 2, 'position': (-533, 0)},
        8: {'type': 2, 'position': (0, 0)},
        9: {'type': 2, 'position': (533, 0)},
        10: {'type': 2, 'position': (0, -533)},

    }

    # Funzione per calcolare la distanza di Manhattan tra due punti
    def manhattan_distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # Creazione del grafo con archi Manhattan
    G = nx.Graph()

    # Aggiunta dei nodi al grafo
    for key, value in nodes.items():
        G.add_node(key, **value, id=key)

    # Aggiunta degli archi Manhattan al grafo
    edges = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            p1 = nodes[i]['position']
            p2 = nodes[j]['position']
            distance = manhattan_distance(p1, p2)
            edges.append((i, j, distance))

    G.add_weighted_edges_from(edges)

    # Creazione del minimo albero coprente
    T = nx.minimum_spanning_tree(G)

    # Copia del grafo T per creare T_m
    T_m = T.copy()

    # Aggiunta dei nodi di tipo 4 (corner nodes) nel grafo T_m
    for (u, v) in list(T_m.edges()):
        pos_u = T_m.nodes[u]['position']
        pos_v = T_m.nodes[v]['position']

        # Se necessario, aggiungi un nodo di tipo 4 per creare un angolo
        if pos_u[0] != pos_v[0] and pos_u[1] != pos_v[1]:
            corner = (pos_u[0], pos_v[1])  # Crea un angolo
            corner_id = len(T_m.nodes)
            T_m.add_node(corner_id, type=4, position=corner, id=corner_id)  # Aggiungi il nodo di tipo 4
            T_m.add_edge(u, corner_id, weight=manhattan_distance(pos_u, corner))
            T_m.add_edge(corner_id, v, weight=manhattan_distance(corner, pos_v))
            T_m.remove_edge(u, v)  # Rimuovi l'arco diagonale

    return T, T_m

def plot_graph(T, title="Graph"):
    # Insieme per tenere traccia delle etichette già utilizzate
    used_labels = set()

    # Plotta i nodi e gli archi del grafo
    plt.figure(figsize=(10, 10))

    # Plotta gli archi
    for (u, v) in T.edges():
        pos_u = T.nodes[u]['position']
        pos_v = T.nodes[v]['position']
        plt.plot([pos_u[0], pos_v[0]], [pos_u[1], pos_v[1]], 'k-', lw=1)

    # Plotta i nodi
    for key, value in T.nodes(data=True):
        node_type = value['type']
        position = value['position']

        if node_type == 0:
            plt.scatter(position[0], position[1], color='green', s=300, edgecolors='black', marker='s', label='Root Node' if 'Root Node' not in used_labels else "")
            used_labels.add('Root Node')
            plt.text(position[0], position[1], 'Root', fontsize=12, ha='center', va='center', color='white', fontweight='bold')
        elif node_type == 1:
            plt.scatter(position[0], position[1], color='yellow', s=200, edgecolors='black', marker='^', label='Macro Cell' if 'Macro Cell' not in used_labels else "")
            used_labels.add('Macro Cell')
            plt.text(position[0], position[1], str(key), fontsize=12, ha='center', va='center', color='black', fontweight='bold')
        elif node_type == 2:
            plt.scatter(position[0], position[1], color='purple', s=100, edgecolors='black', marker='o', label='Small Cell' if 'Small Cell' not in used_labels else "")
            used_labels.add('Small Cell')
            plt.text(position[0], position[1], str(key), fontsize=10, ha='center', va='center', color='white', fontweight='bold')
        elif node_type == 4:
            plt.scatter(position[0], position[1], color='red', s=150, marker='x', label='Corner Node' if 'Corner Node' not in used_labels else "")
            used_labels.add('Corner Node')
            plt.text(position[0], position[1], 'C'+str(key), fontsize=10, ha='center', va='center', color='black', fontweight='bold')

    # Configurazione del grafico
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(True)
    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    plt.legend()
    plt.title(title)
    plt.show()


def create_geotype(geotype):
    """
    Crea i grafi T e T_m basati sul tipo di area geografica.

    Parametri:
    geotype (str): Tipo di area geografica ("Dense Urban", "Urban", "Suburban", "Rural").

    Ritorna:
    T (networkx.Graph): Grafo prima dell'aggiunta dei nodi corner.
    T_m (networkx.Graph): Grafo dopo l'aggiunta dei nodi corner.
    A (float): Area in km2.
    """
    if geotype == "Dense Urban":
        T, T_m = create_dense_urban_geotype()
        return T, T_m, 0.8*0.8
    elif geotype == "Urban":
        T, T_m = create_urban_geotype()
        return T, T_m, 1.6*1.6
    elif geotype == "Suburban":
        T, T_m = create_suburban_geotype()
        return T, T_m, 3.2*3.2
    elif geotype == "Rural":
        T, T_m = create_rural_geotype()
        return T, T_m, 12.8*12.8
    else:
        raise ValueError("Geotype non valido. Scegli tra 'Dense Urban', 'Urban', 'Suburban', 'Rural'.")

'''
# Esempio di utilizzo della funzione
T, T_m = create_dense_urban_geotype()

# Plotta i due grafi separatamente
plot_graph(T, title="Graph T (Prima dell'aggiunta dei nodi corner)")
plot_graph(T_m, title="Graph T_m (Dopo l'aggiunta dei nodi corner)")

# Esempio di utilizzo della funzione
T, T_m = create_urban_geotype()

# Plotta i due grafi separatamente
plot_graph(T, title="Graph T (Prima dell'aggiunta dei nodi corner)")
plot_graph(T_m, title="Graph T_m (Dopo l'aggiunta dei nodi corner)")

# Esempio di utilizzo della funzione
T, T_m = create_suburban_geotype()

# Plotta i due grafi separatamente
plot_graph(T, title="Graph T (Prima dell'aggiunta dei nodi corner)")
plot_graph(T_m, title="Graph T_m (Dopo l'aggiunta dei nodi corner)")

# Esempio di utilizzo della funzione
T, T_m = create_rural_geotype()

# Plotta i due grafi separatamente
plot_graph(T, title="Graph T (Prima dell'aggiunta dei nodi corner)")
plot_graph(T_m, title="Graph T_m (Dopo l'aggiunta dei nodi corner)")
'''