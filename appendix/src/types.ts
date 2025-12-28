// Core data types
export interface LineItem {
  sku: string | null;
  description: string;
  qty: number;
  unitPrice: number;
}

export interface InvoiceFields {
  invoiceNumber: string;
  invoiceDate: string;
  serviceDate?: string | null;
  currency: string | null;
  poNumber: string | null;
  netTotal: number;
  taxRate: number;
  taxTotal: number;
  grossTotal: number;
  lineItems: LineItem[];
  discountTerms?: string | null;
}

export interface Invoice {
  invoiceId: string;
  vendor: string;
  fields: InvoiceFields;
  confidence: number;
  rawText: string;
}

export interface PurchaseOrder {
  poNumber: string;
  vendor: string;
  date: string;
  lineItems: Array<{
    sku: string;
    qty: number;
    unitPrice: number;
  }>;
}

export interface DeliveryNote {
  dnNumber: string;
  vendor: string;
  poNumber: string;
  date: string;
  lineItems: Array<{
    sku: string;
    qtyDelivered: number;
  }>;
}

export interface HumanCorrection {
  invoiceId: string;
  vendor: string;
  corrections: Array<{
    field: string;
    from: any;
    to: any;
    reason: string;
  }>;
  finalDecision: 'approved' | 'rejected';
}

// Memory types
export interface VendorMemory {
  id?: number;
  vendor: string;
  pattern: string;
  fieldMapping: string;
  confidence: number;
  usageCount: number;
  successCount: number;
  lastUsed: string;
  created: string;
}

export interface CorrectionMemory {
  id?: number;
  vendor: string;
  pattern: string;
  correctionType: string;
  correctionLogic: string;
  confidence: number;
  usageCount: number;
  successCount: number;
  lastUsed: string;
  created: string;
}

export interface ResolutionMemory {
  id?: number;
  vendor: string;
  invoiceNumber: string;
  decision: 'approved' | 'rejected' | 'escalated';
  corrections: string;
  timestamp: string;
}

export interface DuplicateMemory {
  id?: number;
  vendor: string;
  invoiceNumber: string;
  invoiceDate: string;
  invoiceId: string;
  timestamp: string;
}

// Output contract
export interface ProposedCorrection {
  field: string;
  currentValue: any;
  proposedValue: any;
  reason: string;
  confidence: number;
  source: string;
}

export interface AuditTrailEntry {
  step: 'recall' | 'apply' | 'decide' | 'learn';
  timestamp: string;
  details: string;
}

export interface MemoryUpdate {
  type: 'vendor' | 'correction' | 'resolution' | 'duplicate';
  action: 'create' | 'update' | 'reinforce';
  details: string;
}

export interface ProcessingResult {
  normalizedInvoice: InvoiceFields;
  proposedCorrections: ProposedCorrection[];
  requiresHumanReview: boolean;
  reasoning: string;
  confidenceScore: number;
  memoryUpdates: MemoryUpdate[];
  auditTrail: AuditTrailEntry[];
}
