from evaluate_architecture import build_prompt
from evaluate_architecture_text import build_prompt as build_prompt_text

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

# IMAGE-based prompt (text only, image sent separately)
prompt_text = build_prompt("accuracy", description)

# TEXT-based prompt (includes SVG)
diagram_path_svg = "geoserver/geoserver-cloud/gs_cloud_architecture_diagram.svg"
with open(diagram_path_svg, "r", encoding="utf-8") as f:
    svg_content = f.read()

prompt_with_svg = build_prompt_text("accuracy", svg_content, description)

# Write to files
with open("prompt_image_based.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("IMAGE-BASED PROMPT (text part only)\n")
    f.write("="*80 + "\n\n")
    f.write(prompt_text)
    f.write("\n\n" + "="*80 + "\n")
    f.write(f"Prompt length: {len(prompt_text)} characters\n")
    f.write(f"Approximate tokens: {len(prompt_text) // 4}\n")
    f.write("Note: Image is sent separately as base64\n")
    f.write("="*80 + "\n")

with open("prompt_text_based.txt", "w", encoding="utf-8") as f:
    f.write("="*80 + "\n")
    f.write("TEXT-BASED PROMPT (includes full SVG)\n")
    f.write("="*80 + "\n\n")
    f.write(prompt_with_svg)
    f.write("\n\n" + "="*80 + "\n")
    f.write(f"Full prompt length: {len(prompt_with_svg):,} characters\n")
    f.write(f"Approximate tokens: {len(prompt_with_svg) // 4:,}\n")
    f.write(f"SVG content length: {len(svg_content):,} characters\n")
    f.write("="*80 + "\n")

print("✓ Prompts saved to:")
print("  - prompt_image_based.txt")
print("  - prompt_text_based.txt")
print(f"\nImage-based prompt: {len(prompt_text):,} chars (~{len(prompt_text) // 4:,} tokens)")
print(f"Text-based prompt: {len(prompt_with_svg):,} chars (~{len(prompt_with_svg) // 4:,} tokens)")

