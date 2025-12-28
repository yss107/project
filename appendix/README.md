# Invoice Memory Learning System

An intelligent memory-driven learning layer for automated invoice processing that learns from human corrections and improves automation rates over time.

## 🎯 Overview

This system implements a memory layer that sits on top of invoice extraction, enabling:
- **Learning from corrections**: Stores reusable insights from past invoices
- **Pattern recognition**: Applies vendor-specific patterns to future invoices
- **Explainable decisions**: Every correction and escalation comes with reasoning
- **Audit trail**: Complete tracking of all decisions and memory updates

## 🏗️ Architecture

The system consists of several key components:

### 1. **Memory Types**

#### Vendor Memory
Stores vendor-specific field mappings and patterns:
- Field name translations (e.g., "Leistungsdatum" → serviceDate)
- Vendor-specific extraction patterns
- Confidence scoring based on usage success

#### Correction Memory
Learns from repeated corrections:
- VAT-inclusive pricing detection
- Currency extraction patterns
- SKU mapping rules
- Confidence reinforcement over time

#### Resolution Memory
Tracks how discrepancies were resolved:
- Human approval/rejection decisions
- Correction history per invoice
- Pattern success tracking

#### Duplicate Memory
Prevents duplicate processing:
- Tracks all processed invoices
- Detects same vendor + invoice number + close dates
- Flags for human review

### 2. **Processing Pipeline**

The system follows a 4-step cycle (RADL):

#### **Recall** 
- Retrieves relevant vendor memories
- Loads correction patterns
- Checks for duplicates
- Reviews resolution history

#### **Apply**
- Applies high-confidence vendor patterns
- Suggests corrections based on learned rules
- Normalizes fields using memory
- Matches purchase orders when applicable

#### **Decide**
- Evaluates confidence scores
- Determines auto-accept vs escalation
- Generates reasoning for decisions
- Flags low-confidence corrections

#### **Learn**
- Stores new patterns from human corrections
- Reinforces successful memories
- Updates confidence scores
- Maintains complete audit trail

### 3. **Confidence Scoring**

The system uses dynamic confidence scoring:
- Initial confidence from extraction
- Boosted by successful pattern matches
- Reduced by duplicates or missing fields
- Updated with each usage: `confidence = successCount / usageCount`

### 4. **Decision Logic**

Auto-accept criteria:
- Confidence > 0.7
- No duplicates detected
- All critical fields present
- High-confidence corrections only

Escalation triggers:
- Duplicate invoices
- Low extraction confidence (< 0.7)
- Missing critical fields (currency, etc.)
- Low-confidence corrections

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ 
- npm

### Installation

```bash
cd appendix
npm install
```

### Build

```bash
npm run build
```

### Run Demo

```bash
npm run demo
```

This will:
1. Initialize a fresh memory database
2. Process invoices in demonstration order
3. Apply human corrections
4. Show learning progression
5. Display memory summary
6. Verify expected outcomes

## 📊 Demo Output

The demo demonstrates all required learning scenarios:

### 1. **Supplier GmbH: Leistungsdatum Learning**
- **INV-A-001**: Human corrects serviceDate from "Leistungsdatum"
- **INV-A-002**: System automatically fills serviceDate
- **Learning**: Vendor pattern "Leistungsdatum" → serviceDate (90% confidence)

### 2. **Supplier GmbH: PO Matching**
- **INV-A-003**: Human matches PO-A-051 based on item WIDGET-002
- **Future invoices**: System suggests PO matches automatically
- **Logic**: Same vendor + matching SKU + within 30 days

### 3. **Parts AG: VAT-Inclusive Pricing**
- **INV-B-001**: Human recalculates due to "MwSt. inkl." (VAT included)
- **INV-B-002**: System detects pattern and suggests recalculation
- **Learning**: Pattern "MwSt. inkl." triggers tax correction (85% confidence)

### 4. **Parts AG: Currency Recovery**
- **INV-B-003**: Human extracts currency from rawText
- **Future invoices**: System searches rawText for currency
- **Learning**: Vendor-specific currency extraction pattern (80% confidence)

### 5. **Freight & Co: Skonto Terms**
- **INV-C-001**: Human adds discount terms from rawText
- **INV-C-003**: System recognizes and records pattern
- **Learning**: Skonto terms detection (90% confidence)

### 6. **Freight & Co: SKU Mapping**
- **INV-C-002**: Human maps "Seefracht/Shipping" → FREIGHT
- **INV-C-003**: System applies mapping automatically
- **Learning**: Description patterns → SKU mappings (75% confidence)

### 7. **Duplicate Detection**
- **INV-A-004**: Flagged as duplicate of INV-A-003
- **INV-B-004**: Flagged as duplicate of INV-B-003
- **Logic**: Same vendor + invoice number + dates within 7 days

## 📁 Project Structure

```
appendix/
├── src/
│   ├── types.ts          # TypeScript interfaces and types
│   ├── database.ts       # SQLite persistence layer
│   ├── memoryEngine.ts   # Core memory and processing logic
│   └── demo.ts           # Demonstration runner script
├── data/
│   ├── invoices.json     # Sample invoice data
│   ├── purchase_orders.json
│   ├── delivery_notes.json
│   └── human_corrections.json
├── dist/                 # Compiled JavaScript (generated)
├── memory.db            # SQLite database (generated)
├── package.json
├── tsconfig.json
└── README.md
```

## 🔧 Technical Details

### Stack
- **TypeScript** (strict mode enabled)
- **Node.js** runtime
- **better-sqlite3** for persistence

### Persistence
- SQLite database (`memory.db`)
- Memory persists across runs
- Four tables: vendor_memory, correction_memory, resolution_memory, duplicate_memory

### Output Contract

Each processed invoice returns:

```typescript
{
  normalizedInvoice: InvoiceFields,      // Corrected invoice data
  proposedCorrections: [                 // Suggested changes
    {
      field: string,
      currentValue: any,
      proposedValue: any,
      reason: string,
      confidence: number,
      source: string
    }
  ],
  requiresHumanReview: boolean,          // Escalation flag
  reasoning: string,                     // Decision explanation
  confidenceScore: number,               // Overall confidence (0-1)
  memoryUpdates: [],                     // Changes to memory
  auditTrail: [                          // Complete history
    {
      step: "recall|apply|decide|learn",
      timestamp: string,
      details: string
    }
  ]
}
```

## 🧪 Testing

The demo script serves as a comprehensive test:

```bash
# Fresh run (clears memory)
rm memory.db && npm run demo

# Rerun to see persistent memory in action
npm run demo
```

### Expected Outcomes

All 7 required outcomes are verified in the demo output:

✅ **Vendor pattern learning** (Leistungsdatum)  
✅ **PO matching** (item + date matching)  
✅ **VAT correction** (MwSt. inkl. detection)  
✅ **Currency extraction** (from rawText)  
✅ **Skonto terms** (discount detection)  
✅ **SKU mapping** (description → SKU)  
✅ **Duplicate detection** (vendor + number + date)

## 🔍 Design Decisions

### Why SQLite?
- Simple, serverless, file-based
- No external dependencies
- Perfect for persistent memory
- Easy to inspect and debug

### Confidence Algorithm
- Starts with learned confidence (0.75-0.9)
- Updates dynamically: `confidence = successCount / usageCount`
- Decays naturally with failures
- Prevents bad learnings from dominating

### Memory Reinforcement
- Each successful application increments usage counter
- Each successful correction increments success counter
- Confidence auto-adjusts based on ratio
- Low-confidence memories (<0.7) trigger escalation

### Audit Trail
- Every step logged with timestamp
- Enables debugging and compliance
- Shows reasoning for all decisions
- Tracks memory evolution

## 🎥 Video Demo

A video demonstration showing:
1. Fresh memory database initialization
2. Sequential invoice processing
3. Human corrections being applied
4. Memory learning and growth
5. Improved automation on later invoices
6. All expected outcomes verified

*[Video link to be provided separately]*

## 🤝 Contributing

This system is designed for extensibility:

- **New memory types**: Add to database schema and engine
- **Custom patterns**: Extend correction memory logic
- **Integration**: Replace sample data with real extraction APIs
- **UI**: Build visualization layer on top of engine

## 📝 License

Educational project for AI Agent Intern Assignment.

## 👨‍💻 Author

Yash Kumar  
GitHub: [yss107](https://github.com/yss107)

---

**Note**: This is a demonstration system. In production, you would:
- Add comprehensive error handling
- Implement memory decay mechanisms
- Add conflict resolution for contradictory memories
- Include batch processing capabilities
- Add monitoring and alerting
- Implement memory pruning for old patterns
