from kani_utils.base_kanis import StreamlitKani
from kani import AIParam, ai_function, ChatMessage
from typing import Annotated, List
import logging
import requests
import streamlit as st

from neo4j import GraphDatabase

# for reading API keys from .env file
import os
import json
import httpx


class PhenomicsAgent(StreamlitKani):
    """A Kani that can use the redline library to compute diffs between text inputs."""

    def __init__(self, *args, **kwargs):
        kwargs['system_prompt'] = """
You are the Phenomics Assistant, an AI-powered chatbot that can answer questions about data from the Monarch Initiative knowledge graph. 
You can search for entities such as genes, diseases, and phenotypes by name to get the associated ontology identifier. 
You can retrieve associations between entities via their identifiers. 
Users may use synonyms such as 'illness' or 'symptom'. DO NOT assume the user is familiar with biomedical terminology. 
ALWAYS add additional information such as lay descriptions of phenotypes. 
IMPORTANT: Include markdown-formatted links to the Monarch Initiative for all results using the templates provided by function call responses, AND include links to publications if provided.
""".strip()
        
        super().__init__(*args, **kwargs)

        self.greeting = """I'm the Phenomics Assistant, an AI chatbot with access to the [Monarch Initiative](https://monarchinitiative.org) biomedical knowledgebase. I can search for information on diseases, genes, and phenotypes. Here are some things you might try asking:
    
- What is the genetic basis of Cystic Fibrosis?
- What symptoms are associated with Fanconi Anemia?

Please note that I am a research preview, and this information should not be used for diagnoses, clinical decision making, or other medical applications.
""".strip()

        self.description = "Queries the Monarch Initiative knowledge graph." # "An AI-driven copy editor."
        self.avatar = "🧬"
        self.user_avatar = "👤"
        self.name = "Phenomics Assistant"

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



class Neo4jAgent(StreamlitKani):
    """Base class for agents that interact with the knowledge graph. NOTE: set NEO4J_BOLT to e.g. bolt://localhost:7687 in .env file."""
    def __init__(self, 
                 *args,
                 max_response_tokens = 10000, 
                 system_prompt = "You have access to a neo4j knowledge graph, and can run cypher queries against it.",
                 **kwargs
                 ):

        super().__init__(system_prompt = system_prompt, *args, **kwargs)

        # dev instance of KG
        self.neo4j_uri = os.environ["NEO4J_URI"]  # default bolt protocol port
        self.neo4j_driver = GraphDatabase.driver(self.neo4j_uri)

        # if description is given, set self.description to it
        if 'description' in kwargs:
                self.description = kwargs['description']

        self.max_response_tokens = max_response_tokens



    @ai_function()
    def query_kg(self, query: Annotated[str, AIParam(desc="Cypher query to run.")],):
        """Run a cypher query against the database."""

        def render_query():
             st.markdown(f"Query Used: ```{query}```")

        self.render_in_streamlit_chat(render_query)

        with self.neo4j_driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]

        result = json.dumps(data)
        # if self.message_token_len reports more than 10000 tokens in the result, we need to ask the agent to make the request smaller
        tokens = self.message_token_len(ChatMessage.user(result))
        if tokens > self.max_response_tokens:
            return f"ERROR: The result contained {tokens} tokens, greater than the maximum allowable of {self.max_response_tokens}. Please try a smaller query."
        else:
            return result
        




class MonarchKGAgent(Neo4jAgent):
    """Agent for interacting with the Monarch knowledge graph; extends KGAgent with keyword search (using Monarch API) system prompt with cypher examples."""
    def __init__(self, *args, **kwargs):

        competency_questions = json.load(open("monarch_competency_questions_1.json", "r")) # list of dict
        # keep only question, search_terms, and query
        competency_questions = [{k: v for k, v in cq.items() if k in ["question", "search_terms", "query"]} for cq in competency_questions]

        # read contents of kg_summary.md into a string for inclusion into the markdown below
        with open("kg_summary.md", "r") as f:
            kg_summary = f.read()

        # note: putting the instructions before background info helps a lot
        system_prompt = f"""
You are the Phenomics Assistant, designed to assist users in exploring and intepreting a biomedical knowledge graph known as Monarch.

Here is a summary of the graph in markdown format:

```
{kg_summary}
```

When users present questions, you'll typically first search for relevant identifiers, then run Cypher queries against the Neo4j database storing the graph. Here are some example questions, searches, and cypher queries:

```
{json.dumps(competency_questions, indent=4)}
```

Instructions:
- Provide non-specialist descriptions of biomedical results to ensure that the information is accessible to users without a specialized background.
- Use the `MATCH (n)-[:`biolink:subclass_of`*]->(m)` pattern liberally to use the graph structure to your advantage.
- Use `LIMIT` and `SKIP` clauses to to answer users' questions accurately and efficiently. 
- Include links in the format [Entity Name](https://monarchinitiative.org/entity_id).
- Refuse to answer questions not related to biomedical information or the Monarch knowledge graph.

""".strip()
        
        super().__init__(system_prompt = system_prompt, *args, **kwargs)

        self.greeting = """I'm the Phenomics Explorer, an experimental AI with knowledge of the Monarch Initiative's knowledge graph structure and contents. I can answer questions via complex graph queries. Some things you can ask:

- What phenotypes are associated with more than one subtype of EDS?
- What is the shortest path between Abnormal dermatoglyphics and the GSTM3 gene?
- Which gene is directly or indirectly associated with the largest number of diseases? (I struggle with this one!)

**Please note that as an experimental work in progress I frequently make mistakes.** More information is available in my [implementation notes](https://github.com/monarch-initiative/phenomics-assistant/blob/new_backend/pe_notes.md).
"""
        self.description = "Queries the Monarch KG with graph queries and contextual information."
        self.avatar = "🕷️"
        self.user_avatar = "👤"
        self.name = "Phenomics Explorer (Experimental)"


    @ai_function()
    def search(self, 
               search_terms: Annotated[List[str], AIParam(desc="Search terms to look up in the database.")],):
        """Search for nodes matching one or more terms. Each term is searched separately."""

        # single query endpoint url is e.g. https://api-v3.monarchinitiative.org/v3/api/search?q=cystic%20fibrosis&limit=10&offset=0
        # use httpx for each search term
        # return the results as a list of dictionaries

        results = {}
        ids = []

        for term in search_terms:
            url = f"https://api-v3.monarchinitiative.org/v3/api/search?q={term}&limit=5&offset=0"
            response = httpx.get(url)
            resp_json = response.json()
            items_slim = []
            if 'items' in resp_json:
                for item in resp_json['items']:
                    items_slim.append({k: v for k, v in item.items() if k in ['id', 'category', 'name', 'in_taxon_label']})
                    ids.append(item['id'])
            results[term] = items_slim

        # again, if self.message_token_len reports more than 10000 tokens in the result, we need to ask the agent to make the request smaller
        tokens = self.message_token_len(ChatMessage.user(json.dumps(results)))
        if tokens > self.max_response_tokens:
            return f"ERROR: The result contained {tokens} tokens, greater than the maximum allowable of {self.max_response_tokens}. Please try a smaller search."
        else:
            return results        
