/**
 * Decision module - determines whether to auto-accept, auto-correct, or escalate
 */

import { ProposedCorrection, AuditTrailEntry } from '../types/output';
import { Memory } from '../types/memory';
import { ExtractedInvoice } from '../types/invoice';

export interface DecisionContext {
  invoice: ExtractedInvoice;
  corrections: ProposedCorrection[];
  memories: Memory[];
  normalizedInvoice: any;
}

export interface DecisionResult {
  requiresHumanReview: boolean;
  reasoning: string;
  confidenceScore: number;
  auditTrail: AuditTrailEntry[];
}

export class DecisionEngine {
  private readonly AUTO_ACCEPT_THRESHOLD = 0.85;
  private readonly AUTO_CORRECT_THRESHOLD = 0.70;
  private readonly LOW_CONFIDENCE_THRESHOLD = 0.50;

  /**
   * Make decision on whether to auto-accept, auto-correct, or escalate
   */
  decide(context: DecisionContext): DecisionResult {
    const auditTrail: AuditTrailEntry[] = [];
    const timestamp = new Date().toISOString();

    // Calculate overall confidence score
    const confidenceScore = this.calculateConfidenceScore(context);

    auditTrail.push({
      step: 'decide',
      timestamp,
      details: `Calculated overall confidence score: ${confidenceScore.toFixed(2)}`,
    });

    // Check for critical issues
    const criticalIssues = this.identifyCriticalIssues(context);

    if (criticalIssues.length > 0) {
      auditTrail.push({
        step: 'decide',
        timestamp: new Date().toISOString(),
        details: `Found ${criticalIssues.length} critical issues: ${criticalIssues.join(', ')}`,
      });

      return {
        requiresHumanReview: true,
        reasoning: `Critical issues detected: ${criticalIssues.join('; ')}. Human review required.`,
        confidenceScore,
        auditTrail,
      };
    }

    // Check for low-confidence corrections
    const lowConfidenceCorrections = context.corrections.filter(
      c => c.confidence < this.LOW_CONFIDENCE_THRESHOLD
    );

    if (lowConfidenceCorrections.length > 0) {
      auditTrail.push({
        step: 'decide',
        timestamp: new Date().toISOString(),
        details: `Found ${lowConfidenceCorrections.length} low-confidence corrections`,
      });

      return {
        requiresHumanReview: true,
        reasoning: `${lowConfidenceCorrections.length} corrections have low confidence. Human review recommended to prevent errors.`,
        confidenceScore,
        auditTrail,
      };
    }

    // Decide based on confidence score and correction count
    if (confidenceScore >= this.AUTO_ACCEPT_THRESHOLD && context.corrections.length === 0) {
      auditTrail.push({
        step: 'decide',
        timestamp: new Date().toISOString(),
        details: 'Decision: AUTO-ACCEPT - High confidence, no corrections needed',
      });

      return {
        requiresHumanReview: false,
        reasoning: `High confidence (${confidenceScore.toFixed(2)}) with no corrections needed. Auto-accepted.`,
        confidenceScore,
        auditTrail,
      };
    }

    if (confidenceScore >= this.AUTO_CORRECT_THRESHOLD && 
        context.corrections.every(c => c.confidence >= this.AUTO_CORRECT_THRESHOLD)) {
      auditTrail.push({
        step: 'decide',
        timestamp: new Date().toISOString(),
        details: `Decision: AUTO-CORRECT - Confidence ${confidenceScore.toFixed(2)}, ${context.corrections.length} high-confidence corrections`,
      });

      return {
        requiresHumanReview: false,
        reasoning: `Good confidence (${confidenceScore.toFixed(2)}) with ${context.corrections.length} reliable corrections. Auto-corrected.`,
        confidenceScore,
        auditTrail,
      };
    }

    // Default to human review
    auditTrail.push({
      step: 'decide',
      timestamp: new Date().toISOString(),
      details: `Decision: ESCALATE - Confidence ${confidenceScore.toFixed(2)}, ${context.corrections.length} corrections`,
    });

    return {
      requiresHumanReview: true,
      reasoning: `Confidence score ${confidenceScore.toFixed(2)} with ${context.corrections.length} correction(s). Human review recommended for validation.`,
      confidenceScore,
      auditTrail,
    };
  }

  /**
   * Calculate overall confidence score
   */
  private calculateConfidenceScore(context: DecisionContext): number {
    let score = context.invoice.confidence;

    // Boost confidence if we have high-confidence memories
    const highConfidenceMemories = context.memories.filter(m => m.confidence >= 0.8);
    if (highConfidenceMemories.length > 0) {
      score += 0.1 * Math.min(highConfidenceMemories.length, 3) / 3;
    }

    // Reduce confidence if we have many corrections
    if (context.corrections.length > 0) {
      const avgCorrectionConfidence = 
        context.corrections.reduce((sum, c) => sum + c.confidence, 0) / context.corrections.length;
      
      // Weight the correction confidence
      score = (score * 0.6) + (avgCorrectionConfidence * 0.4);
    }

    // Ensure score is between 0 and 1
    return Math.max(0, Math.min(1, score));
  }

  /**
   * Identify critical issues that require human review
   */
  private identifyCriticalIssues(context: DecisionContext): string[] {
    const issues: string[] = [];

    // Check for potential duplicate
    if (this.isDuplicateSuspected(context.invoice)) {
      issues.push('Potential duplicate invoice detected');
    }

    // Check for missing critical fields
    if (!context.normalizedInvoice.fields.currency) {
      issues.push('Currency missing');
    }

    // Check for large discrepancies
    const largeDiscrepancies = context.corrections.filter(c => {
      if (typeof c.currentValue === 'number' && typeof c.proposedValue === 'number') {
        const percentDiff = Math.abs(c.currentValue - c.proposedValue) / c.currentValue;
        return percentDiff > 0.2; // More than 20% difference
      }
      return false;
    });

    if (largeDiscrepancies.length > 0) {
      issues.push(`Large discrepancies in ${largeDiscrepancies.length} field(s)`);
    }

    // Check for very low original confidence
    if (context.invoice.confidence < 0.5) {
      issues.push('Low extraction confidence');
    }

    return issues;
  }

  /**
   * Check if invoice might be a duplicate
   */
  private isDuplicateSuspected(invoice: ExtractedInvoice): boolean {
    // This is a simplified check - in real system would query database
    // For now, check if confidence is very low (might indicate duplicate)
    return invoice.confidence < 0.65 && 
           invoice.rawText.toLowerCase().includes('duplicate');
  }
}
