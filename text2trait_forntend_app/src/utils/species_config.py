"""
Species Configuration
---------------------

Defines available species and their corresponding data files.
This module provides a central configuration for multi-species support.

Species files should be named using NCBI taxonomy IDs:
- graph_nodes_{taxon_id}.json
- graph_edges_{taxon_id}.json

For example:
- graph_nodes_3702.json and graph_edges_3702.json for Arabidopsis thaliana (taxon ID: 3702)
- graph_nodes_4081.json and graph_edges_4081.json for Solanum lycopersicum (Tomato, taxon ID: 4081)
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import networkx as nx

# Mapping of NCBI taxonomy IDs to species information
# This provides a fallback when files follow naming conventions but aren't auto-discovered
SPECIES_TAXONOMY_MAP = {
    "3702": {
        "scientific_name": "Arabidopsis thaliana",
        "common_name": "Arabidopsis"
    },
    "4081": {
        "scientific_name": "Solanum lycopersicum",
        "common_name": "Tomato"
    },
    "4530": {
        "scientific_name": "Oryza sativa",
        "common_name": "Rice"
    },
    "3880": {
        "scientific_name": "Medicago truncatula",
        "common_name": "Barrel medic"
    },
}

# Define available species with their NCBI taxonomy IDs
# The default dataset is treated as a general/all species dataset
AVAILABLE_SPECIES = [
    {"value": "all", "label": "All Species"},
    {"value": "3702", "label": "Arabidopsis thaliana"},
    {"value": "4081", "label": "Solanum lycopersicum (Tomato)"},
    {"value": "4530", "label": "Oryza sativa (Rice)"},
]


def get_species_data_paths(species: str, data_dir: Path) -> Tuple[Path, Path]:
    """
    Get the paths to the nodes and edges JSON files for a given species.
    
    Args:
        species: The species identifier (NCBI taxon ID like "3702", or "all")
        data_dir: The directory containing the data files
        
    Returns:
        Tuple of (nodes_path, edges_path)
        
    Examples:
        >>> get_species_data_paths("3702", Path("data"))
        (Path("data/graph_nodes_3702.json"), Path("data/graph_edges_3702.json"))
        
        >>> get_species_data_paths("all", Path("data"))
        (Path("data/graph_nodes_dataset.json"), Path("data/graph_edges_dataset.json"))
    """
    if species == "all" or species is None:
        # Use the default dataset files
        nodes_path = data_dir / "graph_nodes_dataset.json"
        edges_path = data_dir / "graph_edges_dataset.json"
    else:
        # Use species-specific files with NCBI taxon ID
        nodes_path = data_dir / f"graph_nodes_{species}.json"
        edges_path = data_dir / f"graph_edges_{species}.json"
    
    return nodes_path, edges_path


def get_available_species_from_data(data_dir: Path) -> List[Dict[str, str]]:
    """
    Dynamically discover available species based on data files present in the directory.
    Falls back to AVAILABLE_SPECIES if no species-specific files are found.
    
    Files should follow the naming convention:
    - graph_nodes_{taxon_id}.json
    - graph_edges_{taxon_id}.json
    
    Where {taxon_id} is the NCBI taxonomy ID (e.g., 3702 for Arabidopsis thaliana)
    
    Args:
        data_dir: The directory containing the data files
        
    Returns:
        List of species dictionaries with 'value' and 'label' keys
    """
    species_list = [{"value": "all", "label": "All Species"}]
    
    # Check for species-specific node files
    for file_path in data_dir.glob("graph_nodes_*.json"):
        # Extract species identifier from filename
        filename = file_path.stem
        if filename == "graph_nodes_dataset":
            continue
        
        taxon_id = filename.replace("graph_nodes_", "")
        
        # Check if corresponding edges file exists
        edges_file = data_dir / f"graph_edges_{taxon_id}.json"
        if edges_file.exists():
            # Try to get a friendly label from the taxonomy map
            if taxon_id in SPECIES_TAXONOMY_MAP:
                species_info = SPECIES_TAXONOMY_MAP[taxon_id]
                scientific_name = species_info["scientific_name"]
                common_name = species_info.get("common_name", "")
                if common_name:
                    label = f"{scientific_name} ({common_name})"
                else:
                    label = scientific_name
            else:
                # Fallback to taxon ID if not in map
                label = f"Species {taxon_id}"
            
            species_list.append({"value": taxon_id, "label": label})
    
    # If no species-specific files found, return the predefined list
    if len(species_list) == 1:
        return AVAILABLE_SPECIES
    
    return species_list


def get_species_label(taxon_id: str) -> str:
    """
    Get a human-readable label for a species given its NCBI taxon ID.
    
    Args:
        taxon_id: The NCBI taxonomy ID
        
    Returns:
        Human-readable species label
    """
    if taxon_id == "all":
        return "All Species"
    
    if taxon_id in SPECIES_TAXONOMY_MAP:
        species_info = SPECIES_TAXONOMY_MAP[taxon_id]
        scientific_name = species_info["scientific_name"]
        common_name = species_info.get("common_name", "")
        if common_name:
            return f"{scientific_name} ({common_name})"
        return scientific_name
    
    return f"Species {taxon_id}"


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
