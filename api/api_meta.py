# -*- coding: utf-8 -*-
"""api_meta.py

constant with API metadata.
"""

METADATA = {
    "title": "Dictionnaire des imprimeurs-lithographes du XIXe siècle - API",
    "version": "0.1.0",
    "openapi_url": "/dil-db/api/openapi.json",
    "docs_url": "/dil-db/api/docs",
    "redoc_url": "/dil-db/api/redoc",
    "license_info": {
        "name": "MIT",
        "identifier": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
    "openapi_tags": [
        {"name": "default"},
        {"name": "Persons", "description": "Retrieve persons and their information."},
        {"name": "Patents", "description": "Retrieve patents and their information."},
        {
            "name": "Referential",
            "description": "Retrieve terms from the referential used to describe persons and patents.",
        },
    ],
    "description": """
## API Documentation for Dictionnaire des imprimeurs-lithographes du XIXe siècle

École nationale des chartes - PSL

----
""",
    "routes": {
        "get_infos": {
            "summary": "Get general database statistics",
            "description": """
Return high-level statistics about the database.

The response includes the total number of persons, patents, effective patents, cities, and addresses currently available in the API.

Effective patents are counted only when their start date falls within the historical coverage period used by the project.
""",
        },
        "get_cities_with_printers": {
            "summary": "Get geolocated cities linked to printers",
            "description": """
Return geolocated cities associated with printers and patents.

This endpoint is designed to provide data for map-based visualizations. It returns cities with geographic coordinates and the printers linked to them.

The result can be filtered by:

- city identifiers;
- patent start date or activity period;
- exact or overlapping date matching;
- full-text search on printer names;
- full-text search on patent-related content.
""",
        },
        "autocomplete_city": {
            "summary": "Autocomplete cities used in patents",
            "description": """
Return city suggestions for autocomplete fields.

The endpoint searches cities by prefix and can take already selected cities into account. When selected cities are provided, only cities compatible with the current filter context are returned.

Each result includes the city identifier, label, department label, and contextual counts for matching patents and persons.
""",
        },
        "read_images": {
            "summary": "Get images associated with a printer",
            "description": """
Return all images associated with a specific printer through their patents.

The response groups images by patent and indicates whether each image is pinned. It also includes aggregate counts and a dedicated list of pinned images.

Use this endpoint to retrieve visual material linked to a printer record.
""",
        },
        "read_printers": {
            "summary": "Search and list printers",
            "description": """
Return a paginated list of printers.

This endpoint supports combined filtering and sorting. Results can be filtered by printer name, patent content, city of practice, and patent date or period.

Available filters include:

- full-text search in printer names;
- full-text search in patent-related content;
- one or more cities of practice;
- exact or overlapping date matching;
- alphabetical sorting by last name.

Each result includes basic printer information, the total number of patents, optional search highlights, and a summary of places of practice.
""",
        },
        "read_printer": {
            "summary": "Get a printer by ID",
            "description": """
Return the detailed record of a printer identified by their DIL identifier.

The response includes the structured information available for the printer, such as names, biographical data, related patents, places, and associated relationships depending on the data model.

Use the `html` query parameter to include HTML-enriched fields when available.
""",
        },
        "read_patents": {
            "summary": "List patents",
            "description": """
Return a paginated list of patents.

Each patent entry includes its DIL identifier and core descriptive information, such as label, start date, end date, and associated city when available.
""",
        },
        "read_patent": {
            "summary": "Get a patent by ID",
            "description": """
Return the detailed record of a patent identified by its DIL identifier.

The response includes structured information about the patent, including dates, location, related printer, and additional enriched data when available.

Use the `html` query parameter to include HTML-enriched fields when available.
""",
        },
        "read_cities": {
            "summary": "List cities",
            "description": """
Return a paginated list of cities from the referential.

Each city record may include its DIL identifier, label, country code, geographic coordinates, French administrative identifiers, and external authority identifiers when available.
""",
        },
        "read_city": {
            "summary": "Get a city by ID",
            "description": """
Return the detailed record of a city identified by its DIL identifier.

The response includes geographic, administrative, and external authority information when available.
""",
        },
        "read_addresses": {
            "summary": "List addresses",
            "description": """
Return a paginated list of addresses from the referential.

Each address entry includes its DIL identifier, label, associated city label, and associated city identifier when available.
""",
        },
        "read_address": {
            "summary": "Get an address by ID",
            "description": """
Return the detailed record of an address identified by its DIL identifier.

The response includes the address label and its associated city information when available.
""",
        },
        "get_graph_data": {
            "summary": "Get graph data for patents, printers, and cities",
            "description": """
Return graph-oriented data representing relationships between patents, printers, and cities.

This experimental endpoint is intended for network visualization. It builds nodes for patents, printers, and cities, and edges for relationships such as patent ownership, localization, and printer-to-printer relations.

The graph can be filtered by year when enabled.
""",
        },
        "get_meta_person": {
            "summary": "Get developer metadata for person records",
            "description": """
Return technical metadata about person records.

This endpoint is intended for developers and administrators who need information about the structure, availability, or internal handling of person-related data.
""",
        },
        "read_root": {
            "summary": "Check API availability",
            "description": """
Return a simple response indicating whether the API service is available.

This endpoint can be used as a lightweight health check.
""",
        },
        "search": {
            "summary": "Run a full-text search over printers",
            "description": """
Run a full-text search over printer records and related indexed content.

This endpoint is intended to retrieve matching persons from the search index and may return highlights or matched identifiers depending on the implementation.
""",
        },
        "read_person_events": {
            "summary": "List events related to a person",
            "description": """
Return all known events associated with a specific person.

Events may include biographical, professional, administrative, or patent-related information depending on the available data.
""",
        },
        "read_person_family_relationships": {
            "summary": "List family relationships related to a person",
            "description": """
Return all known family relationships associated with a specific person.

The response may include relationship types and linked person records when available.
""",
        },
        "read_person_thesauri_terms": {
            "summary": "List thesaurus terms related to persons",
            "description": """
Return thesaurus terms used to describe person records.

These terms belong to the project referential and may be used for classification, filtering, or semantic description of persons.
""",
        },
        "read_person_thesaurus_term": {
            "summary": "Get a person thesaurus term by ID",
            "description": """
Return a specific thesaurus term used to describe person records.

The term is identified by its DIL identifier and may include labels, definitions, or related referential information depending on the data model.
""",
        },
    },
}
