"""
Species Configuration
---------------------

Defines available species and their corresponding data files.
This module provides a central configuration for multi-species support.
"""

from pathlib import Path
from typing import List, Dict, Tuple
import json
import networkx as nx

# Define available species
# The default dataset is treated as a general/all species dataset
AVAILABLE_SPECIES = [
    {"value": "all", "label": "All Species"},
    {"value": "arabidopsis", "label": "Arabidopsis"},
    {"value": "tomato", "label": "Tomato"},
    {"value": "rice", "label": "Rice"},
]


def get_species_data_paths(species: str, data_dir: Path) -> Tuple[Path, Path]:
    """
    Get the paths to the nodes and edges JSON files for a given species.
    
    Args:
        species: The species identifier (e.g., "arabidopsis", "tomato", or "all")
        data_dir: The directory containing the data files
        
    Returns:
        Tuple of (nodes_path, edges_path)
    """
    if species == "all" or species is None:
        # Use the default dataset files
        nodes_path = data_dir / "graph_nodes_dataset.json"
        edges_path = data_dir / "graph_edges_dataset.json"
    else:
        # Use species-specific files
        nodes_path = data_dir / f"graph_nodes_{species}.json"
        edges_path = data_dir / f"graph_edges_{species}.json"
    
    return nodes_path, edges_path


def get_available_species_from_data(data_dir: Path) -> List[Dict[str, str]]:
    """
    Dynamically discover available species based on data files present in the directory.
    Falls back to AVAILABLE_SPECIES if no species-specific files are found.
    
    Args:
        data_dir: The directory containing the data files
        
    Returns:
        List of species dictionaries with 'value' and 'label' keys
    """
    species_list = [{"value": "all", "label": "All Species"}]
    
    # Check for species-specific node files
    for file_path in data_dir.glob("graph_nodes_*.json"):
        # Extract species name from filename
        filename = file_path.stem
        if filename == "graph_nodes_dataset":
            continue
        
        species_name = filename.replace("graph_nodes_", "")
        # Check if corresponding edges file exists
        edges_file = data_dir / f"graph_edges_{species_name}.json"
        if edges_file.exists():
            # Capitalize first letter for display
            species_label = species_name.capitalize()
            species_list.append({"value": species_name, "label": species_label})
    
    # If no species-specific files found, return the predefined list
    if len(species_list) == 1:
        return AVAILABLE_SPECIES
    
    return species_list


def species_files_exist(species: str, data_dir: Path) -> bool:
    """
    Check if data files exist for the given species.
    
    Args:
        species: The species identifier
        data_dir: The directory containing the data files
        
    Returns:
        True if both nodes and edges files exist, False otherwise
    """
    nodes_path, edges_path = get_species_data_paths(species, data_dir)
    return nodes_path.exists() and edges_path.exists()
