from evaluate_architecture import evaluate_all_criteria as evaluate_image
from evaluate_architecture_text import evaluate_all_criteria as evaluate_text

diagram_path_png = "geoserver/geoserver-cloud/gs_cloud_architecture_diagram.png"
diagram_path_svg = "geoserver/geoserver-cloud/gs_cloud_architecture_diagram.svg"

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
print("EVALUATING GEOSERVER CLOUD ARCHITECTURE")
print("="*80)

print("\n[1/2] Running IMAGE-based evaluation (PNG)...")
print("-"*80)
image_results = evaluate_image(diagram_path_png, description)

print("\n\n[2/2] Running TEXT-based evaluation (SVG)...")
print("-"*80)
text_results = evaluate_text(diagram_path_svg, description)

print("\n" + "="*80)
print("EVALUATION COMPLETE!")
print("="*80)
print(f"\nImage-based results: evaluations/")
print(f"Text-based results: evaluations_text/")
print("\nRun compare_evaluations.py to compare the results!")

