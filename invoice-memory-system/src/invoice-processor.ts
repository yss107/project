/**
 * Main invoice processor - orchestrates recall, apply, decide, and learn
 */

import { MemoryStore } from './persistence/memory-store';
import { MemoryRecall } from './memory/recall';
import { MemoryApply, ApplyContext } from './memory/apply';
import { DecisionEngine, DecisionContext } from './decision/decision-engine';
import { LearningEngine } from './memory/learning';
import { ExtractedInvoice, PurchaseOrder, DeliveryNote, HumanCorrection } from './types/invoice';
import { ProcessingResult, AuditTrailEntry } from './types/output';

export class InvoiceProcessor {
  private store: MemoryStore;
  private recall: MemoryRecall;
  private apply: MemoryApply;
  private decisionEngine: DecisionEngine;
  private learningEngine: LearningEngine;

  constructor(dbPath?: string) {
    this.store = new MemoryStore(dbPath);
    this.recall = new MemoryRecall(this.store);
    this.apply = new MemoryApply();
    this.decisionEngine = new DecisionEngine();
    this.learningEngine = new LearningEngine(this.store);
  }

  /**
   * Process an invoice through the complete pipeline
   */
  processInvoice(
    invoice: ExtractedInvoice,
    purchaseOrders: PurchaseOrder[],
    deliveryNotes: DeliveryNote[]
  ): ProcessingResult {
    const allAuditTrail: AuditTrailEntry[] = [];

    // Step 1: Recall relevant memories
    const { memories, auditTrail: recallAudit } = this.recall.recallMemories(invoice);
    allAuditTrail.push(...recallAudit);

    // Step 2: Apply memories to generate corrections
    const applyContext: ApplyContext = {
      invoice,
      memories,
      purchaseOrders,
      deliveryNotes,
    };

    const { 
      corrections, 
      normalizedInvoice, 
      auditTrail: applyAudit 
    } = this.apply.applyMemories(applyContext);
    allAuditTrail.push(...applyAudit);

    // Step 3: Make decision
    const decisionContext: DecisionContext = {
      invoice,
      corrections,
      memories,
      normalizedInvoice,
    };

    const {
      requiresHumanReview,
      reasoning,
      confidenceScore,
      auditTrail: decideAudit,
    } = this.decisionEngine.decide(decisionContext);
    allAuditTrail.push(...decideAudit);

    // Step 4: Mark memories as used
    const memoryUpdates = memories.map(m => {
      if (m.id) {
        this.store.markUsed(m.id);
      }
      return {
        action: 'applied' as const,
        memoryId: m.id,
        pattern: m.pattern,
        details: `Applied memory for ${invoice.vendor}`,
      };
    });

    return {
      normalizedInvoice,
      proposedCorrections: corrections,
      requiresHumanReview,
      reasoning,
      confidenceScore,
      memoryUpdates,
      auditTrail: allAuditTrail,
    };
  }

  /**
   * Learn from human feedback
   */
  learnFromHumanCorrection(correction: HumanCorrection): void {
    const { updates, auditTrail } = this.learningEngine.learnFromCorrections(correction);
    
    // Log learning results
    console.log(`\n📚 Learning from human corrections for ${correction.invoiceId}:`);
    for (const update of updates) {
      console.log(`  - ${update.action.toUpperCase()}: ${update.details}`);
    }
  }

  /**
   * Check for potential duplicates
   */
  checkForDuplicates(
    invoice: ExtractedInvoice,
    allInvoices: ExtractedInvoice[]
  ): ExtractedInvoice | null {
    for (const existing of allInvoices) {
      if (existing.invoiceId === invoice.invoiceId) continue;

      // Same vendor and invoice number
      if (
        existing.vendor === invoice.vendor &&
        existing.fields.invoiceNumber === invoice.fields.invoiceNumber
      ) {
        // Check if dates are close (within 7 days)
        const date1 = new Date(this.parseDate(existing.fields.invoiceDate));
        const date2 = new Date(this.parseDate(invoice.fields.invoiceDate));
        const daysDiff = Math.abs(date1.getTime() - date2.getTime()) / (1000 * 60 * 60 * 24);

        if (daysDiff <= 7) {
          return existing;
        }
      }
    }

    return null;
  }

  /**
   * Parse various date formats
   */
  private parseDate(dateStr: string): string {
    // Handle DD.MM.YYYY
    if (dateStr.includes('.')) {
      const [day, month, year] = dateStr.split('.');
      return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }

    // Handle DD-MM-YYYY
    if (dateStr.match(/^\d{2}-\d{2}-\d{4}$/)) {
      const [day, month, year] = dateStr.split('-');
      return `${year}-${month}-${day}`;
    }

    // Already in YYYY-MM-DD
    return dateStr;
  }

  /**
   * Get all memories (for debugging)
   */
  getAllMemories() {
    return this.store.getAllMemories();
  }

  /**
   * Close database connection
   */
  close(): void {
    this.store.close();
  }
}
