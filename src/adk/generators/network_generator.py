from typing import Dict, List, cast

from adk.type_aliases import InstructionType, NetworkConfigType, LinkType, NodeType, DijkstraNode


class FullyConnectedNetworkGenerator:
    NOISE_DEPOLARISE = 'Depolarise'
    NOISE_BITFLIP = 'Bitflip'
    NOISE_NONE = 'NoNoise'

    def __init__(self) -> None:
        self.__channel_mapping: Dict[str, List[str]] = {}

    @staticmethod
    def _dijkstra(all_neighbours: Dict[str, Dict[str, LinkType]], start_node: str) -> Dict[str, DijkstraNode]:
        """Find al optimal paths from particular start node to all other nodes.

        For a given network, determines the optimal paths between a start_node and all other nodes in a network, based
        on the (highest) effective fidelity over the entire link. A mapping between the new direct path and the list of
        used original paths is also calculated.

        Returns:
            Dictionary with node names as key and a DijkstraNode as value.
        """
        dijkstra: Dict[str, DijkstraNode] = {
            node: {
                "effective_fidelity": 0,
                "channels": [],
                "final": False
            } for node in all_neighbours}

        # Set fidelity for starting node to 1
        dijkstra[start_node]["effective_fidelity"] = 1

        # Take a subset of nodes that do not yet have a final fidelity value
        temporary_labeled = {node: properties for node, properties in dijkstra.items() if not properties['final']}

        while temporary_labeled:
            # Take node with highest effective fidelity as current node
            current_node = max(temporary_labeled.items(), key=lambda l: l[1]['effective_fidelity'])[0]
            dijkstra[current_node]["final"] = True

            # Find neighbours of current node in temporary subset
            neighbours = [neighbour for neighbour in all_neighbours[current_node].items()
                          if neighbour[0] in temporary_labeled]

            for neighbour, neighbour_link in neighbours:
                current_fidelity = dijkstra[neighbour]["effective_fidelity"]
                alternative_fidelity = 0.0

                # If neighbour is reachable from starting node through current node, calculate alternative fidelity
                if dijkstra[current_node]["effective_fidelity"] > 0:
                    alternative_fidelity = combined_fidelity(dijkstra[current_node]["effective_fidelity"],
                                                             cast(float, neighbour_link['fidelity']))

                # If alternative is better, replace fidelity / route from starting node
                if alternative_fidelity > current_fidelity:
                    dijkstra[neighbour]["effective_fidelity"] = alternative_fidelity
                    dijkstra[neighbour]["channels"] = \
                        dijkstra[current_node]["channels"] + cast(List[str], [neighbour_link['name']])

            temporary_labeled = {node: properties for node, properties in dijkstra.items() if not properties['final']}

        return dijkstra

    @staticmethod
    def _get_all_neighbours(network: NetworkConfigType) -> Dict[str, Dict[str, LinkType]]:
        """Generate dictionary with nodes as key and a dictionary with neighbour node and link between them as value."""
        neighbours: Dict[str, Dict[str, LinkType]] = {}
        nodes: List[NodeType] = cast(List[NodeType], network['nodes'])
        for node in nodes:
            neighbours[cast(str, node['name'])] = {}

        links: List[LinkType] = cast(List[LinkType], network['links'])
        for link in links:
            neighbours[cast(str, link['node_name1'])][cast(str, link['node_name2'])] = link
            neighbours[cast(str, link['node_name2'])][cast(str, link['node_name1'])] = link
        return neighbours

    @staticmethod
    def _get_overall_noise_type(noise_list: List[str]) -> str:
        if FullyConnectedNetworkGenerator.NOISE_DEPOLARISE in noise_list:
            return FullyConnectedNetworkGenerator.NOISE_DEPOLARISE
        if FullyConnectedNetworkGenerator.NOISE_BITFLIP in noise_list:
            return FullyConnectedNetworkGenerator.NOISE_BITFLIP
        return FullyConnectedNetworkGenerator.NOISE_NONE

    def generate(self, original_network: NetworkConfigType, role_mapping: Dict[str, str]) -> NetworkConfigType:
        """Generate a fully connected network based on original network and role mapping.

        Returns:
            A fully connected network dictionary with nodes and (direct) links.
        """
        # Clear channel mapping
        self.__channel_mapping = {}
        # Filter nodes from original network present in role_mapping
        original_nodes = cast(List[NodeType], original_network['nodes'])
        nodes: List[NodeType] = [node for node in original_nodes if node['name'] in role_mapping.values()]

        # Generate dictionary with nodes as key and a dict with neighbour and link as value
        all_neighbours = FullyConnectedNetworkGenerator._get_all_neighbours(original_network)

        # For all possible combinations of two nodes, find optimal path
        links: List[LinkType] = []
        for node1_index in range(len(nodes[:-1])):
            node1 = cast(str, nodes[node1_index]['name'])

            # Run Dijkstra algorithm for this node as starting node
            dijkstra = FullyConnectedNetworkGenerator._dijkstra(all_neighbours, node1)

            # Generate list of links / effective fidelity for all other nodes
            for node2_index in range(node1_index+1, len(nodes)):
                node2 = cast(str, nodes[node2_index]['name'])
                effective_fidelity = dijkstra[node2]["effective_fidelity"]

                # Only add link if there is an actual link between the two nodes
                if effective_fidelity > 0:
                    new_link = f"{node1}-{node2}"
                    self.__channel_mapping[new_link] = dijkstra[node2]["channels"]
                    original_links = cast(List[LinkType], original_network['links'])
                    links.append({
                        "name": new_link,
                        "node_name1": node1,
                        "node_name2": node2,
                        # Worst noise type of used links is taken as the noise type for effective link
                        "noise_type": FullyConnectedNetworkGenerator._get_overall_noise_type(
                            [cast(str, link['noise_type']) for link in original_links
                             if link['name'] in dijkstra[node2]["channels"]]),
                        # Effective fidelity is set to zero if it drops below 1/2
                        "fidelity": round(effective_fidelity, 4) if effective_fidelity >= 0.5 else 0
                    })

        # Check if the generated network is indeed fully connected
        if len(links) != len(nodes)*(len(nodes)-1)/2:
            raise Warning("Generated network is not fully connected.")

        return {
            "nodes": nodes,
            "links": links,
        }

    def convert(self, instructions: List[InstructionType]) -> None:
        """In-place update of channels entry to mapped channels."""
        for idx, _ in enumerate(instructions):
            if "channels" in instructions[idx]:
                instructions[idx]["channels"] = self.__channel_mapping[instructions[idx]["channels"][0]]


def combined_fidelity(f1: float, f2: float) -> float:
    """Calculate effective fidelity over two combined links."""
    f12 = f1 * f2 + (1 - f1) * (1 - f2) / 3
    return f12
