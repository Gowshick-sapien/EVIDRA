from __future__ import annotations

import re
from typing import Literal, Optional
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from src.llm.provider import ReasoningService


class FinancialContext(BaseModel):
    """Multidimensional financial qualifiers disambiguating reporting statements."""
    accounting_basis: Literal["GAAP", "NON_GAAP", "IFRS", "UNKNOWN"] = Field(
        default="UNKNOWN", description="Financial accounting framework"
    )
    organizational_scope: Literal["CONSOLIDATED", "STANDALONE", "SEGMENT", "UNKNOWN"] = Field(
        default="UNKNOWN", description="Reporting boundary"
    )
    filing_type: Literal["ANNUAL_REPORT", "PROSPECTUS", "QUARTERLY_REPORT", "PRESS_RELEASE", "UNKNOWN"] = Field(
        default="UNKNOWN", description="Source document publication type"
    )
    version_status: Literal["INITIAL", "RESTATED", "AMENDED", "UNKNOWN"] = Field(
        default="INITIAL", description="Filing iteration or restatement version"
    )
    segment_name: Optional[str] = Field(default=None, description="Operating segment if applicable")


class ContextResolverAgent:
    """Disambiguates accounting basis, organizational scope, filing type, and restatement status."""

    def __init__(self, reasoning_service: Optional[ReasoningService] = None):
        self.llm = reasoning_service

    @staticmethod
    def resolve_deterministically(
        statement: str,
        chunk_content: str,
        filename: str = "",
    ) -> FinancialContext:
        """High-speed deterministic qualifier analysis based on accounting terminology."""
        combined = f"{statement} {chunk_content} {filename}".lower()

        # 1. Accounting Basis
        basis: Literal["GAAP", "NON_GAAP", "IFRS", "UNKNOWN"] = "UNKNOWN"
        if re.search(r"\b(non-gaap|adjusted ebitda|adjusted revenue|pro forma)\b", combined):
            basis = "NON_GAAP"
        elif re.search(r"\b(ifrs|ind as|international financial reporting)\b", combined):
            basis = "IFRS"
        elif re.search(r"\b(gaap|as per accounting standard)\b", combined):
            basis = "GAAP"

        # 2. Organizational Scope
        scope: Literal["CONSOLIDATED", "STANDALONE", "SEGMENT", "UNKNOWN"] = "UNKNOWN"
        if re.search(r"\b(consolidated|group level)\b", combined):
            scope = "CONSOLIDATED"
        elif re.search(r"\b(standalone|parent company only)\b", combined):
            scope = "STANDALONE"
        elif re.search(r"\b(segment|express parcel|part truckload|supply chain)\b", combined):
            scope = "SEGMENT"

        # 3. Filing Type
        filing: Literal["ANNUAL_REPORT", "PROSPECTUS", "QUARTERLY_REPORT", "PRESS_RELEASE", "UNKNOWN"] = "UNKNOWN"
        if re.search(r"\b(prospectus|red herring|drhp|rhp|ipo)\b", combined):
            filing = "PROSPECTUS"
        elif re.search(r"\b(annual report|10-k|form 20-f)\b", combined):
            filing = "ANNUAL_REPORT"
        elif re.search(r"\b(quarterly report|10-q|q[1-4] results)\b", combined):
            filing = "QUARTERLY_REPORT"
        elif re.search(r"\b(press release|media release)\b", combined):
            filing = "PRESS_RELEASE"

        # 4. Version / Restatement Status
        version: Literal["INITIAL", "RESTATED", "AMENDED", "UNKNOWN"] = "INITIAL"
        if re.search(r"\b(restated|restatement of|as restated)\b", combined):
            version = "RESTATED"
        elif re.search(r"\b(amended|10-k/a|revision)\b", combined):
            version = "AMENDED"

        return FinancialContext(
            accounting_basis=basis,
            organizational_scope=scope,
            filing_type=filing,
            version_status=version,
        )

    def resolve_context(
        self,
        statement: str,
        chunk_content: str,
        filename: str = "",
    ) -> FinancialContext:
        """Resolve financial qualifiers using fast deterministic rules with LLM fallback."""
        ctx = self.resolve_deterministically(statement, chunk_content, filename)
        
        # If any primary dimension was resolved deterministically, return immediately
        if ctx.accounting_basis != "UNKNOWN" or ctx.organizational_scope != "UNKNOWN":
            return ctx

        # If LLM is provided and context is ambiguous, query reasoning service
        if self.llm:
            try:
                prompt = (
                    f"STATEMENT: \"{statement}\"\n"
                    f"EXCERPT CONTEXT:\n{chunk_content[:600]}\n"
                    f"FILENAME: {filename}\n\n"
                    f"Extract the accounting basis, organizational scope, filing type, and restatement status."
                )
                return self.llm.generate_structured(prompt, FinancialContext, max_retries=1)
            except Exception:
                pass

        return ctx
