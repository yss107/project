/**
 * Learning module - stores new insights and updates existing memories
 */

import { MemoryStore } from '../persistence/memory-store';
import { Memory, MemoryType } from '../types/memory';
import { HumanCorrection } from '../types/invoice';
import { ProposedCorrection, MemoryUpdate, AuditTrailEntry } from '../types/output';

export class LearningEngine {
  private readonly REINFORCEMENT_FACTOR = 0.05;
  private readonly WEAKENING_FACTOR = 0.1;
  private readonly MIN_CONFIDENCE = 0.1;
  private readonly MAX_CONFIDENCE = 0.95;

  constructor(private store: MemoryStore) {}

  /**
   * Learn from human corrections
   */
  learnFromCorrections(correction: HumanCorrection): {
    updates: MemoryUpdate[];
    auditTrail: AuditTrailEntry[];
  } {
    const updates: MemoryUpdate[] = [];
    const auditTrail: AuditTrailEntry[] = [];

    for (const corr of correction.corrections) {
      const memoryUpdate = this.createOrUpdateMemory(correction, corr);
      updates.push(memoryUpdate);

      auditTrail.push({
        step: 'learn',
        timestamp: new Date().toISOString(),
        details: `Learned from correction: ${corr.field} (${corr.reason})`,
      });
    }

    return { updates, auditTrail };
  }

  /**
   * Learn from applied corrections (reinforce successful memories)
   */
  reinforceMemories(
    appliedCorrections: ProposedCorrection[],
    wasAccepted: boolean
  ): {
    updates: MemoryUpdate[];
    auditTrail: AuditTrailEntry[];
  } {
    const updates: MemoryUpdate[] = [];
    const auditTrail: AuditTrailEntry[] = [];

    for (const correction of appliedCorrections) {
      if (!correction.memoryId) continue;

      const memory = this.store.getById(correction.memoryId);
      if (!memory) continue;

      if (wasAccepted) {
        const newConfidence = this.reinforceConfidence(memory.confidence);
        this.store.updateMemory(correction.memoryId, {
          confidence: newConfidence,
          successCount: memory.successCount + 1,
        });

        updates.push({
          action: 'reinforced',
          memoryId: correction.memoryId,
          pattern: memory.pattern,
          details: `Confidence increased from ${memory.confidence.toFixed(2)} to ${newConfidence.toFixed(2)}`,
        });

        auditTrail.push({
          step: 'learn',
          timestamp: new Date().toISOString(),
          details: `Reinforced memory #${correction.memoryId}: ${memory.pattern}`,
        });
      } else {
        const newConfidence = this.weakenConfidence(memory.confidence);
        this.store.updateMemory(correction.memoryId, {
          confidence: newConfidence,
          failureCount: memory.failureCount + 1,
        });

        updates.push({
          action: 'weakened',
          memoryId: correction.memoryId,
          pattern: memory.pattern,
          details: `Confidence decreased from ${memory.confidence.toFixed(2)} to ${newConfidence.toFixed(2)}`,
        });

        auditTrail.push({
          step: 'learn',
          timestamp: new Date().toISOString(),
          details: `Weakened memory #${correction.memoryId}: ${memory.pattern}`,
        });
      }
    }

    return { updates, auditTrail };
  }

  /**
   * Create or update memory from human correction
   */
  private createOrUpdateMemory(
    humanCorrection: HumanCorrection,
    correction: any
  ): MemoryUpdate {
    const { vendor, finalDecision } = humanCorrection;
    const { field, reason } = correction;

    // Determine memory type and pattern
    const memoryInfo = this.extractMemoryInfo(field, reason, correction);

    // Check if similar memory exists
    const existingMemories = this.store.findByPattern(memoryInfo.pattern, vendor);

    if (existingMemories.length > 0) {
      // Update existing memory
      const existing = existingMemories[0];
      const newConfidence = this.reinforceConfidence(existing.confidence);
      
      this.store.updateMemory(existing.id!, {
        confidence: newConfidence,
        successCount: existing.successCount + (finalDecision === 'approved' ? 1 : 0),
        failureCount: existing.failureCount + (finalDecision === 'rejected' ? 1 : 0),
      });

      return {
        action: 'reinforced',
        memoryId: existing.id,
        pattern: memoryInfo.pattern,
        details: `Updated existing memory for ${vendor}`,
      };
    } else {
      // Create new memory
      const initialConfidence = finalDecision === 'approved' ? 0.6 : 0.4;

      const memory: Omit<Memory, 'id'> = {
        type: memoryInfo.type,
        vendor,
        pattern: memoryInfo.pattern,
        action: memoryInfo.action,
        confidence: initialConfidence,
        occurrences: 1,
        successCount: finalDecision === 'approved' ? 1 : 0,
        failureCount: finalDecision === 'rejected' ? 1 : 0,
        createdAt: new Date().toISOString(),
        lastUsedAt: new Date().toISOString(),
        lastUpdatedAt: new Date().toISOString(),
      };

      const id = this.store.saveMemory(memory);

      return {
        action: 'created',
        memoryId: id,
        pattern: memoryInfo.pattern,
        details: `Created new ${memoryInfo.type} memory for ${vendor}`,
      };
    }
  }

  /**
   * Extract memory information from correction
   */
  private extractMemoryInfo(
    field: string,
    reason: string,
    correction: any
  ): { type: MemoryType; pattern: string; action: string } {
    const reasonLower = reason.toLowerCase();

    // Check for vendor-specific patterns
    if (reasonLower.includes('leistungsdatum')) {
      return {
        type: 'vendor',
        pattern: 'Leistungsdatum',
        action: 'extract_service_date',
      };
    }

    if (reasonLower.includes('vat') && reasonLower.includes('incl')) {
      return {
        type: 'vendor',
        pattern: 'MwSt. inkl.',
        action: 'recalculate_vat',
      };
    }

    if (reasonLower.includes('skonto')) {
      return {
        type: 'vendor',
        pattern: 'skonto_terms',
        action: 'extract_discount_terms',
      };
    }

    if (reasonLower.includes('currency') && reasonLower.includes('rawtext')) {
      return {
        type: 'vendor',
        pattern: 'currency_in_text',
        action: 'extract_currency',
      };
    }

    if (reasonLower.includes('description') && reasonLower.includes('map')) {
      // Extract description pattern and SKU from reason or correction
      const descMatch = reason.match(/([\w\s/]+)\s+(?:map|to)\s+(?:SKU\s+)?(\w+)/i);
      if (descMatch) {
        return {
          type: 'vendor',
          pattern: 'description_to_sku_mapping',
          action: `${descMatch[1].trim()}->${descMatch[2].trim()}`,
        };
      }
    }

    // Check for correction patterns
    if (field === 'serviceDate' || field.includes('serviceDate')) {
      return {
        type: 'correction',
        pattern: 'missing_service_date',
        action: 'extract_from_raw_text',
      };
    }

    if (field === 'poNumber' || field.includes('poNumber')) {
      return {
        type: 'correction',
        pattern: 'missing_po_number',
        action: 'match_by_items_and_vendor',
      };
    }

    if (field === 'currency') {
      return {
        type: 'correction',
        pattern: 'missing_currency',
        action: 'extract_from_raw_text',
      };
    }

    if (field.includes('qty')) {
      return {
        type: 'correction',
        pattern: 'qty_mismatch',
        action: 'adjust_to_delivery_note',
      };
    }

    if (field.includes('tax') || field.includes('gross')) {
      return {
        type: 'correction',
        pattern: 'tax_included',
        action: 'recalculate_vat',
      };
    }

    // Default to generic correction
    return {
      type: 'correction',
      pattern: field,
      action: 'apply_correction',
    };
  }

  /**
   * Increase confidence with diminishing returns
   */
  private reinforceConfidence(current: number): number {
    const newConfidence = current + (this.REINFORCEMENT_FACTOR * (1 - current));
    return Math.min(this.MAX_CONFIDENCE, newConfidence);
  }

  /**
   * Decrease confidence
   */
  private weakenConfidence(current: number): number {
    const newConfidence = current - this.WEAKENING_FACTOR;
    return Math.max(this.MIN_CONFIDENCE, newConfidence);
  }

  /**
   * Apply confidence decay for unused memories
   */
  applyDecay(): {
    updates: MemoryUpdate[];
    auditTrail: AuditTrailEntry[];
  } {
    const updates: MemoryUpdate[] = [];
    const auditTrail: AuditTrailEntry[] = [];

    const allMemories = this.store.getAllMemories();
    const now = new Date();
    const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

    for (const memory of allMemories) {
      const lastUsed = new Date(memory.lastUsedAt);
      
      // Apply decay if not used in 30 days
      if (lastUsed < thirtyDaysAgo) {
        const decayFactor = 0.02; // 2% decay per month
        const newConfidence = Math.max(
          this.MIN_CONFIDENCE,
          memory.confidence - decayFactor
        );

        if (newConfidence !== memory.confidence) {
          this.store.updateMemory(memory.id!, { confidence: newConfidence });

          updates.push({
            action: 'weakened',
            memoryId: memory.id,
            pattern: memory.pattern,
            details: `Decay applied: confidence decreased from ${memory.confidence.toFixed(2)} to ${newConfidence.toFixed(2)}`,
          });
        }
      }
    }

    if (updates.length > 0) {
      auditTrail.push({
        step: 'learn',
        timestamp: new Date().toISOString(),
        details: `Applied decay to ${updates.length} unused memories`,
      });
    }

    return { updates, auditTrail };
  }
}
