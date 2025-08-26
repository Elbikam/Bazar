# Data Science with Multiple Agents

## Overview

This project demonstrates a multi-agent system designed for sophisticated data analysis. It integrates several specialized agents to handle different aspects of the data pipeline, from data retrieval to advanced analytics and machine learning. The system is built to interact with BigQuery, perform complex data manipulations, generate data visualizations and execute machine learning tasks using BigQuery ML (BQML). The agent can generate text response as well as visuals, including plots and graphs for data analysis and exploration.


## Agent Details
The key features of the Data Science Multi-Agent include:

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational |
| **Complexity:**  | Advanced |
| **Agent Type:**  | Multi Agent |
| **Components:**  | Tools, AgentTools, Session Memory, RAG |
| **Vertical:**  | All (Applicable across industries needing advanced data analysis) |


### Architecture
![Data Science Architecture](data-science-architecture.png)


### Key Features

*   **Multi-Agent Architecture:** Utilizes a top-level agent that orchestrates sub-agents, each specialized in a specific task.
*   **Database Interaction (NL2SQL):** Employs a Database Agent to interact with BigQuery using natural language queries, translating them into SQL.
*   **Data Science Analysis (NL2Py):** Includes a Data Science Agent that performs data analysis and visualization using Python, based on natural language instructions.
*   **Machine Learning (BQML):** Features a BQML Agent that leverages BigQuery ML for training and evaluating machine learning models.
*   **Code Interpreter Integration:** Supports the use of a Code Interpreter extension in Vertex AI for executing Python code, enabling complex data analysis and manipulation.
*   **ADK Web GUI:** Offers a user-friendly GUI interface for interacting with the agents.
*   **Testability:** Includes a comprehensive test suite for ensuring the reliability of the agents.



