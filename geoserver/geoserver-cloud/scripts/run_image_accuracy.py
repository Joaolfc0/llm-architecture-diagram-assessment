import sys
from pathlib import Path

# Add project root to path (3 levels up: scripts -> geoserver-cloud -> geoserver -> root)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from evaluate_architecture import evaluate_architecture, save_evaluation_result

# Diagram is in the same directory as the script's parent
diagram_path_png = str(Path(__file__).parent.parent / "gs_cloud_architecture_diagram.png")

description = """
GeoServer Cloud
GeoServer is an open-source server for sharing and editing geospatial data from any major spatial data source using open standards.
GeoServer Cloud builds on GeoServer to provide a Cloud Native distribution of its geospatial services and APIs.
Hexagons represent microservices.
Colored rectangles represent logical groupings of components.
Lines connecting a group to another component indicate that the connector applies to all services of the outgoing end and to all components of the incoming end.
White rectangles represent components that are platform/deployment choices. For example:
"Event bus" could be a cloud infrastructure provider's native service (event queue) or a microservice implementing a distributed event broker.
"Catalog/Config backend" is the software component used to access the catalog and configuration. It might be a microservice itself, a catalog/config provider for a "data directory", a database, or another external service store, depending on the available catalog/config backend implementations and how they're configured and provisioned.
"Catalog/Config storage" is the storage mechanism that backs the catalog/config software component. It might a shared "data directory" or database, a "per instance" data directory or database, and so on, depending on the available catalog/config backend implementations, and how they're configured and provisioned.
"Geospatial data sources" is whatever method is used to access the actual data served up by the microservices.
"""

print("="*80)
print("EVALUATING GEOSERVER CLOUD ARCHITECTURE - IMAGE (ACCURACY)")
print("="*80)

result = evaluate_architecture(
    evaluation_type="accuracy",
    diagram_path=diagram_path_png,
    description=description
)

file_path = save_evaluation_result(result, "accuracy", output_dir=str(project_root / "evaluations"))
print(f"\n✓ Evaluation saved to {file_path}.txt/.json")
print(f"Tokens used: {result['usage']['total_tokens']:,}")
print(f"Cost estimate: ${(result['usage']['prompt_tokens']/1_000_000*1.25 + result['usage']['completion_tokens']/1_000_000*10):.4f}")

