import os
import json
from typing import Dict, Any
import networkx as nx
import matplotlib.pyplot as plt
from langgraph.graph import StateGraph

def visualize_graph(graph: StateGraph, output_path: str = "output/workflow_graph.png"):
    """
    Visualize a LangGraph StateGraph and save it as an image
    
    Args:
        graph: The compiled LangGraph StateGraph
        output_path: Path to save the visualization
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Get the graph data
    graph_data = graph.get_graph()
    
    # Create a NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes
    for node in graph_data["nodes"]:
        G.add_node(node)
    
    # Add edges
    for edge in graph_data["edges"]:
        G.add_edge(edge["source"], edge["target"])
    
    # Create the visualization
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue", alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, arrowsize=20)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
    
    # Save the visualization
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Graph visualization saved to {output_path}")

def export_graph_json(graph: StateGraph, output_path: str = "output/workflow_graph.json"):
    """
    Export the LangGraph StateGraph as a JSON file for visualization with external tools
    
    Args:
        graph: The compiled LangGraph StateGraph
        output_path: Path to save the JSON file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Get the graph data
    graph_data = graph.get_graph()
    
    # Save as JSON
    with open(output_path, "w") as f:
        json.dump(graph_data, f, indent=2)
    
    print(f"Graph data exported to {output_path}")

def track_execution(state_history: Dict[str, Any], output_path: str = "output/execution_history.json"):
    """
    Save the execution history of a LangGraph workflow
    
    Args:
        state_history: Dictionary of states at each step of execution
        output_path: Path to save the execution history
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert any non-serializable objects to strings
    serializable_history = {}
    for step, state in state_history.items():
        serializable_state = {}
        for key, value in state.items():
            if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                serializable_state[key] = value
            else:
                serializable_state[key] = str(value)
        serializable_history[step] = serializable_state
    
    # Save as JSON
    with open(output_path, "w") as f:
        json.dump(serializable_history, f, indent=2)
    
    print(f"Execution history saved to {output_path}") 