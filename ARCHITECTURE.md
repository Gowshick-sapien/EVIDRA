# System Architecture

The Fact Knowledge Layer is organized into four distinct layers, each with a strict responsibility boundary. The architecture is designed to enforce the principle that *observations are not facts, and facts are not decisions.*

## Layer 1: Document Evidence Preparation
This layer is responsible for ingesting PDF documents and creating a structured, provenance-tagged representation. It operates without any semantic reasoning, focusing solely on layout, text, and tabular structures.

* **Primary Engine:** PyMuPDF (fitz) for fast document loading, text block extraction, and precise bounding box generation.
* **Table Specialist:** pdfplumber for precise structural extraction of tables, cells, and multi-line headers.
* **Evidence Bundling:** Every extracted span is assigned a stable ID and coordinate anchor, creating an immutable Evidence Object.

## Layer 2: Fact Construction
This layer interprets the Evidence Objects to generate structured propositions. Crucially, it separates the generation of a claim from its verification.

* **Extraction Agents:** Domain-specific prompts (numerical, semantic, event) instruct the LLM (Qwen2.5) to identify claims within the evidence.
* **Evidence Verifier:** An independent agent that checks if the extracted claim is strictly entailed by the cited evidence, acting as a safeguard against LLM hallucination.
* **Context Resolver:** Extracts dimensions of meaning (units, currencies, scopes).
* **Deterministic Normalizers:** Python-native validation for exact financial arithmetic (Decimal) and date parsing.
* **Fact Grouping:** sentence-transformers (BGE-Small) generates embeddings to block similar facts into groups for relationship testing.

## Layer 3: Fact Decision Engine
This is the core orchestration layer where facts are compared, contradicted, or reconciled. The workflow is deterministically controlled by LangGraph.

* **Hypothesis Generator:** Proposes explanations (e.g., temporal mismatch, scope difference) when two facts within a group appear to differ.
* **Specialist Validators:** Deterministic or semantic agents that test specific hypotheses against the facts' context.
* **Reconciliation Agent:** Attempts to find a logically sound explanation that allows both facts to be true based on the evidence.
* **Adversarial Challenge:** A skeptic agent that attempts to falsify any proposed reconciliation using the original source documents.
* **Decision Policy:** A pure Python rule engine that maps the surviving validation paths to a final categorical verdict (CORROBORATED, CONTRADICTION, RECONCILED, UNRESOLVED).

## Layer 4: Observability and Inspection
This layer provides the interfaces and artifacts necessary for human and machine inspection.

* **Evidence Ledger (SQLite):** The relational system of record storing the full hierarchy from Document to Decision.
* **Inspectable Artifacts:** JSON/JSONL for machine-readable state and streams; Markdown for executive reports.
* **Interfaces:** A FastAPI backend with auto-generated Swagger UI for interactive inspection, paired with an rgparse CLI for rapid local evaluation.

---

## Complete System Topology

`	ext
                         FACT KNOWLEDGE LAYER
                                  |
                +-----------------+-----------------+
                |                                   |
         DOCUMENT PROCESSING                    REASONING
                |                                   |
          +-----+-----+                       +-----+------+
          |           |                       |            |
       PyMuPDF    pdfplumber                Ollama      BGE-small
       (Engine)    (Tables)                (Qwen2.5)   (Embeddings)
          |           |                       |            |
          +-----+-----+                       |            |
                |                             |            |
                v                             |            |
         Evidence Objects                     |            |
                |                             |            |
                +-------------+---------------+------------+
                              |
                              v
                         Pydantic v2
                              |
                              v
                          LangGraph
                              |
        +---------------------+---------------------+
        |                     |                     |
   Extraction            Verification            Context
     Agents                 Agent               Resolver
        +---------------------+---------------------+
                              |
                              v
                         Fact Groups
                              |
                     Hypothesis Generator
                              |
                   +----------+----------+
                   |          |          |
                   v          v          v
               Numerical   Temporal   Semantic
               Validator  Validator  Validator
               (Decimal)  (dateutil)  (Rules)
                   +----------+----------+
                              |
                              v
                     Reconciliation Agent
                              |
                              v
                    Adversarial Challenge
                              |
                              v
                    Decision Policy (Pure Python)
                              |
                              v
                        Final Decision
                              |
                     +--------+--------+
                     |                 |
                     v                 v
                  SQLite         JSON / JSONL / MD
                     |
                     v
               FastAPI + CLI (argparse)
`
