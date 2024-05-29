from kani_utils.kanis import StreamlitKani
from kani import AIParam, ai_function
from typing import Annotated, List
import textwrap
import logging
import requests


class PhenomicsAgent(StreamlitKani):
    """A Kani that can use the redline library to compute diffs between text inputs."""

    def __init__(self, *args, **kwargs):
        kwargs['system_prompt'] = textwrap.dedent(f"""
            You are the Phenomics Assistant, an AI-powered chatbot that can answer questions about data from the Monarch Initiative knowledge graph. 
            You can search for entities such as genes, diseases, and phenotypes by name to get the associated ontology identifier. 
            You can retrieve associations between entities via their identifiers. 
            Users may use synonyms such as 'illness' or 'symptom'. DO NOT assume the user is familiar with biomedical terminology. 
            ALWAYS add additional information such as lay descriptions of phenotypes. 
            IMPORTANT: Include markdown-formatted links to the Monarch Initiative for all results using the templates provided by function call responses, AND include links to publications if provided.
            """).strip()
        
        super().__init__(*args, **kwargs)

        self.greeting = "Hello! I am the Phenomics Assistant. How can I help you today?"
        self.description = "Searches the Monarch Initiative knowledge graph." # "An AI-driven copy editor."
        self.avatar = "ℹ️"
        self.user_avatar = "👤"
        self.name = "" # "RedLiner"

        self.api_base = "https://oai-monarch-plugin.monarchinitiative.org"

    # helper function to make API calls
    def api_call(self, endpoint, timeout=30, **kwargs):
        url = f"{self.api_base}/{endpoint}"
        logging.info(f"############ api_call: url={url}, kwargs={kwargs}")
        response = requests.get(url, params=kwargs, timeout=timeout)
        response.raise_for_status()
        return response.json()

    # search endpoint, implements all parameters described in openapi.json
    @ai_function()
    def search_entity(self,
                        term: Annotated[str, AIParam(desc="The ontology term to search for.")],
                        category: Annotated[str, AIParam(desc="A single category to search within as a string. Valid categories are: biolink:Disease, biolink:PhenotypicQuality, and biolink:Gene")] = "biolink:Disease",
                        limit: Annotated[int, AIParam(desc="The maximum number of search results to return.")] = 10,
                        offset: Annotated[int, AIParam(desc="Offset for pagination of results.")] = 0):
            """Search for entities in the Monarch knowledge graph."""
            logging.info(f"search: term={term}, category={category}, limit={limit}, offset={offset}")
            return self.api_call("search", term=term, category=category, limit=limit, offset=offset)
    
    # get disease gene associations
    @ai_function()
    def get_disease_gene_associations(self,
                                        disease_id: Annotated[str, AIParam(desc="The ontology identifier of the disease.")],
                                        limit: Annotated[int, AIParam(desc="The maximum number of associations to return.")] = 10,
                                        offset: Annotated[int, AIParam(desc="Offset for pagination of results.")] = 0):
            """Get a list of genes associated with a disease."""
            return self.api_call("disease-genes", disease_id=disease_id, limit=limit, offset=offset)  

    # get disease phenotype associations
    @ai_function()
    def get_disease_phenotype_associations(self,
                                            disease_id: Annotated[str, AIParam(desc="The ontology identifier of the disease.")],
                                            limit: Annotated[int, AIParam(desc="The maximum number of associations to return.")] = 10,
                                            offset: Annotated[int, AIParam(desc="Offset for pagination of results.")] = 0):
            """Get a list of phenotypes associated with a disease."""
            return self.api_call("disease-phenotypes", disease_id=disease_id, limit=limit, offset=offset)
    
    # get gene disease associations
    @ai_function()
    def get_gene_disease_associations(self,
                                        gene_id: Annotated[str, AIParam(desc="The identifier of the gene.")],
                                        limit: Annotated[int, AIParam(desc="The maximum number of associations to return.")] = 10,
                                        offset: Annotated[int, AIParam(desc="Offset for pagination of results.")] = 0):
            """Get a list of diseases associated with a gene."""
            return self.api_call("gene-diseases", gene_id=gene_id, limit=limit, offset=offset)
    
    # get gene phenotype associations
    @ai_function()
    def get_gene_phenotype_associations(self,
                                        gene_id: Annotated[str, AIParam(desc="The ontology identifier of the gene.")],
                                        limit: Annotated[int, AIParam(desc="The maximum number of associations to return.")] = 10,
                                        offset: Annotated[int, AIParam(desc="Offset for pagination of results.")] = 0):
            """Get a list of phenotypes associated with a gene."""
            return self.api_call("gene-phenotypes", gene_id=gene_id, limit=limit, offset=offset)
    
    # get phenotype disease associations
    @ai_function()
    def get_phenotype_disease_associations(self,
                                            phenotype_id: Annotated[str, AIParam(desc="The ontology identifier of the phenotype.")],
                                            limit: Annotated[int, AIParam(desc="The maximum number of associations to return.")] = 10,
                                            offset: Annotated[int, AIParam(desc="Offset for pagination of results.")] = 0):
            """Get a list of diseases associated with a phenotype."""
            return self.api_call("phenotype-diseases", phenotype_id=phenotype_id, limit=limit, offset=offset)
    
    # get phenotype gene associations
    @ai_function()
    def get_phenotype_gene_associations(self,
                                        phenotype_id: Annotated[str, AIParam(desc="The ontology identifier of the phenotype.")],
                                        limit: Annotated[int, AIParam(desc="The maximum number of associations to return.")] = 10,
                                        offset: Annotated[int, AIParam(desc="Offset for pagination of results.")] = 1):
            """Get a list of genes associated with a phenotype."""
            return self.api_call("phenotype-genes", phenotype_id=phenotype_id, limit=limit, offset=offset)
        
    # get entities
    @ai_function()
    def get_entities(self,
                    ids: Annotated[List[str], AIParam(desc="The ontology identifier of the entity.")]):
            """Get a single entity by its ontology identifier."""
            return self.api_call("entity", ids=ids)
