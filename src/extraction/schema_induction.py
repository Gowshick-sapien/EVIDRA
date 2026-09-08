"""
Schema Induction Engine for EVIDRA 2.0 (Phase P0).

Dynamically discovers the structural financial/operational vocabulary
and primary entity directly from document evidence windows without hardcoded
brittle schemas, preserving exact verbatim surface forms.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.extraction.schemas import EvidenceWindow

GENERIC_ENTITIES: Set[str] = {
    "reporting entity",
    "the company",
    "company",
    "management",
    "total",
    "consolidated",
    "standalone",
    "group",
    "unknown entity",
    "n/a",
    "none",
    "our company",
}

CORPORATE_ENTITY_PATTERNS = [
    re.compile(r"\b([A-Z][A-Za-z0-9&.,\s]{2,45}\s+(?:Limited|Ltd\.?|Corporation|Corp\.?|Inc\.?|LLC|Pvt\.?\s*Ltd\.?))\b"),
    re.compile(r"\b([A-Z][A-Za-z0-9&.,\s]{2,45}\s+(?:Holdings?|Enterprises?|Services?|Logistics?))\b"),
]

HEADER_EXCLUDE_TERMS: Set[str] = {
    "particulars",
    "description",
    "line item",
    "item",
    "sr. no.",
    "sr no",
    "s. no.",
    "notes",
    "note no.",
    "quarter ended",
    "year ended",
    "as at",
    "period ended",
    "total",
    "subtotal",
    "sub-total",
}

FAMILY_KEYWORD_MAP = {
    "REVENUE": [
        "revenue", "turnover", "sales", "topline", "top-line", "income from operations",
        "service revenue", "operating revenue", "gross receipts", "billing"
    ],
    "PROFITABILITY": [
        "profit", "loss", "ebitda", "ebit", "pat", "pbt", "margin", "net income",
        "operating profit", "surplus", "earnings per share", "eps"
    ],
    "EXPENSES": [
        "expense", "cost", "freight", "handling", "employee benefit", "depreciation",
        "amortisation", "amortization", "finance cost", "tax expense", "other expenses",
        "operating cost", "fuel", "rent"
    ],
    "VOLUME": [
        "volume", "shipment", "tonnage", "parcel", "package", "order", "weight",
        "pin codes", "pincodes", "centers", "gateways", "vehicles", "fleet", "clients"
    ],
    "CASH_FLOW": [
        "cash flow", "operating activities", "investing activities", "financing activities",
        "free cash flow", "capital expenditure", "capex"
    ],
    "BALANCE_SHEET": [
        "asset", "liability", "equity", "borrowing", "debt", "net worth", "capital",
        "working capital", "reserves", "provisions", "investments"
    ],
}


class MetricSubtype(BaseModel):
    subtype_name: str
    surface_variants: List[str] = Field(default_factory=list)


class MetricFamily(BaseModel):
    family_name: str
    subtypes: List[MetricSubtype] = Field(default_factory=list)


class DocumentSchema(BaseModel):
    document_id: str
    primary_entity: str
    metric_families: List[MetricFamily] = Field(default_factory=list)

    def find_subtype(self, surface_text: str) -> Optional[MetricSubtype]:
        """Look up a subtype across all families by matching surface variants or name."""
        target = surface_text.strip().lower()
        for fam in self.metric_families:
            for sub in fam.subtypes:
                if sub.subtype_name.lower() == target:
                    return sub
                for var in sub.surface_variants:
                    if var.lower() == target:
                        return sub
        return None


class SchemaInductionEngine:
    """
    Lightweight schema inducer that derives primary entity identities and
    structured metric taxonomies from parsed EvidenceWindows.
    """

    def induce_schema(
        self,
        document_id: str,
        windows: List[EvidenceWindow],
        manifest_entity: Optional[str] = None,
    ) -> DocumentSchema:
        """
        Derive document schema from evidence windows.
        """
        primary_entity = self._resolve_primary_entity(windows, manifest_entity)
        metric_families = self._induce_metric_taxonomies(windows)

        return DocumentSchema(
            document_id=document_id,
            primary_entity=primary_entity,
            metric_families=metric_families,
        )

    def _resolve_primary_entity(
        self,
        windows: List[EvidenceWindow],
        manifest_entity: Optional[str] = None,
    ) -> str:
        """
        Determine the primary corporate entity for the document.
        Manifest entity is trusted if valid, otherwise multi-signal resolution runs.
        """
        if manifest_entity and manifest_entity.strip().lower() not in GENERIC_ENTITIES:
            return manifest_entity.strip()

        entity_counts: Dict[str, int] = {}

        # Scan headers, page headers, section titles, and early windows (first 10)
        early_windows = sorted(windows, key=lambda w: (w.page_number, w.chunk_id))[:15]
        for w in early_windows:
            search_corpus = [
                w.page_header,
                w.section_title,
                w.table_caption,
                w.content[:400],
            ]
            for text in search_corpus:
                if not text:
                    continue
                for pattern in CORPORATE_ENTITY_PATTERNS:
                    matches = pattern.findall(text)
                    for match in matches:
                        clean_candidate = self._clean_entity_candidate(match)
                        if clean_candidate and clean_candidate.lower() not in GENERIC_ENTITIES:
                            entity_counts[clean_candidate] = entity_counts.get(clean_candidate, 0) + 1

        if entity_counts:
            # Pick most frequent candidate
            best_entity = max(entity_counts.items(), key=lambda item: item[1])[0]
            return best_entity

        # Fallback: scan remaining windows
        for w in windows:
            if w.page_header:
                for pattern in CORPORATE_ENTITY_PATTERNS:
                    matches = pattern.findall(w.page_header)
                    for match in matches:
                        clean_candidate = self._clean_entity_candidate(match)
                        if clean_candidate and clean_candidate.lower() not in GENERIC_ENTITIES:
                            entity_counts[clean_candidate] = entity_counts.get(clean_candidate, 0) + 1

        if entity_counts:
            return max(entity_counts.items(), key=lambda item: item[1])[0]

        return "Unknown Entity"

    def _clean_entity_candidate(self, candidate: str) -> str:
        candidate = candidate.strip()
        candidate = re.sub(r"\s+", " ", candidate)
        # Strip leading phrases like "For ", "To ", "By "
        candidate = re.sub(r"^(?:For|To|By|From|In|Of)\s+", "", candidate, flags=re.IGNORECASE)
        return candidate.strip(" ,.-:")

    def _induce_metric_taxonomies(
        self,
        windows: List[EvidenceWindow],
    ) -> List[MetricFamily]:
        """
        Extract row labels from table windows and group into canonical metric families.
        """
        # Map: family_name -> dict(subtype_name -> list of surface variants)
        taxonomy: Dict[str, Dict[str, Set[str]]] = {
            "REVENUE": {},
            "PROFITABILITY": {},
            "EXPENSES": {},
            "VOLUME": {},
            "CASH_FLOW": {},
            "BALANCE_SHEET": {},
            "OPERATIONAL_METRICS": {},
        }

        for w in windows:
            row_labels = self._extract_table_row_labels(w.content)
            for raw_label in row_labels:
                cleaned_label = self._clean_row_label(raw_label)
                if not cleaned_label or cleaned_label.lower() in HEADER_EXCLUDE_TERMS:
                    continue

                family = self._classify_label_family(cleaned_label)
                subtype_key = self._canonicalize_subtype_name(cleaned_label)

                if subtype_key not in taxonomy[family]:
                    taxonomy[family][subtype_key] = set()
                taxonomy[family][subtype_key].add(raw_label.strip())

        metric_families: List[MetricFamily] = []
        for family_name, subtypes_map in taxonomy.items():
            if not subtypes_map:
                continue
            subtypes_list: List[MetricSubtype] = []
            for sub_name, variants in subtypes_map.items():
                subtypes_list.append(
                    MetricSubtype(
                        subtype_name=sub_name,
                        surface_variants=sorted(list(variants)),
                    )
                )
            subtypes_list.sort(key=lambda s: s.subtype_name)
            metric_families.append(
                MetricFamily(
                    family_name=family_name,
                    subtypes=subtypes_list,
                )
            )

        metric_families.sort(key=lambda f: f.family_name)
        return metric_families

    def _extract_table_row_labels(self, content: str) -> List[str]:
        """Extract candidate row labels from markdown table column 0."""
        labels: List[str] = []
        lines = content.splitlines()
        data_rows_started = False

        for line in lines:
            line_str = line.strip()
            if not line_str.startswith("|"):
                continue
            # Divider line check
            if re.match(r"^\|(?:\s*:?-+:?\s*\|)+$", line_str):
                data_rows_started = True
                continue

            if not data_rows_started:
                continue

            # Parse columns
            parts = [col.strip() for col in line_str.strip("|").split("|")]
            if parts:
                col0 = parts[0]
                if col0 and not self._is_numeric_or_empty(col0):
                    labels.append(col0)

        return labels

    def _clean_row_label(self, raw_label: str) -> str:
        """Strip footnotes, bullet numbers, and punctuation."""
        text = raw_label.strip()
        # Remove footnote markers like (1), [2], *, ^
        text = re.sub(r"[\(\[]\d+[\)\]]", "", text)
        text = re.sub(r"[\*\^]", "", text)
        # Remove leading numbers like "1.", "a.", "(i)"
        text = re.sub(r"^(?:[0-9]+|[a-z]|\([0-9ivx]+\))[\.\)]\s*", "", text, flags=re.IGNORECASE)
        # Remove trailing colon
        text = re.sub(r":\s*$", "", text)
        return text.strip()

    def _is_numeric_or_empty(self, text: str) -> bool:
        clean = text.strip().replace(",", "").replace(".", "").replace("-", "").replace("%", "")
        return not text.strip() or clean.isdigit()

    def _classify_label_family(self, label: str) -> str:
        """Classify a line item label into a financial metric family."""
        lower = label.lower()
        for family, keywords in FAMILY_KEYWORD_MAP.items():
            for kw in keywords:
                if kw in lower:
                    return family
        return "OPERATIONAL_METRICS"

    def _canonicalize_subtype_name(self, label: str) -> str:
        """Generate an uppercase canonical slug identifier for the line item."""
        slug = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_").upper()
        return slug or "UNKNOWN_SUBTYPE"
