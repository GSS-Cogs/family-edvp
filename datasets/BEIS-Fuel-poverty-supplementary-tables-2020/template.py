from gssutils import pathify

def generate_codelist_from_template(url, title, label, path_id):
    """
    Returns a codelist csvw template with a vars placed in it
    """
    pathified_label = pathify(label)
    pathified_title = pathify(title)

    return """
    {{
  "@context": "http://www.w3.org/ns/csvw",
  "@id": "{path_id}#schema",
  "url": "{url}",
  "tableSchema": {{
    "columns": [
      {{
        "titles": "Label",
        "name": "label",
        "datatype": "string",
        "required": true,
        "propertyUrl": "rdfs:label"
      }},
      {{
        "titles": "Notation",
        "name": "notation",
        "datatype": {{
          "base": "string",
          "format": "^-?[\\w\\.\\/]+(-[\\w\\.\\/]+)*$"
        }},
        "required": true,
        "propertyUrl": "skos:notation"
      }},
      {{
        "titles": "Parent Notation",
        "name": "parent_notation",
        "datatype": {{
          "base": "string",
          "format": "^(-?[\\w\\.\\/]+(-[\\w\\.\\/]+)*|)$"
        }},
        "required": false,
        "propertyUrl": "skos:broader",
        "valueUrl": "{path_id}#concept/{pathified_label}/{{parent_notation}}"
      }},
      {{
        "titles": "Sort Priority",
        "name": "sort",
        "datatype": "integer",
        "required": false,
        "propertyUrl": "http://www.w3.org/ns/ui#sortPriority"
      }},
      {{
        "titles": "Description",
        "name": "description",
        "datatype": "string",
        "required": false,
        "propertyUrl": "rdfs:comment"
      }},
      {{
        "virtual": true,
        "propertyUrl": "rdf:type",
        "valueUrl": "skos:Concept"
      }},
      {{
        "virtual": true,
        "propertyUrl": "skos:inScheme",
        "valueUrl": "{path_id}#scheme/{pathified_label}"
      }}
    ],
    "primaryKey": "notation",
    "aboutUrl": "{path_id}#concept/{pathified_label}/{{notation}}"
  }},
  "prov:hadDerivation": {{
    "@id": "{path_id}#scheme/{pathified_label}",
    "@type": "skos:ConceptScheme",
    "rdfs:label": "{label}"
  }}
    """.format(url=url, label=label, pathified_label=pathified_label, path_id=path_id, pathified_title=pathified_title)