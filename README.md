# BIS Metadata / Knowledge Base Dataset

## Smart India Hackathon (SIH) Project

**Checkpoint:** 15 September 2026  
**Current dataset checkpoint:** 12,223 validated BIS New Standards records

---

## 1. Project Overview

This repository contains the metadata and data-collection foundation for a Smart India Hackathon project focused on building an AI assistant for the Bureau of Indian Standards (BIS).

The objective is to build a reliable, structured and source-traceable BIS knowledge base that can later be connected to MongoDB, document processing, embeddings, vector search, hybrid retrieval, reranking and Retrieval-Augmented Generation (RAG).

The current 12,223 records are the validated **New Standards listing layer**. They are not yet a complete BIS-wide dataset covering products, QCOs, laboratories, certification services and all related regulatory information.

---

# 2. Setup for Continuing the Remaining Work

This section is intended as the handover/start point for the teammate continuing the project.

## 2.1 Clone the Repository

```bash
git clone https://github.com/siddhantjagtap150-spec/SIH_METADATASET.git
cd SIH_METADATASET
```

Open the project in VS Code:

```bash
code .
```

## 2.2 Create a Python Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

If the existing scripts require it, install `requests`:

```powershell
pip install requests
```

As the remaining work grows, maintain a `requirements.txt` containing the project's actual dependencies.

## 2.3 Project Structure

```text
SIH_metadataset/
│
├── data/
│   ├── standards/
│   │   ├── standards.json
│   │   └── standards_relationships.json
│   ├── products/
│   │   ├── products.json
│   │   └── product_relationships.json
│   └── qcos/
│       ├── qcos.json
│       └── qco_relationships.json
│
├── metadata/
│   ├── relationships.json
│   ├── schema.json
│   └── taxonomy.json
│
├── output/
├── scripts/
├── sources/
│   └── source_registry.json
└── README.md
```

Some directories/files are placeholders for later phases and do not mean that those BIS domains have already been populated.

## 2.4 Important: Do Not Restart the Completed Collection

The current resume point is **after collection and validation**.

Do not restart BIS API discovery or recollect the 12,223 records unless a deliberate refresh is required.

The next action is:

```text
Existing raw BIS data
        ↓
Normalize
        ↓
Validate
        ↓
Create manifest
        ↓
Finalize verified relationships
        ↓
GitHub Dataset v1.0
```

## 2.5 Environment and Secrets

For future MongoDB/RAG work, use environment variables for credentials and API keys.

Do not commit:

```text
.env
API keys
MongoDB passwords
LLM API keys
private tokens
```

Add `.env` to `.gitignore`.

---

# 3. Official Source Policy

The knowledge base follows an official-source-first policy.

### Source priority

1. Bureau of Indian Standards (BIS)
2. Government of India
3. Official Gazette
4. Government ministries/departments
5. Relevant international standards bodies where appropriate

Do not use Kaggle, blogs, commercial certification websites, consultancy summaries, Wikipedia, news summaries or unverified social-media content as authoritative BIS metadata.

If a value cannot be verified, use `null` or leave it unavailable rather than guessing.

Every important record should retain provenance and source information.

---

# 4. Completed Work

## 4.1 Project Structure

The repository structure has been established for:

- standards
- products
- QCOs
- metadata definitions
- relationships
- source registry
- scripts
- output/validation artifacts

## 4.2 Metadata Schema

`metadata/schema.json` has been created as the common metadata schema.

It supports entity types including:

- standard
- product
- qco
- scheme
- certification
- registration
- licence
- hallmarking_service
- crs_service
- fmcs_service
- laboratory
- test_method
- procedure
- fee
- document
- act
- rule
- regulation
- notification
- circular
- office
- contact
- complaint_service
- training_service
- consumer_service
- management_system
- other

The schema includes concepts such as:

- entity identity
- name and aliases
- classification
- description and purpose
- stakeholders
- industry sectors
- products
- standards
- schemes
- QCOs
- applicability
- eligibility
- requirements
- procedures
- testing
- certification/registration
- fees
- timelines
- validity
- renewal
- surveillance
- inspection
- complaints
- appeals/grievances
- locations
- contacts
- related entities
- FAQs
- keywords/search metadata
- source/provenance
- metadata quality/version information

## 4.3 Master Taxonomy

`metadata/taxonomy.json` has been created.

Major domains include:

- Standards
- Products
- Conformity Assessment
- Product Certification
- Compulsory Certification
- Quality Control Orders
- CRS
- Scheme-X
- FMCS
- Hallmarking
- Laboratories
- Testing
- Management Systems
- Standards Development
- Regulatory Framework
- Procedures
- Fees
- Renewal and Licence Management
- Surveillance and Enforcement
- Consumer Services
- Complaints and Grievances
- Training
- Offices and Contacts
- Documents and Forms
- Portals and Digital Services
- Organizations and Stakeholders
- International Activities
- FAQ/User Queries
- Glossary and Terminology

## 4.4 Relationship Model

`metadata/relationships.json` defines the relationship types and compliance chains needed for future multi-hop BIS queries.

Examples:

```text
Product ↔ Standard
Standard ↔ Amendment
Standard ↔ Revision
Standard ↔ Superseding Standard

QCO → Product
QCO → Standard
QCO → Certification
QCO → Scheme

Scheme → Product
Scheme → Standard
Scheme → Testing
Scheme → Inspection
Scheme → Certification
Scheme → Registration

Testing → Test Method
Testing → Laboratory

Certification → Product
Certification → Standard
Certification → Stakeholder
Certification → Licence

Licence → Product
Licence → Standard
Licence → Scheme
Licence → Renewal
Licence → Surveillance

Procedure → Entity
Procedure → Document
Procedure → Fee
Procedure → Timeline
```

A major future compliance chain is:

```text
Product
 → Standard
 → QCO
 → Scheme
 → Testing
 → Laboratory
 → Certification
 → Licence
 → Renewal
 → Surveillance / Enforcement
```

**Important:** the relationship model defines possible relationship types. It does not mean that every relationship has already been populated or verified.

Actual relationships must be supported by official evidence.

## 4.5 Official Source Registry

`sources/source_registry.json` has been created.

It defines official source categories such as:

- BIS official website
- BIS Standards Portal
- BIS Product Certification
- BIS Scheme-X
- BIS CRS
- BIS FMCS
- BIS Hallmarking
- BIS Laboratories
- Manakonline
- BIS CARE
- BIS Regulations
- BIS Notifications
- BIS Training
- Government of India QCO sources
- Official Gazette
- Government ministries/departments

Important source fields include:

- source identity
- organization
- source class
- URL
- verification status
- last verified date
- historical/superseded status where relevant

Exact URLs must be verified from official sources before being treated as evidence.

---

# 5. BIS Standards Portal Investigation

The project moved to the new BIS Standards Portal:

```text
https://standards.bis.gov.in/
```

The old BIS catalogue collection approach did not provide useful records, so the new portal became the collection source.

The portal investigation identified:

- Angular/JavaScript frontend
- backend service architecture
- standards-related APIs
- New Standards services
- Revised Standards services
- Review of Standards services
- department count services
- committee-related services
- standard-list services

The collection scripts were built around the new portal rather than the old catalogue.

---

# 6. New Standards Collection — Completed

The New Standards acquisition phase successfully collected:

**12,223 records**

across:

**18 departments**

with page size:

**100 records per page**

## Collection validation

| Metric | Verified Result |
|---|---:|
| Departments | 18 |
| Page size | 100 |
| Reported records | 12,223 |
| Collected records | 12,223 |
| Unique standard IDs | 12,223 |
| Unique standard numbers | 12,215 |
| Duplicate standard IDs | 0 |
| Duplicate standard numbers | 8 |
| Pagination discrepancy | None |
| Skipped pages | None |
| Department completion | All 18 completed successfully |

The collection therefore passed the count and pagination checks.

The eight repeated standard numbers were retained for further verification instead of being silently deleted.

---

# 7. Raw Data Preservation

Raw BIS data must remain preserved.

The intended separation is:

```text
RAW BIS DATA
    ↓
NORMALIZED DATA
    ↓
VALIDATED DATA
```

Normalization must not destroy the original source records.

The raw layer should remain available for:

- debugging
- reprocessing
- provenance
- comparison
- future enrichment
- auditability

---

# 8. Standard Detail Enrichment Status

Individual standard-detail API/service research was performed.

The research identified that individual standard details and related metadata may require additional service calls and identifiers.

However:

> **Deep individual-standard enrichment is NOT complete.**

Therefore it must not be presented as completed dataset coverage.

Future standard enrichment may include:

- official standard title/name
- department
- committee
- product manual
- summary
- referred standards
- superseding standard
- degree of equivalence
- revision information
- amendments
- classification
- ministry
- SDG mapping
- ICS
- certification status
- licence information
- CRS information
- laboratory information
- management certification information
- product-specific guidelines

Only verified official values should be added.

---

# 9. Remaining Work for Dataset v1.0

## Priority 1 — Normalize 12,223 Records

Map the existing raw BIS records into:

```text
metadata/schema.json
```

Requirements:

- preserve official standard identity
- preserve standard number
- preserve official names/titles
- normalize field names
- normalize data types
- retain source/provenance
- retain raw-source references
- do not invent values
- use `null`/unavailable for unknown values

Definition of done:

```text
12,223 raw records
        ↓
12,223 normalized records
```

## Priority 2 — Validate the Normalized Dataset

Check:

- record count
- required fields
- stable entity IDs
- standard-number presence where available
- uniqueness
- duplicate handling
- JSON validity
- schema compliance
- source/provenance
- data-type consistency
- absence of fabricated metadata

## Priority 3 — Create Dataset Manifest

Create:

```text
output/dataset_manifest.json
```

The manifest should record:

- dataset name
- version
- checkpoint date
- source
- source URL
- entity type
- total records
- unique IDs
- unique standard numbers
- duplicate information
- collection date
- normalization status
- validation status
- enrichment status
- coverage limitations
- deferred-work notes

Example:

```json
{
  "dataset_name": "BIS New Standards",
  "version": "1.0",
  "record_count": 12223,
  "unique_standard_ids": 12223,
  "unique_standard_numbers": 12215,
  "source": "BIS Standards Portal",
  "status": "validated",
  "deep_enrichment": "deferred"
}
```

## Priority 4 — Finalize Relationship Checkpoint

Only verified relationships should be included.

Every populated relationship should retain, where applicable:

- source entity
- relationship type
- target entity
- status
- source/evidence
- confidence/verification
- effective dates

Do not infer a relationship simply because it appears logically possible.

## Priority 5 — GitHub Backup

After each major milestone:

```bash
git status
git add .
git commit -m "Normalize BIS New Standards dataset"
git push
```

The repository is already backed up on GitHub.

---

# 10. Intentionally Deferred Work

These areas are not required to declare the basic Dataset v1.0 foundation ready and can be added incrementally.

## Standards

- individual standard deep-detail enrichment
- published standards
- revised standards
- review of standards
- standards lifecycle
- amendments
- corrigenda
- supersession relationships

## Products and QCOs

- products
- product-to-standard mappings
- Quality Control Orders
- ministry-wise QCO data
- QCO implementation dates
- exemptions and exceptions
- QCO amendments

## Certification

- product certification
- ISI Mark
- Scheme-I
- Scheme-IV
- Scheme-X
- CRS
- FMCS
- MCS
- other conformity-assessment schemes

## Testing

- BIS laboratories
- recognized/empanelled laboratories
- test methods
- product testing requirements
- testing frequency
- test-report relationships

## Hallmarking

- gold
- silver
- jewellers
- hallmarking centres
- assaying
- HUID
- hallmark verification
- hallmarking regulations
- charges

## Operational Information

- fees
- procedures
- applications
- renewal
- surveillance
- enforcement
- complaints
- grievances
- offices
- contacts
- training
- consumer services
- digital portals

## Knowledge Graph

- full BIS compliance relationship graph
- multi-hop compliance relationships
- regulatory dependency graph
- standard lifecycle graph
- product certification graph

---

# 11. Recommended Completion Order

Follow this order to avoid rebuilding work unnecessarily:

```text
1. Normalize 12,223 existing raw records
                ↓
2. Validate normalized dataset
                ↓
3. Create dataset_manifest.json
                ↓
4. Finalize verified relationship checkpoint
                ↓
5. Commit Dataset v1.0 to GitHub
                ↓
6. Add deeper BIS standard enrichment
                ↓
7. Collect products + product-standard relationships
                ↓
8. Collect QCOs + QCO/product/standard relationships
                ↓
9. Collect certification / CRS / FMCS / Scheme-X
                ↓
10. Collect laboratories + test methods
                ↓
11. Collect hallmarking information
                ↓
12. Collect procedures, fees, complaints and offices
                ↓
13. Build complete verified relationship graph
                ↓
14. Load structured data into MongoDB
                ↓
15. Process official BIS documents
                ↓
16. Chunk documents
                ↓
17. Generate embeddings
                ↓
18. Build vector search
                ↓
19. Build hybrid retrieval
                ↓
20. Add reranking
                ↓
21. Connect retrieval to RAG
                ↓
22. Add source citations / verification
                ↓
23. Connect RAG to the BIS AI assistant
```

---

# 12. MongoDB Phase

After Dataset v1.0 is stable, the structured knowledge base can be loaded into MongoDB.

Possible logical collections:

```text
bis_database
│
├── standards
├── products
├── qcos
├── certifications
├── registrations
├── schemes
├── laboratories
├── test_methods
├── hallmarking
├── procedures
├── fees
├── documents
├── regulations
├── notifications
├── offices
├── contacts
└── relationships
```

The final MongoDB design should be based on actual query requirements and the final normalized schema.

---

# 13. Planned RAG Architecture

The final knowledge pipeline is expected to follow:

```text
OFFICIAL BIS SOURCES
        ↓
DATA COLLECTION
        ↓
RAW DATA
        ↓
NORMALIZATION
        ↓
VALIDATION
        ↓
MONGODB
        ↓
OFFICIAL DOCUMENT PROCESSING
        ↓
CHUNKING
        ↓
EMBEDDINGS
        ↓
VECTOR SEARCH
        ↓
HYBRID RETRIEVAL
        ↓
RERANKING
        ↓
RAG
        ↓
LLM
        ↓
SOURCE CITATIONS
        ↓
BIS AI ASSISTANT
```

The system should support both structured and semantic retrieval.

### Structured retrieval

Useful for exact fields such as:

- standard number
- standard title
- department
- committee
- certification status
- QCO number
- scheme
- licence information
- fees
- dates

### Semantic retrieval

Useful for questions such as:

- Which BIS standard applies to this product?
- What certification process is required?
- What documents are needed?
- Which laboratory can perform this test?
- What happens during renewal?
- Is BIS certification compulsory?

### Hybrid retrieval

Combine structured filters with semantic document retrieval for better precision and coverage.

---

# 14. Source Verification in the Final Assistant

The final assistant should be able to trace important answers to official BIS evidence.

Conceptually:

```text
User Question
      ↓
Retriever
      ↓
BIS Record / Official Document
      ↓
Evidence
      ↓
LLM
      ↓
Answer + Source
```

Information such as:

- fees
- dates
- regulations
- QCO applicability
- certification requirements
- licence validity
- contact information

should be verified against current official sources whenever possible.

---

# 15. Data Quality Rules

## Rule 1 — Never fabricate BIS data

Unknown values should remain unknown.

Prefer:

```json
null
```

over an invented value.

## Rule 2 — Preserve official identity

Do not casually rewrite:

- standard numbers
- official titles
- scheme names
- QCO numbers
- licence identifiers
- official terminology

## Rule 3 — Preserve provenance

Every important record must be traceable to its source.

## Rule 4 — Preserve historical information

Superseded/withdrawn information should not automatically be deleted when it is needed for historical queries.

Use statuses such as:

```text
active
inactive
superseded
withdrawn
draft
unknown
```

## Rule 5 — Schema is not populated evidence

A relationship defined in `relationships.json` is not automatically a verified relationship.

## Rule 6 — Deferred enrichment must remain marked as deferred

Deep individual-standard enrichment was researched/tested but is not complete.

## Rule 7 — Never destroy raw data

Always keep the original collected source data.

---

# 16. Current Resume Point

The exact project checkpoint is:

```text
12,223 validated BIS New Standards records
                    ↓
              NEXT ACTION
                    ↓
        Normalize existing raw data
                    ↓
        Validate normalized dataset
                    ↓
        Create dataset_manifest.json
                    ↓
        Finalize verified relationships
                    ↓
            Dataset v1.0
                    ↓
               MongoDB
                    ↓
                  RAG
```

**Do not restart API discovery.**

**Do not claim the BIS-wide dataset is complete.**

**Do not claim deep standard enrichment is complete.**

---

# 17. Dataset v1.0 Readiness Checklist

Dataset v1.0 is ready when:

- [x] 12,223 raw official BIS records are preserved
- [ ] 12,223 records are normalized using `metadata/schema.json`
- [ ] Stable source identity is retained
- [ ] BIS provenance exists for normalized records
- [ ] No unsupported/fabricated metadata is added
- [ ] Validation confirms record counts
- [ ] Validation confirms unique entity IDs
- [ ] Duplicate standard numbers are documented
- [ ] `output/dataset_manifest.json` exists
- [ ] Verified relationship checkpoint is finalized
- [x] Project is backed up in GitHub

---

# 18. Final Project Goal

The long-term goal is not simply to create a list of BIS standards.

The goal is to build a source-grounded BIS knowledge base capable of answering complex questions across:

- standards
- products
- QCOs
- certification
- registration
- testing
- laboratories
- hallmarking
- regulatory requirements
- procedures
- fees
- licences
- surveillance
- complaints
- consumer services
- offices and contacts

The knowledge base should eventually support multi-step reasoning such as:

```text
Product
   ↓
Applicable Standard
   ↓
Mandatory QCO?
   ↓
Applicable Certification Scheme
   ↓
Testing Requirement
   ↓
Laboratory
   ↓
Certification / Registration
   ↓
Licence
   ↓
Renewal / Surveillance
```

This relationship-driven structure is intended to make the BIS AI assistant more useful than a simple FAQ chatbot.

---

# 19. Handover Summary

## Completed

```text
✓ Project structure
✓ Metadata schema
✓ Master taxonomy
✓ Relationship model
✓ Official source registry
✓ New BIS Standards Portal investigation
✓ BIS API discovery
✓ 18-department discovery
✓ 12,223 New Standards collection
✓ Pagination validation
✓ Record-count validation
✓ Unique-ID validation
✓ Duplicate-number analysis
✓ Detail API research
✓ GitHub backup
```

## Immediate next work

```text
1. Normalize 12,223 records
2. Validate normalized data
3. Create dataset_manifest.json
4. Finalize verified relationships
5. Commit Dataset v1.0
```

## Later work

```text
Standards enrichment
Products
QCOs
Certification
CRS
FMCS
Scheme-X
Laboratories
Testing
Hallmarking
Fees
Procedures
Complaints
Offices / contacts
Regulatory documents
Full relationship graph
MongoDB
Embeddings
Vector search
Hybrid retrieval
Reranking
RAG
Source citations
AI assistant integration
```

---

## Important Project Note

The 12,223-record collection is a **validated foundation**, not the final BIS knowledge base.

The project should continue expanding from this verified base while preserving raw data, provenance and validation history.

The guiding principle is:

> **Official source → raw preservation → normalization → validation → provenance → retrieval → cited answer**
