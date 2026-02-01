# Data Directory - Multi-Species Graph Support

This directory contains graph data files for the Text2Trait application. The application supports multiple species through a flexible file naming convention with **layered visualization** when multiple species are loaded.

## File Naming Convention

Species-specific graph data should follow this naming pattern using **NCBI Taxonomy IDs**:

```
graph_nodes_{taxon_id}.json
graph_edges_{taxon_id}.json
```

### Examples

- **Arabidopsis thaliana** (NCBI Taxon ID: 3702)
  - `graph_nodes_3702.json`
  - `graph_edges_3702.json`

- **Solanum lycopersicum** (Tomato, NCBI Taxon ID: 4081)
  - `graph_nodes_4081.json`
  - `graph_edges_4081.json`

- **Oryza sativa** (Rice, NCBI Taxon ID: 4530)
  - `graph_nodes_4530.json`
  - `graph_edges_4530.json`

## Default Dataset

The files `graph_nodes_dataset.json` and `graph_edges_dataset.json` serve as the default "All Species" dataset and are always available.

## Multi-Species Layered Visualization

When users select **"All Species"** on the home page and navigate to results, the application:

1. **Automatically discovers** all species-specific data files in this directory
2. **Loads and merges** graphs from all available species
3. **Tags each node and edge** with its species of origin
4. **Displays species layer controls** with checkboxes for each species
5. **Allows toggling** individual species layers on/off in real-time
6. **Uses color-coded indicators** (● bullets) to distinguish between species

### Features:
- **Real-time filtering**: Toggle species visibility without reloading the page
- **Color coordination**: Each species gets a unique color for easy identification
- **Flexible selection**: View all species together or focus on specific ones
- **No conflicts**: Species-specific node IDs are prefixed to avoid collisions

## Finding NCBI Taxonomy IDs

To find the NCBI Taxonomy ID for your species:

1. Visit the [NCBI Taxonomy Browser](https://www.ncbi.nlm.nih.gov/taxonomy)
2. Search for your species name (e.g., "Arabidopsis thaliana")
3. The Taxonomy ID will be displayed in the result (e.g., 3702)

## Adding a New Species

To add data for a new species:

1. **Create the data files** with the appropriate taxon ID:
   ```
   graph_nodes_{taxon_id}.json
   graph_edges_{taxon_id}.json
   ```

2. **Update the species configuration** (optional but recommended):
   Edit `text2trait_forntend_app/src/utils/species_config.py` and add an entry to `SPECIES_TAXONOMY_MAP`:
   
   ```python
   SPECIES_TAXONOMY_MAP = {
       "3702": {
           "scientific_name": "Arabidopsis thaliana",
           "common_name": "Arabidopsis"
       },
       "YOUR_TAXON_ID": {
           "scientific_name": "Scientific Name Here",
           "common_name": "Common Name Here"
       },
       # ... other species
   }
   ```

3. **Restart the application** - The new species will be automatically discovered and:
   - Added to the species dropdown on the home page
   - Included in the "All Species" multi-layer visualization
   - Assigned a unique color for layer identification

## File Format

Both node and edge files follow the same JSON structure as the default dataset.

### Nodes File Format
```json
[
  {
    "id": "N1",
    "label": "Gene",
    "text": "GENE_NAME",
    "source": "https://doi.org/..."
  },
  ...
]
```

### Edges File Format
```json
[
  {
    "type": "INFLUENCES",
    "source": "N1",
    "target": "N2"
  },
  ...
]
```

## Auto-Discovery

The application automatically discovers available species by scanning for files matching the naming pattern. If a species is not listed in `SPECIES_TAXONOMY_MAP`, it will still appear in the dropdown as "Species {taxon_id}".

## Benefits of Using NCBI Taxonomy IDs

1. **Standardization**: Universally recognized identifiers
2. **No ambiguity**: Unique IDs prevent naming conflicts
3. **File-system friendly**: No spaces or special characters
4. **Extensibility**: Easy to add new species without code changes
5. **Interoperability**: Can be linked to other biological databases
6. **Multi-species support**: Enables layered visualization across species
