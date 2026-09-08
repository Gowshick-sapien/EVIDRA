# EVIDRA: 3-Minute Video Presentation Plan and Script

## Professional Video Guide for Evaluators, Examiners, and Technical Reviewers

---

## 1. Executive Strategy: The 3-Minute Time Budget

In a 3-minute (180-second) video presentation, conciseness and pacing are critical. At a professional speaking cadence of **130 to 135 words per minute**, the entire script must not exceed **400 to 410 words**. 

### 180-Second Segment Allocation:

| Segment | Timestamp | Duration | Core Objective | Word Budget |
| :--- | :--- | :--- | :--- | :--- |
| **1. Introduction** | 0:00 - 0:15 | 15s | Name, Registration Number, Project Title | ~35 words |
| **2. Problem Statement** | 0:15 - 0:45 | 30s | Why conventional RAG and LLMs fail on corporate filings | ~65 words |
| **3. Proposed Solution** | 0:45 - 1:15 | 30s | The 4-Gate resolution engine and Zero-LLM verdict policy | ~70 words |
| **4. Core Architecture** | 1:15 - 1:45 | 30s | The 4 operational layers and adversarial tournament | ~65 words |
| **5. Live Execution Demo** | 1:45 - 2:40 | 55s | CLI run, `summary.md`, `contradictions.md`, SQLite ledger | ~120 words |
| **6. Verification & Conclusion** | 2:40 - 3:00 | 20s | 110 passing automated tests and closing statement | ~45 words |
| **Total** | **0:00 - 3:00** | **180s** | **Complete Technical Walkthrough** | **~400 words** |

---

## 2. What Were You Missing? (Key Evaluation Differentiators)

To maximize your score with academic examiners and technical evaluators, ensure you include two critical points that were not in your initial outline:

1. **The Four Canonical Discrepancy Outcomes:** Evaluators want to know what the output categories are. Explicitly state the four outcomes: **CORROBORATED**, **CONTRADICTION**, **RECONCILED**, and **UNRESOLVED**.
2. **The Zero-LLM Deterministic Verdict Gate:** Evaluators will ask, *"How do you prevent hallucinations?"* Explicitly state that while local LLMs extract candidate facts and draft hypotheses, **all final verdicts are computed by deterministic pure Python truth tables**, making the decision engine immune to token drift and hallucinations.

---

## 3. Verbatim Speaking Script with Screen Cues

Below is your word-for-word spoken script. Follow the on-screen cues precisely to ensure your visuals remain perfectly synchronized with your voice.

---

### Segment 1: Introduction (0:00 - 0:15 | 15 Seconds)
- **On Screen:** Title slide or the top of root [`README.md`](file:///d:/projects/superjoin/EVIDRA/README.md) showing project title, your name, and registration number.
- **Spoken Words:**
  > "Hello everyone. My name is [Your Full Name], registration number [Your Reg Number]. Today I am presenting EVIDRA, an evidence-driven knowledge layer for multi-document fact validation and financial reconciliation."

---

### Segment 2: Problem Statement (0:15 - 0:45 | 30 Seconds)
- **On Screen:** Switch to [`docs/PROPOSED_SOLUTION.md`](file:///d:/projects/superjoin/EVIDRA/docs/PROPOSED_SOLUTION.md) Section 1 ("Executive Summary: The Business and Technical Problem").
- **Spoken Words:**
  > "When financial analysts and auditors evaluate corporate disclosures across multiple filings like prospectuses and annual reports, determining whether numbers agree or conflict is critical. Conventional RAG pipelines fail here because they split tables blindly, lose header units, compare incompatible metrics like margins with revenues, and hallucinate false contradictions. When context is missing, generative chatbots guess rather than admitting uncertainty."

---

### Segment 3: Proposed Solution and Epistemic Invariants (0:45 - 1:15 | 30 Seconds)
- **On Screen:** Scroll to [`docs/PROPOSED_SOLUTION.md`](file:///d:/projects/superjoin/EVIDRA/docs/PROPOSED_SOLUTION.md) Section 2 and the 4 Canonical Outcomes table.
- **Spoken Words:**
  > "EVIDRA solves this by establishing that the document itself is the guide. Every extracted claim is anchored to physical PDF bounding box coordinates. Comparisons pass four sequential isolation gates: Canonical Entity, Temporal Period, Measurement Type, and Accounting Context. Crucially, final verdicts are decided by deterministic Python truth tables, completely excluding generative models from the decision gate to guarantee zero hallucinations."

---

### Segment 4: 4-Layer System Architecture (1:15 - 1:45 | 30 Seconds)
- **On Screen:** Switch to [`docs/developer/ARCHITECTURE_README.md`](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_README.md) Section 3 ("System Architecture" 4-Layer ASCII Diagram).
- **Spoken Words:**
  > "The architecture operates across four distinct layers. Layer 1 extracts visual layout topology and preserves 100 percent of tabular grids. Layer 2 derives dynamic schemas and fact identity signatures with dimensional measurement typing. Layer 3 executes an evidence sufficiency gate, specialist validators, and an adversarial reasoning tournament. Layer 4 persists every observation, candidate fact, and relationship edge to a relational SQLite WAL ledger."

---

### Segment 5: Live Execution Showcase & Output Walkthrough (1:45 - 2:40 | 55 Seconds)
- **On Screen:** 
  1. *[1:45 - 2:00]* Terminal showing the CLI command executing:  
     `python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 15`
  2. *[2:00 - 2:15]* Switch to VS Code opening [`runs/JOB-20260908-133430-8f0093/reports/summary.md`](file:///d:/projects/superjoin/EVIDRA/runs/JOB-20260908-133430-8f0093/reports/summary.md).
  3. *[2:15 - 2:30]* Switch tab to [`runs/JOB-20260908-133430-8f0093/reports/contradictions.md`](file:///d:/projects/superjoin/EVIDRA/runs/JOB-20260908-133430-8f0093/reports/contradictions.md).
  4. *[2:30 - 2:40]* Quick terminal command showing SQLite query:  
     `sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT verdict, decision_strength, count(*) FROM decisions GROUP BY verdict, decision_strength;"`
- **Spoken Words:**
  > "Let us see the system in action. Running the EVIDRA CLI on the Delhivery IPO prospectus excerpt evaluates 15 candidate chunks. The pipeline extracts 48 claims and renders four audited outcomes. In `summary.md`, we observe 3 corroborated facts, 1 genuine contradiction, and 44 single-source claims safely isolated as UNRESOLVED. In `contradictions.md`, conflicting intragroup restatement rows at negative 1.98 and negative 5.67 million are flagged side-by-side with exact coordinates and refuted reconciliation hypotheses. Finally, in SQLite, every relationship edge and calculated variance is fully auditable."

---

### Segment 6: Verification & Conclusion (2:40 - 3:00 | 20 Seconds)
- **On Screen:** Terminal running `pytest tests/ -q` or displaying the 110 passed summary.
- **Spoken Words:**
  > "The entire EVIDRA codebase is validated by a rigorous test suite of 110 passing automated tests covering unit logic, API contracts, and evaluation scenarios. By anchoring claims to coordinate provenance and enforcing deterministic adjudication, EVIDRA provides a trustworthy, production-grade fact knowledge layer. Thank you."

---

## 4. Pre-Recording Staging Checklist

To ensure your video flows smoothly without pausing or searching for files:

### A. Windows to Prepare in Advance:
1. **Window 1: VS Code (Main Presentation Window)**
   - Tab 1: [`README.md`](file:///d:/projects/superjoin/EVIDRA/README.md) (Scrolled to top)
   - Tab 2: [`docs/PROPOSED_SOLUTION.md`](file:///d:/projects/superjoin/EVIDRA/docs/PROPOSED_SOLUTION.md) (Scrolled to Section 1 & 2)
   - Tab 3: [`docs/developer/ARCHITECTURE_README.md`](file:///d:/projects/superjoin/EVIDRA/docs/developer/ARCHITECTURE_README.md) (Scrolled to 4-Layer ASCII Diagram)
   - Tab 4: `runs/JOB-20260908-133430-8f0093/reports/summary.md`
   - Tab 5: `runs/JOB-20260908-133430-8f0093/reports/contradictions.md`

2. **Window 2: Terminal 1 (CLI Execution Showcase)**
   - Pre-type the command so you only have to press Enter:
     ```powershell
     python -m src.cli.main process sample_docs/01-delhivery-prospectus-2022-excerpt.pdf --max-chunks 15
     ```
   *(Tip: If you do not want to wait for local Ollama extraction during the 55s window, you can run it beforehand and showcase the completed terminal output, or run with `--skip-llm` for immediate layout demonstration).*

3. **Window 3: Terminal 2 (SQLite Query & Test Suite)**
   - Have the SQLite query pre-typed:
     ```powershell
     sqlite3 runs/JOB-20260908-133430-8f0093/ledger.db "SELECT verdict, decision_strength, count(*) FROM decisions GROUP BY verdict, decision_strength;"
     ```
   - Have the test command ready to execute:
     ```powershell
     pytest tests/ -q
     ```

### B. Screen Recording Configuration:
- **Resolution:** 1080p (1920x1080) at 30 or 60 FPS.
- **Audio:** Crisp microphone without background echo or fan noise.
- **Font Size:** Zoom VS Code to 120% (`Ctrl + =`) so text and tables are easily readable on smaller laptop screens.
- **Clean Desktop:** Hide desktop icons and close background messaging apps.
