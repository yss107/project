/**
 * Core types for invoice processing and memory system
 */

export interface LineItem {
  sku: string | null;
  description: string;
  qty: number;
  unitPrice: number;
  qtyDelivered?: number;
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

export interface ExtractedInvoice {
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

export interface Correction {
  field: string;
  from: any;
  to: any;
  reason: string;
}

export interface HumanCorrection {
  invoiceId: string;
  vendor: string;
  corrections: Correction[];
  finalDecision: 'approved' | 'rejected';
}
