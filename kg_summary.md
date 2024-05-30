## Node Labels and Properties

### Common Properties Across Node Types
- `name`: The common name of the entity.
- `description`: A detailed description of the entity.
- `id`: A unique identifier for the entity.
- `in_taxon_label`: The taxonomic association of the entity (when applicable).
- `synonym`: Alternative names or synonyms for the entity.
- `provided_by`: The source or database that provided the information.
- `category`: The ontological categories the entity belongs to.

### Specific Node Types and Their Properties

#### `biolink:Gene`
- Description: Represents genes with information about symbols, synonyms, full names, cross-references, and taxonomic context.
- Additional Properties: `symbol`, `full_name`.

#### `biolink:Disease`
- Description: Represents diseases with information about synonyms, names, descriptions, and sources.

#### `biolink:ChemicalEntity`
- Description: Represents chemical entities with details about synonyms, names, descriptions, and sources.

#### `biolink:BiologicalProcess`
- Description: Represents biological processes with information about names, taxonomic context, and sources.

#### `biolink:Cell`
- Description: Represents cells with details about names, descriptions, and sources.

#### `biolink:PhenotypicFeature`
- Description: Represents phenotypic features with information about synonyms, names, descriptions, and sources.

#### `biolink:Pathway`
- Description: Represents pathways with information about names, taxonomic context, and sources.

#### `biolink:Drug`
- Description: Represents drugs with information about synonyms, names, descriptions, and sources.

#### `biolink:Publication`
- Description: Represents publications, including articles, patents, and web pages.

#### `biolink:EvidenceType`
- Description: Represents types of evidence used to support assertions.

## Relationship Types and Contexts

### Important Relationships
- `biolink:interacts_with`: Indicates interactions between entities such as genes or gene products.
- `biolink:expressed_in`: Indicates where a gene or gene product is expressed within an anatomical entity or cell type.
- `biolink:has_phenotype`: Connects genes or gene products to phenotypic features, indicating an association with certain phenotypes or diseases.
- `biolink:actively_involved_in`: Connects genes or gene products to biological processes or activities, indicating active involvement.
- `biolink:orthologous_to`: Connects genes or gene products that are orthologous to each other, indicating evolutionary relationships.
- `biolink:enables`: Connects genes or gene products to biological processes or activities that they enable.
- `biolink:located_in`: Indicates the cellular or anatomical location of a gene or gene product.
- `biolink:subclass_of`: Hierarchical relationship connecting phenotypic features to their broader categories.
- `biolink:participates_in`: Connects genes or gene products to biological pathways in which they participate.
- `biolink:gene_associated_with_condition`: Connects genes or gene products to diseases or phenotypic features, indicating an association with certain conditions.
- `biolink:causes`: Indicates that a gene or gene product causes a disease or phenotypic feature.
- `biolink:contributes_to`: Indicates that a gene or gene product contributes to a disease or phenotypic feature.
- `biolink:enables`: Connects genes or gene products to biological processes or activities that they enable.
- `biolink:part_of`: Indicates that a gene or gene product is part of a biological process or activity.
- `biolink:related_to`: A general relationship that connects diseases to various biological entities such as phenotypic features, biological processes, or anatomical entities.

### Important Relationship Properties
- `has_evidence`: A property of relationships indicating the type of evidence supporting the relationship. Found in relationships such as `biolink:acts_upstream_of_or_within`, `biolink:actively_involved_in`, `biolink:enables`, `biolink:located_in`, `biolink:part_of`, and `biolink:orthologous_to`.
- `publications`: A property of relationships referring to publications that are associated with the relationship. Found in relationships such as `biolink:has_phenotype` and `biolink:has_mode_of_inheritance`.
- Qualifier properties: Provide additional context to relationships. Examples include `sex_qualifier`, `frequency_qualifier`, `onset_qualifier`, and `stage_qualifier`. Found in relationships such as `biolink:has_phenotype` and `biolink:expressed_in`.

## Redundancy and Frequency Analysis

- General labels such as `biolink:Entity` and `biolink:NamedThing` are very common and may be too general for most queries.
- Biological labels like `biolink:BiologicalEntity` and `biolink:PhysicalEssence` are also quite common but cover a wide range of biological concepts.
- Specific labels such as `biolink:Gene`, `biolink:Disease`, and `biolink:ChemicalEntity` are useful for targeted queries.
