/**
 * Memory types for the learning system
 */

export type MemoryType = 'vendor' | 'correction' | 'resolution';

export interface BaseMemory {
  id?: number;
  type: MemoryType;
  vendor: string;
  pattern: string;
  action: string;
  confidence: number;
  occurrences: number;
  successCount: number;
  failureCount: number;
  createdAt: string;
  lastUsedAt: string;
  lastUpdatedAt: string;
}

export interface VendorMemory extends BaseMemory {
  type: 'vendor';
  // Pattern examples: "Leistungsdatum", "MwSt. inkl.", "Seefracht"
}

export interface CorrectionMemory extends BaseMemory {
  type: 'correction';
  // Pattern examples: "qty_mismatch", "missing_po", "tax_included"
}

export interface ResolutionMemory extends BaseMemory {
  type: 'resolution';
  resolutionType: 'approved' | 'rejected';
  // Tracks how discrepancies were resolved
}

export type Memory = VendorMemory | CorrectionMemory | ResolutionMemory;
