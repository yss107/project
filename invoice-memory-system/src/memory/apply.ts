/**
 * Memory apply module - applies learned patterns to normalize and correct invoices
 */

import { Memory } from '../types/memory';
import { ExtractedInvoice, PurchaseOrder, DeliveryNote } from '../types/invoice';
import { ProposedCorrection, AuditTrailEntry } from '../types/output';

export interface ApplyContext {
  invoice: ExtractedInvoice;
  memories: Memory[];
  purchaseOrders: PurchaseOrder[];
  deliveryNotes: DeliveryNote[];
}

export class MemoryApply {
  /**
   * Apply memories to generate corrections
   */
  applyMemories(context: ApplyContext): {
    corrections: ProposedCorrection[];
    normalizedInvoice: any;
    auditTrail: AuditTrailEntry[];
  } {
    const corrections: ProposedCorrection[] = [];
    const auditTrail: AuditTrailEntry[] = [];
    const normalizedInvoice = JSON.parse(JSON.stringify(context.invoice));

    for (const memory of context.memories) {
      const memoryCorrections = this.applyMemory(context, memory);
      corrections.push(...memoryCorrections);

      if (memoryCorrections.length > 0) {
        auditTrail.push({
          step: 'apply',
          timestamp: new Date().toISOString(),
          details: `Applied memory #${memory.id}: ${memory.pattern} -> ${memoryCorrections.length} corrections proposed`,
        });
      }
    }

    // Apply high-confidence corrections to normalized invoice
    for (const correction of corrections) {
      if (correction.confidence >= 0.7) {
        this.applyToNormalizedInvoice(normalizedInvoice, correction);
        auditTrail.push({
          step: 'apply',
          timestamp: new Date().toISOString(),
          details: `Auto-applied correction to ${correction.field}: ${correction.currentValue} -> ${correction.proposedValue}`,
        });
      }
    }

    return { corrections, normalizedInvoice, auditTrail };
  }

  /**
   * Apply a single memory to generate corrections
   */
  private applyMemory(context: ApplyContext, memory: Memory): ProposedCorrection[] {
    const corrections: ProposedCorrection[] = [];

    switch (memory.type) {
      case 'vendor':
        corrections.push(...this.applyVendorMemory(context, memory));
        break;
      case 'correction':
        corrections.push(...this.applyCorrectionMemory(context, memory));
        break;
      case 'resolution':
        // Resolution memories don't directly generate corrections
        break;
    }

    return corrections;
  }

  /**
   * Apply vendor-specific patterns
   */
  private applyVendorMemory(context: ApplyContext, memory: Memory): ProposedCorrection[] {
    const corrections: ProposedCorrection[] = [];
    const { invoice } = context;

    // Handle service date extraction patterns
    if (memory.pattern.includes('Leistungsdatum') && !invoice.fields.serviceDate) {
      const serviceDate = this.extractServiceDate(invoice.rawText);
      if (serviceDate) {
        corrections.push({
          field: 'serviceDate',
          currentValue: null,
          proposedValue: serviceDate,
          reason: `Vendor ${invoice.vendor} uses "Leistungsdatum" for service date`,
          confidence: memory.confidence,
          memoryId: memory.id,
        });
      }
    }

    // Handle VAT inclusion patterns
    if ((memory.pattern.includes('MwSt. inkl') || memory.pattern.includes('VAT incl')) &&
        invoice.fields.taxTotal) {
      const recalculated = this.recalculateVAT(invoice.fields);
      if (recalculated) {
        corrections.push({
          field: 'taxTotal',
          currentValue: invoice.fields.taxTotal,
          proposedValue: recalculated.taxTotal,
          reason: `Vendor ${invoice.vendor} includes VAT in totals`,
          confidence: memory.confidence,
          memoryId: memory.id,
        });
        corrections.push({
          field: 'grossTotal',
          currentValue: invoice.fields.grossTotal,
          proposedValue: recalculated.grossTotal,
          reason: `Vendor ${invoice.vendor} includes VAT in totals`,
          confidence: memory.confidence,
          memoryId: memory.id,
        });
      }
    }

    // Handle currency extraction
    if (memory.pattern.includes('currency') && !invoice.fields.currency) {
      const currency = this.extractCurrency(invoice.rawText);
      if (currency) {
        corrections.push({
          field: 'currency',
          currentValue: null,
          proposedValue: currency,
          reason: `Currency found in raw text based on vendor pattern`,
          confidence: memory.confidence,
          memoryId: memory.id,
        });
      }
    }

    // Handle SKU mapping from descriptions
    if (memory.pattern.includes('description_to_sku') && memory.action) {
      const actionParts = memory.action.split('->');
      if (actionParts.length === 2) {
        const [descPattern, targetSku] = actionParts;
        for (let i = 0; i < invoice.fields.lineItems.length; i++) {
          const item = invoice.fields.lineItems[i];
          if (!item.sku && item.description.toLowerCase().includes(descPattern.toLowerCase())) {
            corrections.push({
              field: `lineItems[${i}].sku`,
              currentValue: null,
              proposedValue: targetSku.trim(),
              reason: `Description "${item.description}" maps to SKU ${targetSku} for ${invoice.vendor}`,
              confidence: memory.confidence,
              memoryId: memory.id,
            });
          }
        }
      }
    }

    // Handle discount terms
    if (memory.pattern.includes('skonto') || memory.pattern.includes('discount')) {
      const terms = this.extractDiscountTerms(invoice.rawText);
      if (terms && !invoice.fields.discountTerms) {
        corrections.push({
          field: 'discountTerms',
          currentValue: null,
          proposedValue: terms,
          reason: `Discount terms found in invoice text`,
          confidence: memory.confidence,
          memoryId: memory.id,
        });
      }
    }

    return corrections;
  }

  /**
   * Apply correction-specific memories
   */
  private applyCorrectionMemory(context: ApplyContext, memory: Memory): ProposedCorrection[] {
    const corrections: ProposedCorrection[] = [];
    const { invoice, purchaseOrders, deliveryNotes } = context;

    // Handle missing PO number
    if (memory.pattern === 'missing_po_number' && !invoice.fields.poNumber) {
      const matchingPO = this.findMatchingPO(invoice, purchaseOrders);
      if (matchingPO) {
        corrections.push({
          field: 'poNumber',
          currentValue: null,
          proposedValue: matchingPO.poNumber,
          reason: `Matched to PO ${matchingPO.poNumber} based on vendor and line items`,
          confidence: memory.confidence,
          memoryId: memory.id,
        });
      }
    }

    // Handle quantity mismatches
    if (memory.pattern === 'qty_mismatch' && invoice.fields.poNumber) {
      const dn = deliveryNotes.find(d => d.poNumber === invoice.fields.poNumber);
      if (dn) {
        for (let i = 0; i < invoice.fields.lineItems.length; i++) {
          const invoiceItem = invoice.fields.lineItems[i];
          const dnItem = dn.lineItems.find(d => d.sku === invoiceItem.sku);
          if (dnItem && invoiceItem.qty !== dnItem.qtyDelivered) {
            corrections.push({
              field: `lineItems[${i}].qty`,
              currentValue: invoiceItem.qty,
              proposedValue: dnItem.qtyDelivered,
              reason: `Quantity mismatch: invoice shows ${invoiceItem.qty}, delivery note shows ${dnItem.qtyDelivered}`,
              confidence: memory.confidence,
              memoryId: memory.id,
            });
          }
        }
      }
    }

    return corrections;
  }

  /**
   * Extract service date from raw text
   */
  private extractServiceDate(rawText: string): string | null {
    const patterns = [
      /Leistungsdatum:\s*(\d{2}\.\d{2}\.\d{4})/i,
      /Leistungsdatum:\s*(\d{4}-\d{2}-\d{2})/i,
    ];

    for (const pattern of patterns) {
      const match = rawText.match(pattern);
      if (match) {
        return this.normalizeDate(match[1]);
      }
    }

    return null;
  }

  /**
   * Recalculate VAT when it's included in totals
   */
  private recalculateVAT(fields: any): { taxTotal: number; grossTotal: number } | null {
    // If VAT is included, the grossTotal is already correct
    // We need to back-calculate: net = gross / (1 + taxRate), tax = gross - net
    const gross = fields.grossTotal;
    const rate = fields.taxRate;
    const net = gross / (1 + rate);
    const tax = gross - net;

    return {
      taxTotal: Math.round(tax * 100) / 100,
      grossTotal: gross,
    };
  }

  /**
   * Extract currency from raw text
   */
  private extractCurrency(rawText: string): string | null {
    const patterns = [
      /Currency:\s*([A-Z]{3})/i,
      /Währung:\s*([A-Z]{3})/i,
      /(EUR|USD|GBP|CHF)/,
    ];

    for (const pattern of patterns) {
      const match = rawText.match(pattern);
      if (match) {
        return match[1].toUpperCase();
      }
    }

    return null;
  }

  /**
   * Extract discount terms from raw text
   */
  private extractDiscountTerms(rawText: string): string | null {
    const patterns = [
      /(\d+%\s*Skonto[^.\n]*)/i,
      /(Skonto[^.\n]*)/i,
      /(\d+%\s*discount[^.\n]*)/i,
    ];

    for (const pattern of patterns) {
      const match = rawText.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }

    return null;
  }

  /**
   * Find matching purchase order
   */
  private findMatchingPO(invoice: ExtractedInvoice, pos: PurchaseOrder[]): PurchaseOrder | null {
    const vendorPOs = pos.filter(po => po.vendor === invoice.vendor);
    
    // Look for PO with matching items
    for (const po of vendorPOs) {
      const matches = invoice.fields.lineItems.every(invoiceItem => 
        po.lineItems.some(poItem => poItem.sku === invoiceItem.sku)
      );

      if (matches && vendorPOs.length === 1) {
        return po;
      }
    }

    return null;
  }

  /**
   * Normalize date format to YYYY-MM-DD
   */
  private normalizeDate(date: string): string {
    // Handle DD.MM.YYYY
    if (date.includes('.')) {
      const [day, month, year] = date.split('.');
      return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }

    // Already in YYYY-MM-DD format
    if (date.match(/^\d{4}-\d{2}-\d{2}$/)) {
      return date;
    }

    return date;
  }

  /**
   * Apply correction to normalized invoice
   */
  private applyToNormalizedInvoice(invoice: any, correction: ProposedCorrection): void {
    const fieldParts = correction.field.split('.');
    let current = invoice.fields;

    for (let i = 0; i < fieldParts.length - 1; i++) {
      const part = fieldParts[i];
      const match = part.match(/(\w+)\[(\d+)\]/);
      
      if (match) {
        const [, arrayName, index] = match;
        current = current[arrayName][parseInt(index)];
      } else {
        current = current[part];
      }
    }

    const lastField = fieldParts[fieldParts.length - 1];
    current[lastField] = correction.proposedValue;
  }
}
