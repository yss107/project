import { MemoryDatabase } from './database';
import {
  Invoice,
  PurchaseOrder,
  DeliveryNote,
  HumanCorrection,
  ProcessingResult,
  ProposedCorrection,
  AuditTrailEntry,
  MemoryUpdate,
  InvoiceFields,
  VendorMemory,
  CorrectionMemory,
  ResolutionMemory
} from './types';

export class MemoryEngine {
  private db: MemoryDatabase;
  private confidenceThreshold = 0.7;

  constructor(db: MemoryDatabase) {
    this.db = db;
  }

  processInvoice(
    invoice: Invoice,
    purchaseOrders: PurchaseOrder[],
    deliveryNotes: DeliveryNote[]
  ): ProcessingResult {
    const auditTrail: AuditTrailEntry[] = [];
    const proposedCorrections: ProposedCorrection[] = [];
    const memoryUpdates: MemoryUpdate[] = [];

    // Step 1: Recall relevant memories
    auditTrail.push({
      step: 'recall',
      timestamp: new Date().toISOString(),
      details: `Recalling memories for vendor: ${invoice.vendor}`
    });

    const vendorMemories = this.db.getVendorMemories(invoice.vendor);
    const correctionMemories = this.db.getCorrectionMemories(invoice.vendor);
    const resolutionMemories = this.db.getResolutionMemories(invoice.vendor);

    // Step 2: Check for duplicates
    const duplicates = this.db.findDuplicates(
      invoice.vendor,
      invoice.fields.invoiceNumber,
      invoice.fields.invoiceDate
    );

    if (duplicates.length > 0) {
      auditTrail.push({
        step: 'recall',
        timestamp: new Date().toISOString(),
        details: `Duplicate invoice detected! Same vendor + invoiceNumber already seen: ${duplicates.map(d => d.invoiceId).join(', ')}`
      });
    }

    // Step 3: Apply vendor-specific patterns
    auditTrail.push({
      step: 'apply',
      timestamp: new Date().toISOString(),
      details: `Applying ${vendorMemories.length} vendor memories and ${correctionMemories.length} correction memories`
    });

    const normalizedInvoice = { ...invoice.fields };
    let totalConfidence = invoice.confidence;
    let correctionCount = 0;

    // Apply vendor memories (field mappings)
    for (const memory of vendorMemories) {
      if (memory.confidence >= this.confidenceThreshold) {
        const correction = this.applyVendorMemory(memory, invoice, normalizedInvoice);
        if (correction) {
          proposedCorrections.push(correction);
          correctionCount++;
        }
      }
    }

    // Apply correction memories (tax, currency, etc.)
    for (const memory of correctionMemories) {
      if (memory.confidence >= this.confidenceThreshold) {
        const correction = this.applyCorrectionMemory(memory, invoice, normalizedInvoice);
        if (correction) {
          proposedCorrections.push(correction);
          correctionCount++;
        }
      }
    }

    // Try to match PO if missing
    if (!normalizedInvoice.poNumber && purchaseOrders.length > 0) {
      const poMatch = this.matchPurchaseOrder(invoice, purchaseOrders);
      if (poMatch) {
        proposedCorrections.push(poMatch);
        correctionCount++;
      }
    }

    // Step 4: Decide whether to auto-accept, escalate, or reject
    auditTrail.push({
      step: 'decide',
      timestamp: new Date().toISOString(),
      details: `Making decision based on ${proposedCorrections.length} proposed corrections`
    });

    const decision = this.makeDecision(
      invoice,
      normalizedInvoice,
      proposedCorrections,
      duplicates,
      resolutionMemories
    );

    // Apply high-confidence corrections to normalized invoice
    for (const correction of proposedCorrections) {
      if (correction.confidence >= this.confidenceThreshold) {
        this.applyCorrection(normalizedInvoice, correction);
      }
    }

    const result: ProcessingResult = {
      normalizedInvoice,
      proposedCorrections,
      requiresHumanReview: decision.requiresHumanReview,
      reasoning: decision.reasoning,
      confidenceScore: decision.confidenceScore,
      memoryUpdates,
      auditTrail
    };

    return result;
  }

  private applyVendorMemory(
    memory: VendorMemory,
    invoice: Invoice,
    normalizedInvoice: InvoiceFields
  ): ProposedCorrection | null {
    // Check if pattern matches in rawText
    if (!invoice.rawText.includes(memory.pattern)) {
      return null;
    }

    const mapping = JSON.parse(memory.fieldMapping);
    const field = mapping.targetField;
    const currentValue = (normalizedInvoice as any)[field];

    // Only propose if current value is null or undefined
    if (currentValue !== null && currentValue !== undefined) {
      return null;
    }

    // Extract value from rawText
    const extractedValue = this.extractValueFromPattern(invoice.rawText, memory.pattern, mapping);
    if (!extractedValue) {
      return null;
    }

    return {
      field,
      currentValue,
      proposedValue: extractedValue,
      reason: `Vendor pattern learned: "${memory.pattern}" maps to ${field}`,
      confidence: memory.confidence,
      source: 'vendor_memory'
    };
  }

  private applyCorrectionMemory(
    memory: CorrectionMemory,
    invoice: Invoice,
    normalizedInvoice: InvoiceFields
  ): ProposedCorrection | null {
    // Check if pattern matches
    if (!invoice.rawText.toLowerCase().includes(memory.pattern.toLowerCase())) {
      return null;
    }

    const logic = JSON.parse(memory.correctionLogic);

    if (memory.correctionType === 'vat_included') {
      // Recalculate tax when prices include VAT
      const grossTotal = normalizedInvoice.grossTotal;
      const taxRate = normalizedInvoice.taxRate;
      const netTotal = grossTotal / (1 + taxRate);
      const taxTotal = grossTotal - netTotal;

      return {
        field: 'grossTotal',
        currentValue: normalizedInvoice.grossTotal,
        proposedValue: grossTotal,
        reason: `Vendor uses VAT-inclusive pricing (pattern: "${memory.pattern}"). Recalculated net=${netTotal.toFixed(2)}, tax=${taxTotal.toFixed(2)}`,
        confidence: memory.confidence,
        source: 'correction_memory'
      };
    } else if (memory.correctionType === 'currency_extraction') {
      // Extract currency from rawText
      if (normalizedInvoice.currency === null) {
        const currencyMatch = invoice.rawText.match(/Currency:\s*(\w+)/i);
        if (currencyMatch) {
          return {
            field: 'currency',
            currentValue: null,
            proposedValue: currencyMatch[1],
            reason: `Currency extracted from rawText using vendor pattern`,
            confidence: memory.confidence,
            source: 'correction_memory'
          };
        }
      }
    } else if (memory.correctionType === 'sku_mapping') {
      // Map description to SKU
      const item = normalizedInvoice.lineItems[0];
      if (!item.sku && item.description) {
        const mappedSku = logic.mappings[item.description.toLowerCase()] || logic.defaultSku;
        if (mappedSku) {
          return {
            field: 'lineItems[0].sku',
            currentValue: null,
            proposedValue: mappedSku,
            reason: `Vendor description "${item.description}" maps to SKU ${mappedSku}`,
            confidence: memory.confidence,
            source: 'correction_memory'
          };
        }
      }
    }

    return null;
  }

  private extractValueFromPattern(rawText: string, pattern: string, mapping: any): any {
    // NOTE: This method is currently hardcoded for demonstration purposes.
    // In production, this should use a pattern registry or configuration-driven approach
    // to allow adding new patterns without code changes.
    
    // Extract date from Leistungsdatum pattern
    if (pattern === 'Leistungsdatum') {
      const match = rawText.match(/Leistungsdatum:\s*(\d{2}\.\d{2}\.\d{4})/);
      if (match) {
        // Convert DD.MM.YYYY to YYYY-MM-DD
        const [day, month, year] = match[1].split('.');
        return `${year}-${month}-${day}`;
      }
    }

    return null;
  }

  private matchPurchaseOrder(
    invoice: Invoice,
    purchaseOrders: PurchaseOrder[]
  ): ProposedCorrection | null {
    // Find POs from same vendor
    const vendorPOs = purchaseOrders.filter(po => po.vendor === invoice.vendor);

    // Check for item match
    for (const po of vendorPOs) {
      for (const poItem of po.lineItems) {
        const invoiceItem = invoice.fields.lineItems.find(item => item.sku === poItem.sku);
        if (invoiceItem) {
          // Check if PO date is within 30 days of invoice
          const poDays = this.daysBetween(po.date, invoice.fields.invoiceDate);
          if (poDays <= 30) {
            return {
              field: 'poNumber',
              currentValue: null,
              proposedValue: po.poNumber,
              reason: `Matching PO found: same vendor, matching item ${poItem.sku}, within 30 days`,
              confidence: 0.85,
              source: 'po_matching'
            };
          }
        }
      }
    }

    return null;
  }

  private daysBetween(date1: string, date2: string): number {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    const diffTime = Math.abs(d2.getTime() - d1.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  private makeDecision(
    invoice: Invoice,
    normalizedInvoice: InvoiceFields,
    corrections: ProposedCorrection[],
    duplicates: any[],
    resolutionMemories: ResolutionMemory[]
  ): { requiresHumanReview: boolean; reasoning: string; confidenceScore: number } {
    const reasons: string[] = [];
    let requiresHumanReview = false;
    let confidenceScore = invoice.confidence;

    // Check for duplicates
    if (duplicates.length > 0) {
      requiresHumanReview = true;
      reasons.push(`DUPLICATE DETECTED: Invoice ${invoice.fields.invoiceNumber} from ${invoice.vendor} already processed as ${duplicates.map(d => d.invoiceId).join(', ')}`);
      confidenceScore = Math.min(confidenceScore, 0.3);
    }

    // Check if there are low-confidence corrections
    const lowConfidenceCorrections = corrections.filter(c => c.confidence < this.confidenceThreshold);
    if (lowConfidenceCorrections.length > 0) {
      requiresHumanReview = true;
      reasons.push(`${lowConfidenceCorrections.length} corrections have confidence below threshold (${this.confidenceThreshold})`);
    }

    // Check for missing critical fields
    if (!normalizedInvoice.currency) {
      requiresHumanReview = true;
      reasons.push('Missing currency field');
    }

    // Calculate average correction confidence
    if (corrections.length > 0) {
      // NOTE: This uses simple averaging for demonstration. In production, consider:
      // - Weighted average based on number of corrections
      // - Separate tracking of extraction vs correction confidence
      // - More sophisticated confidence aggregation algorithms
      const avgCorrectionConfidence = corrections.reduce((sum, c) => sum + c.confidence, 0) / corrections.length;
      confidenceScore = (confidenceScore + avgCorrectionConfidence) / 2;
      
      if (avgCorrectionConfidence >= this.confidenceThreshold) {
        reasons.push(`Applied ${corrections.length} high-confidence corrections from memory`);
      }
    }

    // Check initial confidence
    if (invoice.confidence < 0.7) {
      requiresHumanReview = true;
      reasons.push(`Initial extraction confidence low (${invoice.confidence.toFixed(2)})`);
    }

    // If no issues and high confidence, can auto-accept
    if (!requiresHumanReview && corrections.length === 0) {
      reasons.push('No corrections needed, high confidence extraction');
    } else if (!requiresHumanReview && corrections.every(c => c.confidence >= 0.85)) {
      reasons.push('All corrections applied with high confidence from learned patterns');
    } else if (!requiresHumanReview) {
      // Has corrections but confidence is decent
      reasons.push('Corrections applied based on learned patterns, but manual review recommended');
      requiresHumanReview = true;
    }

    return {
      requiresHumanReview,
      reasoning: reasons.join('. '),
      confidenceScore: Math.max(0, Math.min(1, confidenceScore))
    };
  }

  private applyCorrection(invoice: InvoiceFields, correction: ProposedCorrection): void {
    if (correction.field.includes('[')) {
      // Handle array field like lineItems[0].sku
      const match = correction.field.match(/(\w+)\[(\d+)\]\.(\w+)/);
      if (match) {
        const [, arrayName, index, fieldName] = match;
        (invoice as any)[arrayName][parseInt(index)][fieldName] = correction.proposedValue;
      }
    } else {
      (invoice as any)[correction.field] = correction.proposedValue;
    }
  }

  learnFromCorrection(invoice: Invoice, correction: HumanCorrection): void {
    const now = new Date().toISOString();

    // Store resolution memory
    this.db.saveResolutionMemory({
      vendor: invoice.vendor,
      invoiceNumber: invoice.fields.invoiceNumber,
      decision: correction.finalDecision,
      corrections: JSON.stringify(correction.corrections),
      timestamp: now
    });

    // Store duplicate memory
    this.db.saveDuplicateMemory({
      vendor: invoice.vendor,
      invoiceNumber: invoice.fields.invoiceNumber,
      invoiceDate: invoice.fields.invoiceDate,
      invoiceId: invoice.invoiceId,
      timestamp: now
    });

    // Learn patterns from corrections
    for (const corr of correction.corrections) {
      if (corr.field === 'serviceDate' && corr.reason.includes('Leistungsdatum')) {
        // Learn vendor-specific field mapping
        const existingMemories = this.db.getVendorMemories(invoice.vendor);
        const hasPattern = existingMemories.some(m => m.pattern === 'Leistungsdatum');

        if (!hasPattern) {
          this.db.saveVendorMemory({
            vendor: invoice.vendor,
            pattern: 'Leistungsdatum',
            fieldMapping: JSON.stringify({ targetField: 'serviceDate', extraction: 'date' }),
            confidence: 0.9,
            usageCount: 1,
            successCount: 1,
            lastUsed: now,
            created: now
          });
        }
      } else if (corr.reason.includes('VAT') || corr.reason.includes('MwSt. inkl.')) {
        // Learn VAT-inclusive pricing pattern
        const existingMemories = this.db.getCorrectionMemories(invoice.vendor);
        const hasPattern = existingMemories.some(m => m.correctionType === 'vat_included');

        if (!hasPattern) {
          this.db.saveCorrectionMemory({
            vendor: invoice.vendor,
            pattern: 'MwSt. inkl.',
            correctionType: 'vat_included',
            correctionLogic: JSON.stringify({ recalculate: true }),
            confidence: 0.85,
            usageCount: 1,
            successCount: 1,
            lastUsed: now,
            created: now
          });
        }
      } else if (corr.field === 'currency' && corr.reason.includes('rawText')) {
        // Learn currency extraction pattern
        const existingMemories = this.db.getCorrectionMemories(invoice.vendor);
        const hasPattern = existingMemories.some(m => m.correctionType === 'currency_extraction');

        if (!hasPattern) {
          this.db.saveCorrectionMemory({
            vendor: invoice.vendor,
            pattern: 'Currency:',
            correctionType: 'currency_extraction',
            correctionLogic: JSON.stringify({ extractFrom: 'rawText' }),
            confidence: 0.8,
            usageCount: 1,
            successCount: 1,
            lastUsed: now,
            created: now
          });
        }
      } else if (corr.field.includes('sku') && corr.reason.includes('map')) {
        // Learn SKU mapping
        const existingMemories = this.db.getCorrectionMemories(invoice.vendor);
        let skuMemory = existingMemories.find(m => m.correctionType === 'sku_mapping');

        if (!skuMemory) {
          // Find the description from invoice
          const item = invoice.fields.lineItems[0];
          const mappings: any = {};
          if (item && item.description) {
            mappings[item.description.toLowerCase()] = corr.to;
            // Also add variations
            if (item.description.toLowerCase().includes('seefracht')) {
              mappings['seefracht'] = corr.to;
              mappings['shipping'] = corr.to;
              mappings['transport'] = corr.to;
            }
          }

          this.db.saveCorrectionMemory({
            vendor: invoice.vendor,
            pattern: 'freight|shipping|seefracht',
            correctionType: 'sku_mapping',
            correctionLogic: JSON.stringify({ mappings, defaultSku: corr.to }),
            confidence: 0.75,
            usageCount: 1,
            successCount: 1,
            lastUsed: now,
            created: now
          });
        }
      } else if (corr.field === 'discountTerms' && corr.reason.includes('Skonto')) {
        // Learn discount terms pattern - store as vendor memory
        const existingMemories = this.db.getVendorMemories(invoice.vendor);
        const hasPattern = existingMemories.some(m => m.pattern.includes('Skonto'));

        if (!hasPattern) {
          this.db.saveVendorMemory({
            vendor: invoice.vendor,
            pattern: 'Skonto',
            fieldMapping: JSON.stringify({ targetField: 'discountTerms', extraction: 'text' }),
            confidence: 0.9,
            usageCount: 1,
            successCount: 1,
            lastUsed: now,
            created: now
          });
        }
      }
    }
  }
}
