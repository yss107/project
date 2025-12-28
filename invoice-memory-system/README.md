# Invoice Memory Learning System

A memory-driven learning layer for invoice automation that learns from past corrections and applies insights to future invoices.

## 🎯 Overview

This system addresses a common problem in invoice processing: **corrections are wasted**. Every day, companies manually correct the same vendor-specific patterns, tax calculation issues, and data mismatches without the system learning from these corrections.

This solution implements a **Memory Layer** that:
- 🧠 **Stores** reusable insights from past invoices
- 🔄 **Applies** them to future invoices to improve automation
- 📊 **Decides** whether to auto-accept, auto-correct, or escalate
- 📚 **Learns** from human feedback with confidence tracking
- 🔍 **Remains** explainable and auditable

## 🏗️ Architecture & Design

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Invoice Processor                        │
│                   (Main Orchestrator)                       │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─► 1. RECALL   ─► Retrieve relevant memories
             │
             ├─► 2. APPLY    ─► Generate corrections
             │
             ├─► 3. DECIDE   ─► Auto-process or escalate
             │
             └─► 4. LEARN    ─► Update memories from feedback
```

### Memory Types

1. **Vendor Memory**: Vendor-specific patterns
   - Example: "Leistungsdatum" → service date for Supplier GmbH
   - Example: "MwSt. inkl." → VAT included for Parts AG

2. **Correction Memory**: Recurring correction patterns
   - Example: Quantity mismatches → adjust to delivery note
   - Example: Missing PO → match by line items

3. **Resolution Memory**: Human decision tracking
   - Tracks approved vs. rejected corrections
   - Helps avoid repeating failed patterns

### Confidence System

- **Initial confidence**: 0.6 for approved corrections, 0.4 for rejected
- **Reinforcement**: +5% per success (with diminishing returns)
- **Weakening**: -10% per failure
- **Decay**: -2% per month if unused
- **Range**: 0.1 (min) to 0.95 (max)

### Decision Thresholds

- **Auto-Accept**: ≥85% confidence, no corrections needed
- **Auto-Correct**: ≥70% confidence, all corrections high-confidence
- **Escalate**: Below thresholds, low confidence, or critical issues

## 🚀 Quick Start

### Prerequisites

- Node.js (v16+)
- npm or yarn

### Installation

```bash
cd invoice-memory-system
npm install
```

### Run Demo

```bash
npm run demo
```

The demo will:
1. Process initial invoices (INV-A-001, INV-A-003, INV-B-001, etc.)
2. Learn from human corrections
3. Process new invoices showing improved automation
4. Demonstrate duplicate detection

### Build

```bash
npm run build
```

### Clean

```bash
npm run clean
```

## 📊 Demo Output

The demo demonstrates all required learning outcomes:

### Phase 1: Initial Learning
- Processes first batch of invoices
- Applies human corrections
- Builds memory database

### Phase 2: Applying Knowledge
- Shows improved processing for similar invoices
- Demonstrates automatic field extraction
- Shows confidence improvements

### Phase 3: Duplicate Detection
- Flags INV-A-004 and INV-B-004 as duplicates
- Prevents contradictory memory creation

## 🎓 Expected Outcomes (All Achieved)

✅ **Supplier GmbH**: After learning from INV-A-001, service date auto-extracted from "Leistungsdatum"

✅ **Supplier GmbH**: INV-A-003 auto-matched to PO-A-051 (single matching PO + item match)

✅ **Parts AG**: VAT inclusion detection ("MwSt. inkl.") triggers recalculation with reasoning

✅ **Parts AG**: Missing currency recovered from rawText with vendor-specific confidence

✅ **Freight & Co**: Skonto terms detected and recorded; later invoices flagged less often

✅ **Freight & Co**: "Seefracht/Shipping" maps to SKU FREIGHT with increasing confidence

✅ **Duplicates**: INV-A-004 and INV-B-004 flagged as duplicates; no contradictory memory

## 📝 API Usage

### Process Invoice

```typescript
import { InvoiceProcessor } from './invoice-processor';

const processor = new InvoiceProcessor('./memory.db');

const result = processor.processInvoice(
  invoice,
  purchaseOrders,
  deliveryNotes
);

console.log(result.requiresHumanReview);
console.log(result.proposedCorrections);
console.log(result.confidenceScore);
```

### Learn from Correction

```typescript
processor.learnFromHumanCorrection({
  invoiceId: "INV-A-001",
  vendor: "Supplier GmbH",
  corrections: [
    {
      field: "serviceDate",
      from: null,
      to: "2024-01-01",
      reason: "Leistungsdatum found in rawText"
    }
  ],
  finalDecision: "approved"
});
```

### Check Duplicates

```typescript
const duplicate = processor.checkForDuplicates(
  newInvoice,
  existingInvoices
);

if (duplicate) {
  console.log("Duplicate detected:", duplicate.invoiceId);
}
```

## 🔍 Output Contract

Every invoice processing returns:

```typescript
{
  "normalizedInvoice": { /* corrected invoice data */ },
  "proposedCorrections": [
    {
      "field": "serviceDate",
      "currentValue": null,
      "proposedValue": "2024-01-01",
      "reason": "Vendor Supplier GmbH uses 'Leistungsdatum' for service date",
      "confidence": 0.75,
      "memoryId": 1
    }
  ],
  "requiresHumanReview": false,
  "reasoning": "Good confidence (0.82) with 1 reliable correction. Auto-corrected.",
  "confidenceScore": 0.82,
  "memoryUpdates": [
    {
      "action": "applied",
      "memoryId": 1,
      "pattern": "Leistungsdatum",
      "details": "Applied memory for Supplier GmbH"
    }
  ],
  "auditTrail": [
    {
      "step": "recall",
      "timestamp": "2024-01-15T10:30:00Z",
      "details": "Retrieved 3 memories for vendor: Supplier GmbH"
    },
    /* ... more audit entries ... */
  ]
}
```

## 🗄️ Data Persistence

The system uses **SQLite** for persistent memory storage:

- **Table**: `memories`
- **Indexes**: vendor, type, pattern, confidence
- **Unique constraint**: (type, vendor, pattern, action)
- **Location**: Configurable (default: `./memory.db`)

### Schema

```sql
CREATE TABLE memories (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL,
  vendor TEXT NOT NULL,
  pattern TEXT NOT NULL,
  action TEXT NOT NULL,
  confidence REAL NOT NULL,
  occurrences INTEGER DEFAULT 1,
  successCount INTEGER DEFAULT 0,
  failureCount INTEGER DEFAULT 0,
  createdAt TEXT NOT NULL,
  lastUsedAt TEXT NOT NULL,
  lastUpdatedAt TEXT NOT NULL,
  resolutionType TEXT
);
```

## 🔒 Security & Quality

### Prevention of Bad Learnings

1. **Confidence thresholds**: Low-confidence memories don't auto-apply
2. **Human review**: Critical issues always escalated
3. **Reinforcement learning**: Success/failure tracking adjusts confidence
4. **Decay mechanism**: Unused memories gradually weaken
5. **Audit trail**: Every decision is logged and explainable

### Duplicate Prevention

- Same vendor + invoice number + close dates (≤7 days)
- Prevents contradictory memory from duplicate submissions

## 📂 Project Structure

```
invoice-memory-system/
├── src/
│   ├── types/
│   │   ├── invoice.ts       # Invoice data types
│   │   ├── memory.ts        # Memory types
│   │   └── output.ts        # Output/result types
│   ├── persistence/
│   │   └── memory-store.ts  # SQLite persistence layer
│   ├── memory/
│   │   ├── recall.ts        # Memory retrieval
│   │   ├── apply.ts         # Apply memories to invoices
│   │   └── learning.ts      # Learn from corrections
│   ├── decision/
│   │   └── decision-engine.ts  # Decision logic
│   ├── data/
│   │   ├── invoices_extracted.json
│   │   ├── purchase_orders.json
│   │   ├── delivery_notes.json
│   │   └── human_corrections.json
│   ├── invoice-processor.ts # Main orchestrator
│   └── demo.ts              # Demo runner
├── package.json
├── tsconfig.json
└── README.md
```

## 🧪 Testing Approach

The system uses **heuristics-based logic** rather than ML training:

- Pattern matching for vendor-specific terms
- Statistical confidence tracking
- Rule-based decision thresholds
- Explainable reasoning for all decisions

No ML training required - the system learns through usage and human feedback.

## 📈 Future Enhancements

- 🌐 Web UI for memory visualization
- 📊 Analytics dashboard for automation rates
- 🔄 Export/import memory databases
- 🤖 ML-based pattern recognition
- 🌍 Multi-language support
- 🔔 Alert system for anomalies

## 👨‍💻 Author

**Yash Kumar**
- Machine Learning Engineer & Data Analyst
- LinkedIn: [linkedin.com/in/yash-kumar09](https://www.linkedin.com/in/yash-kumar09/)
- Portfolio: [yss107.github.io](https://yss107.github.io)

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built as part of an AI Agent System assignment focusing on document automation and learning systems.

---

**Made with ❤️ for intelligent invoice automation**
