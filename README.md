Latest update: March 13, 2026
# GraphRAG and PostgreSQL integration in docker with AGE and AI agents
This solution accelerator is designed to integrate graphRAG and PostgreSQL in a docker, with AGE added and AI agents capabilities on top. This enables Cypher queries, besides graphRAG search, vector search. Even more, AI agents can be built on top to perform advanced tasks by utilizing the rich knowledge graph.

## Background and objectives:
This solution is especially useful when:
- You have raw input data already in a DB.
- You want Cypher query capabilities.
- You prefer CLI version of graphRAG.
- You want to avoid another blob storage between the DB and graphRAG.

## Solution Accelerator Architecture
The solution is to build graphRAG index directly using the data in DB. The docker image uses postgres as base, then added python, graphRAG, AGE, semantic-kernel and other needed packages. With Apache AGE, it enables Cypher queries.
Two volumes are created to persist postgres data and app related data.

<p align="center">
<img src="project_folder/data/pics/graphrag-postgres.png" style="width:70%; height:auto; display: block; margin: 0 auto;  text-align:center">
</p>

## What's new:
1> New graphRAG version 3.0.5. GraphRAG 3.0.5 stabilizes the 3.x configuration‑driven, API‑based architecture and improves indexing reliability, making graph construction more predictable and easier to integrate into real workflows. <br>

2> Postgres:16-bookworm. Its' a fully supported long‑term release built on Debian 12, providing a modern and stable foundation for Apache AGE and graph persistence. <br>

3> Added MCP tools:<br>
[graphrag_search]:<br>
    description="Run a GraphRAG query (local or global) with runtime-tunable API params". <br>
[age_get_schema_cached]: <br>
    description="Return cached AGE graph schema; if refresh=true, re-query the database and update the cache." <br>
[age_cypher_query]: <br>
    description="Execute a user-provided Cypher query against the AGE graph and return rows (each row under key 'result')." <br>
[age_entity_lookup]: <br>
    description="Find Entity nodes by name/title substring match (best for 'Who is X?' or quick disambiguation)." <br>
[age_nl2cypher_query]   <br>
    description="Convert a natural-language question into a Cypher query (Entity/RELATED_TO only), execute it, and return rows; best for complex or multi-hop semantic graph questions." <br>
    
4> Uses Microsoft agent framework. Multiple scenarios of agents with MCP tools are included in the agent-notebook.ipynb: <br>

- graphRAG search: local search and global search examples with direct mcp call. <br>
- graphRAG search: local search and global search examples with agent and include mcp tools. <br>
- Cypher query in direct mcp call.<br>
- Agent to query in natural language, and mcp tool included to convert NL2Cypher.<br>
- Agent with unified mcp ( all five mcp tools), and based on the question route to the corresponding tool.<br>

## How to deploy the solution
Please refer to the HOWTO.pdf for detailed steps to deploy the solution:

- [HOWTO.pdf](https://github.com/Azure-Samples/postgreSQL-graphRAG-docker/blob/main/project_folder/HOWTO.pdf)

## Trademark Notice
This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft’s Trademark & Brand Guidelines. https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks. 
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party’s policies.


