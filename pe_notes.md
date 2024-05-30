## Implementation Notes - Phenomics Explorer

The Phenomics "Explorer" agent implemented in this branch attemtps to use LLMs to
generate Cypher queries against the Monarch Initiative Neo4J database. Tested LLMs (including GPT-4)
struggle with accurate generation of Cypher queries, and need sufficient context about the
graph to generate effective queries. This implementation attempts to address these with extensive
system-prompt information, including a [summary](kg_summary.md) of KG contents and a set of
[example competency questions and queries](monarch_competency_questions_1.json). (These were generated
interactively via trial-and-error with a similar query-generating agent.)

Results so far are mixed. In some cases the agent is able to develop sophisticated queries to answer
graph-based questions, such as "What genes influence more than one phenotype of any subtype of EDS?"
In other cases however, the agent misinterprets questions too narrowly. "Which gene is directly or
indirectly associated with the largest number of diseases?" for example may use only
`biolink:gene_associated_with_condition` links due to the "associated" keyword when
`biolink:causes` and other relationships may be important. It also occasionally generates
computationally- or results-heavy queries, resulting in poor database performance or massive
token counts in returned information. Currently results longer than 10K tokens are not returned
the model and it is asked to try again with a smaller query.