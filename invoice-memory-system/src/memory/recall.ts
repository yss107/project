/**
 * Memory recall module - retrieves relevant past learnings
 */

import { MemoryStore } from '../persistence/memory-store';
import { Memory } from '../types/memory';
import { ExtractedInvoice } from '../types/invoice';
import { AuditTrailEntry } from '../types/output';

export class MemoryRecall {
  constructor(private store: MemoryStore) {}

  /**
   * Recall all relevant memories for an invoice
   */
  recallMemories(invoice: ExtractedInvoice): {
    memories: Memory[];
    auditTrail: AuditTrailEntry[];
  } {
    const auditTrail: AuditTrailEntry[] = [];
    const now = new Date().toISOString();

    // Get all memories for this vendor
    const vendorMemories = this.store.getMemories(invoice.vendor);

    auditTrail.push({
      step: 'recall',
      timestamp: now,
      details: `Retrieved ${vendorMemories.length} memories for vendor: ${invoice.vendor}`,
    });

    // Filter memories based on relevance to this invoice
    const relevantMemories = this.filterRelevantMemories(invoice, vendorMemories);

    auditTrail.push({
      step: 'recall',
      timestamp: new Date().toISOString(),
      details: `Found ${relevantMemories.length} relevant memories after filtering`,
    });

    return { memories: relevantMemories, auditTrail };
  }

  /**
   * Filter memories based on invoice context
   */
  private filterRelevantMemories(
    invoice: ExtractedInvoice,
    memories: Memory[]
  ): Memory[] {
    const relevant: Memory[] = [];

    for (const memory of memories) {
      // Apply confidence threshold
      if (memory.confidence < 0.3) continue;

      // Check if pattern appears in rawText or is contextually relevant
      const isRelevant = this.isMemoryRelevant(invoice, memory);

      if (isRelevant) {
        relevant.push(memory);
      }
    }

    // Sort by confidence descending
    return relevant.sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Determine if a memory is relevant to the current invoice
   */
  private isMemoryRelevant(invoice: ExtractedInvoice, memory: Memory): boolean {
    const rawTextLower = invoice.rawText.toLowerCase();
    const patternLower = memory.pattern.toLowerCase();

    // Check if pattern appears in raw text
    if (rawTextLower.includes(patternLower)) {
      return true;
    }

    // Check contextual relevance based on memory type
    switch (memory.type) {
      case 'vendor':
        // Vendor memories are always relevant for the same vendor
        return true;

      case 'correction':
        // Check if the correction pattern matches current issue
        return this.isCorrectionRelevant(invoice, memory);

      case 'resolution':
        // Resolution memories are generally relevant for similar scenarios
        return true;

      default:
        return false;
    }
  }

  /**
   * Check if a correction memory is relevant
   */
  private isCorrectionRelevant(invoice: ExtractedInvoice, memory: Memory): boolean {
    const pattern = memory.pattern;

    // Check for specific correction patterns
    if (pattern === 'missing_service_date' && !invoice.fields.serviceDate) {
      return true;
    }

    if (pattern === 'missing_po_number' && !invoice.fields.poNumber) {
      return true;
    }

    if (pattern === 'missing_currency' && !invoice.fields.currency) {
      return true;
    }

    if (pattern === 'tax_included' && 
        (invoice.rawText.toLowerCase().includes('inkl') || 
         invoice.rawText.toLowerCase().includes('incl'))) {
      return true;
    }

    if (pattern === 'qty_mismatch') {
      return true; // Always relevant as we need to check quantities
    }

    if (pattern === 'skonto_terms' && 
        invoice.rawText.toLowerCase().includes('skonto')) {
      return true;
    }

    if (pattern === 'description_to_sku_mapping') {
      // Check if any line items are missing SKU
      return invoice.fields.lineItems.some(item => !item.sku);
    }

    return false;
  }
}
