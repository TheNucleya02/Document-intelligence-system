from pydantic import BaseModel, Field
from typing import List, Optional

class ContractActionItem(BaseModel):
    description: str = Field(..., description="The specific obligation or action required.")
    due_date: Optional[str] = Field(None, description="The deadline mentioned, if any.")
    responsible_party: Optional[str] = Field(None, description="Who is responsible (e.g., 'Client', 'Provider').")

class ContractRisk(BaseModel):
    risk_description: str = Field(..., description="A potential risk or liability identified.")
    severity: str = Field(..., description="Low, Medium, or High.")

class DocumentAnalysis(BaseModel):
    summary: str = Field(..., description="A brief executive summary of the document.")
    action_items: List[ContractActionItem]
    risks: List[ContractRisk]
    monetary_values: List[str] = Field(..., description="Any currency amounts mentioned (e.g., '$50,000').")