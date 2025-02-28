"""api_meta.py

constant with API metadata.
"""

METADATA = {
    "title": "Dictionnaire des imprimeurs-lithographes du XIXe siècle - API",
    "version": "0.1.0",
    "openapi_url": "/dil/api/openapi.json",
    "docs_url": "/dil/api/docs",
    "redoc_url": "/dil/api/redoc",
    "license_info": {
        "name": "MIT",
        "identifier": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    "swagger_ui_parameters": {"defaultModelsExpandDepth": -1},
    "openapi_tags": [
        {"name": "default"},
        {"name": "Persons", "description": "Retrieve persons and their information."},
    ],
    "description": """
## API Documentation for Dictionnaire des imprimeurs-lithographes du XIXe siècle

École nationale des chartes - PSL

----
""",
    "routes": {
        "get_meta_person": {
            "summary": "Get a meta and db administration information utils on person for developers.",
            "description": "",
        },
        "read_root": {
            "summary": "Check if the service is available.",
            "description": "",
        },
        "search": {
            "summary": "Full-text search to retrieve persons.",
            "description": "",
        },
        "read_persons": {
            "summary": "Retrieve all available persons.",
            "description": "",
        },
        "read_person": {
            "summary": "Retrieve a person by its _endp_id.",
            "description": "",
        },
        "read_person_events": {
            "summary": "Retrieve all events related to a specific person.",
            "description": "",
        },
        "read_person_family_relationships": {
            "summary": "Retrieve all family relationships related to a specific person.",
            "description": "",
        },
        "read_person_thesauri_terms": {
            "summary": "Retrieve all available thesauri terms.",
            "description": "",
        },
        "read_person_thesaurus_term": {
            "summary": "Retrieve a specific thesaurus term by its _endp_id.",
            "description": "",
        },


    }
}
