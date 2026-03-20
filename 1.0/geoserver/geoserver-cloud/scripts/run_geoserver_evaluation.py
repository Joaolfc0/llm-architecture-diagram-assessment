import sys
import argparse
import time
from pathlib import Path

# Add project root to sys.path (scripts -> geoserver-cloud -> geoserver -> project root)
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from evaluate_architecture import evaluate_all_criteria as evaluate_image
from evaluate_architecture_text import evaluate_all_criteria as evaluate_text

# Diagram paths relative to this script
diagram_path_png = str(Path(__file__).resolve().parent.parent / "gs_cloud_architecture_diagram.png")
diagram_path_svg = str(Path(__file__).resolve().parent.parent / "gs_cloud_architecture_diagram.svg")

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


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate GeoServer Cloud Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run only image-based evaluation
  python run_geoserver_evaluation.py --image-only
  
  # Run only text-based evaluation
  python run_geoserver_evaluation.py --text-only
  
  # Run both (with delay between them)
  python run_geoserver_evaluation.py --both --delay 60
  
  # Run both with default 30 second delay
  python run_geoserver_evaluation.py --both
        """
    )
    
    parser.add_argument(
        "--image-only",
        action="store_true",
        help="Run only image-based evaluation (PNG)"
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Run only text-based evaluation (SVG)"
    )
    parser.add_argument(
        "--both",
        action="store_true",
        help="Run both image and text evaluations"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=30,
        help="Delay in seconds between image and text evaluations (default: 30)"
    )
    
    args = parser.parse_args()
    
    # If no option specified, default to both with delay
    if not (args.image_only or args.text_only or args.both):
        args.both = True
    
    print("="*80)
    print("EVALUATING GEOSERVER CLOUD ARCHITECTURE")
    print("="*80)
    
    image_results = None
    text_results = None
    
    # Run image evaluation
    if args.image_only or args.both:
        print("\n[IMAGE] Running IMAGE-based evaluation (PNG)...")
        print("-"*80)
        try:
            image_results = evaluate_image(diagram_path_png, description)
            print("\n✓ Image-based evaluation completed!")
        except Exception as e:
            print(f"\n✗ Image-based evaluation failed: {str(e)}")
            image_results = None
        
        # If running both, add delay before text evaluation
        if args.both and not args.text_only:
            print(f"\n⏳ Waiting {args.delay} seconds before starting text evaluation...")
            print("   (This helps avoid API rate limiting)")
            time.sleep(args.delay)
    
    # Run text evaluation
    if args.text_only or args.both:
        print("\n[TEXT] Running TEXT-based evaluation (SVG)...")
        print("-"*80)
        try:
            text_results = evaluate_text(diagram_path_svg, description)
            print("\n✓ Text-based evaluation completed!")
        except Exception as e:
            print(f"\n✗ Text-based evaluation failed: {str(e)}")
            text_results = None
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE!")
    print("="*80)
    
    if image_results:
        print(f"\n✓ Image-based results: evaluations/")
    if text_results:
        print(f"✓ Text-based results: evaluations_text/")
    
    print("\nRun compare_evaluations.py to compare the results!")


if __name__ == "__main__":
    main()

