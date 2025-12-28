# Video Demonstration Script

## Introduction (30 seconds)

**Show**: Terminal with project directory

"Hello! I'm demonstrating the Invoice Memory Learning System - a memory-driven learning layer for invoice automation that learns from past corrections and applies insights to future invoices."

**Show**: README.md overview

"The system addresses a critical problem: companies waste manual corrections every day without learning from them. This solution stores corrections as memories and applies them automatically."

## Architecture Overview (1 minute)

**Show**: DESIGN.md architecture diagram

"The system uses a 4-step pipeline:

1. **RECALL**: Retrieves relevant memories for an invoice
2. **APPLY**: Generates corrections based on memories  
3. **DECIDE**: Determines whether to auto-process or escalate
4. **LEARN**: Updates memories from human feedback

Memory types include:
- Vendor-specific patterns (e.g., German field names)
- Correction patterns (e.g., quantity mismatches)
- Resolution tracking (approved vs rejected)

The system uses SQLite for persistence and TypeScript with strict mode."

## Tech Stack (30 seconds)

**Show**: package.json and tsconfig.json

"Built with:
- TypeScript in strict mode
- Node.js runtime  
- SQLite (better-sqlite3) for persistence
- Zero dependencies beyond runtime essentials

The entire codebase is about 1,800 lines of clean, documented TypeScript."

## Live Demo - Phase 1: Initial Learning (2 minutes)

**Show**: Run `npm run demo`

"Let me run the demo. Starting with a clean database..."

**Show**: Phase 1 output scrolling

"Phase 1 processes 6 initial invoices from 3 vendors:

- **INV-A-001** (Supplier GmbH): System flags for review, human teaches it about 'Leistungsdatum' field
- **INV-A-003** (Supplier GmbH): Now the system ALREADY suggests service date extraction! Plus learns PO matching
- **INV-B-001** (Parts AG): Learns about VAT inclusion in totals  
- **INV-B-003** (Parts AG): Learns currency extraction from raw text
- **INV-C-001** (Freight & Co): Learns Skonto discount term detection
- **INV-C-002** (Freight & Co): Learns description-to-SKU mapping

After each correction, you can see the system creating new memories or reinforcing existing ones."

**Show**: Memory summary

"Here's what it learned: 7 memories across 3 vendors with confidence scores around 60% to start."

## Live Demo - Phase 2: Applying Knowledge (1.5 minutes)

**Show**: Phase 2 output

"Phase 2 shows the power of learning. Processing new invoices:

- **INV-A-002**: Automatically extracts service date from 'Leistungsdatum' - no human needed!
- **INV-B-002**: Detects VAT inclusion pattern and suggests recalculation
- **INV-C-003**: Applies learned discount detection

Notice the 'Memories Applied' counter - the system is now using its learned knowledge."

## Live Demo - Phase 3: Duplicate Detection (1 minute)

**Show**: Phase 3 output

"Phase 3 demonstrates duplicate detection:

- **INV-A-004**: DUPLICATE of INV-A-003 - same vendor, same invoice number, dates within 7 days
- **INV-B-004**: DUPLICATE of INV-B-003

The system correctly flags these and prevents processing to avoid contradictory memories."

## Expected Outcomes Verification (1 minute)

**Show**: Final summary output

"All expected outcomes achieved:

✓ Supplier GmbH: 'Leistungsdatum' service date extraction
✓ Supplier GmbH: PO matching for INV-A-003
✓ Parts AG: VAT inclusion detection and recalculation  
✓ Parts AG: Currency recovery from rawText
✓ Freight & Co: Skonto terms detection
✓ Freight & Co: Description to SKU mapping (Seefracht → FREIGHT)
✓ Duplicates: INV-A-004 and INV-B-004 correctly flagged

The system is production-ready with 7 memories and will continue improving with each correction."

## Output Structure (1 minute)

**Show**: Sample output JSON in README.md

"Every processing result includes:

- **normalizedInvoice**: Corrected invoice data
- **proposedCorrections**: Each with field, values, reason, and confidence
- **requiresHumanReview**: Boolean decision
- **reasoning**: Explanation of why
- **confidenceScore**: Overall confidence (0-1)
- **memoryUpdates**: What memories were created/used
- **auditTrail**: Complete step-by-step log

Everything is explainable and auditable."

## Code Walkthrough (2 minutes)

**Show**: src/ directory structure

"Quick code tour:

**Types**: Clean TypeScript interfaces for all data structures

**Persistence**: SQLite store with proper indexes and unique constraints

**Memory Module**: 
- Recall: Filters relevant memories by pattern matching
- Apply: Generates corrections from memories  
- Learning: Updates confidence with reinforcement and decay

**Decision Engine**: Multi-factor confidence calculation and decision matrix

**Invoice Processor**: Orchestrates the entire pipeline

All heavily commented and following strict TypeScript."

**Show**: Key code snippets - confidence calculation, pattern matching

## Key Features Deep Dive (1.5 minutes)

**Show**: Confidence evolution explanation in DESIGN.md

"Confidence system highlights:

- Starts at 60% for approved, 40% for rejected
- +5% per success with diminishing returns
- -10% per failure  
- -2% decay per month if unused
- Capped at 95% to prevent overconfidence

Decision thresholds:
- 85%+ and no corrections → Auto-accept
- 70%+ with high-confidence corrections → Auto-correct  
- Below that or critical issues → Escalate to human

This prevents bad learnings while enabling automation."

**Show**: Pattern extraction examples

"Pattern extraction is heuristic-based - no ML training needed. The system intelligently extracts patterns from correction reasons and field names."

## Running the System (1 minute)

**Show**: Terminal commands

"Super simple to run:

```bash
cd invoice-memory-system
npm install
npm run demo
```

For production:
```bash
npm run build
```

Use as a library:
```typescript
const processor = new InvoiceProcessor('./memory.db');
const result = processor.processInvoice(invoice, pos, dns);
processor.learnFromHumanCorrection(correction);
```

Database persists between runs. Memory keeps improving."

## Documentation (30 seconds)

**Show**: README, DESIGN, QUICKSTART files

"Complete documentation provided:

- **README.md**: Full system overview, API usage, architecture
- **DESIGN.md**: Deep dive into design decisions and data flow
- **QUICKSTART.md**: Get started in 5 minutes

All expected outcomes documented and verified."

## Conclusion (30 seconds)

**Show**: Project structure overview

"Summary:

✅ Complete TypeScript implementation with strict mode
✅ SQLite persistence  
✅ Working demo that proves learning over time
✅ All expected outcomes achieved
✅ Comprehensive documentation
✅ Production-ready code

The system learns from corrections, applies knowledge automatically, remains explainable, and improves continuously.

Thank you!"

---

## Key Points to Emphasize

1. **Problem**: Corrections are wasted without learning
2. **Solution**: Memory layer that learns and applies
3. **Safety**: Explainable, auditable, confidence-based
4. **Results**: All 7 expected outcomes achieved
5. **Production**: SQLite persistence, TypeScript, clean architecture

## Demo Tips

- Keep terminal font large and readable
- Pause to highlight key outputs
- Point out confidence scores improving
- Show audit trail entries
- Emphasize duplicate detection working
- Highlight memory creation messages
- Show final summary proving all outcomes

## Time Management

- Total: ~15 minutes
- Introduction: 0:30
- Architecture: 1:00
- Tech Stack: 0:30
- Demo Phase 1: 2:00
- Demo Phase 2: 1:30
- Demo Phase 3: 1:00
- Outcomes: 1:00
- Output Structure: 1:00
- Code Tour: 2:00
- Features: 1:30
- Running: 1:00
- Documentation: 0:30
- Conclusion: 0:30

Adjust timing based on actual recording pace.
