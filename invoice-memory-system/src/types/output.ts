/**
 * Output types for the decision system
 */

export interface AuditTrailEntry {
  step: 'recall' | 'apply' | 'decide' | 'learn';
  timestamp: string;
  details: string;
}

export interface ProposedCorrection {
  field: string;
  currentValue: any;
  proposedValue: any;
  reason: string;
  confidence: number;
  memoryId?: number;
}

export interface MemoryUpdate {
  action: 'created' | 'reinforced' | 'weakened' | 'applied';
  memoryId?: number;
  pattern: string;
  details: string;
}

export interface ProcessingResult {
  normalizedInvoice: any;
  proposedCorrections: ProposedCorrection[];
  requiresHumanReview: boolean;
  reasoning: string;
  confidenceScore: number;
  memoryUpdates: MemoryUpdate[];
  auditTrail: AuditTrailEntry[];
}
