# Video Demo Script

## Introduction (30 seconds)

"Hello! I'm demonstrating my Invoice Memory Learning System - an AI-powered solution that learns from human corrections to automate invoice processing.

This system implements a memory-driven learning layer that:
- Learns from past corrections
- Applies vendor-specific patterns
- Improves automation over time
- Provides explainable decisions"

## System Overview (1 minute)

"The system is built with TypeScript in strict mode, uses SQLite for persistence, and implements 4 types of memory:

1. Vendor Memory - field mappings like 'Leistungsdatum' to serviceDate
2. Correction Memory - automated fixes like VAT recalculation
3. Resolution Memory - tracks human decisions
4. Duplicate Memory - prevents reprocessing

The processing follows a RADL cycle: Recall, Apply, Decide, Learn."

## Code Walkthrough (2 minutes)

[Show file structure]
"Here's the project structure:
- src/types.ts defines all interfaces
- src/database.ts handles SQLite persistence
- src/memoryEngine.ts contains the core learning logic
- src/demo.ts is the demonstration runner"

[Show key code sections]
"The memory engine processes each invoice through:
1. Recalling relevant memories
2. Applying high-confidence patterns
3. Deciding whether to escalate
4. Learning from human corrections"

[Show confidence scoring]
"Confidence is dynamic: confidence = successCount / usageCount
This ensures patterns that work get reinforced, while bad patterns decay naturally."

## Running the Demo (3 minutes)

[Terminal screen]
"Let's run the demo:
```
cd appendix
npm install
npm run demo
```

Watch as we process 12 invoices:

**INV-A-001 (Supplier GmbH)**:
- Human teaches: 'Leistungsdatum' means serviceDate
- System stores vendor memory with 90% confidence

**INV-A-002 (Supplier GmbH)**:
- System automatically extracts serviceDate
- Applied learned pattern - no human review needed!

**INV-A-003 (Supplier GmbH)**:
- Human teaches PO matching logic
- System learns to match by SKU and date

**INV-B-001 (Parts AG)**:
- Human corrects VAT-inclusive pricing
- System learns 'MwSt. inkl.' pattern

**INV-B-002 (Parts AG)**:
- System detects VAT-inclusive pattern
- Auto-suggests recalculation with reasoning

**INV-B-003 (Parts AG)**:
- Human extracts currency from rawText
- System learns extraction pattern

**INV-C-001 (Freight & Co)**:
- Human adds Skonto discount terms
- System stores as vendor memory

**INV-C-002 (Freight & Co)**:
- Human maps 'Seefracht' to SKU FREIGHT
- System learns description-to-SKU mapping

**INV-C-003 (Freight & Co)**:
- System applies learned patterns automatically
- Fewer flags, smarter decisions!

**INV-A-004 & INV-B-004**:
- System detects duplicates
- Same vendor + invoice number + close dates
- Confidence drops to 30%, flagged for review"

## Learning Summary (1 minute)

[Show memory summary section]
"At the end, we see what the system learned:

Vendor Memories:
- Supplier GmbH: Leistungsdatum pattern (90% confidence)
- Freight & Co: Skonto terms (90% confidence)

Correction Memories:
- Parts AG: VAT-inclusive detection (85% confidence)
- Parts AG: Currency extraction (80% confidence)
- Freight & Co: SKU mapping (75% confidence)

Resolution History shows 6 invoices resolved successfully."

## Expected Outcomes Verification (1 minute)

[Show verification section]
"All 7 required outcomes are working:

1. ✅ Leistungsdatum learning (Supplier GmbH)
2. ✅ PO matching (Supplier GmbH)
3. ✅ VAT-inclusive detection (Parts AG)
4. ✅ Currency extraction (Parts AG)
5. ✅ Skonto terms (Freight & Co)
6. ✅ SKU mapping (Freight & Co)
7. ✅ Duplicate detection (INV-A-004, INV-B-004)"

## Output Format (30 seconds)

[Show JSON output]
"Each invoice returns a standardized JSON with:
- Normalized invoice data
- Proposed corrections with confidence scores
- Decision (requires review or not)
- Reasoning explaining why
- Complete audit trail
- Memory updates"

## Persistence Demo (30 seconds)

[Show database]
"Memory is stored in SQLite:
```
sqlite3 memory.db
SELECT * FROM vendor_memory;
```

Memory persists across runs. If I run the demo again, it starts with learned patterns already in place."

## Conclusion (30 seconds)

"This system demonstrates:
- Real learning that improves over time
- Explainable AI with reasoning
- Safe automation with proper escalation
- Production-ready TypeScript code

The code is on GitHub at: github.com/yss107/project/tree/main/appendix

Thank you for watching!"

---

## Video Recording Tips

1. **Screen Setup**:
   - Terminal window (full screen or large)
   - Code editor for quick views
   - Browser for README

2. **Recording Flow**:
   - Start with intro
   - Show file structure
   - Open 1-2 key files
   - Run the demo (full output)
   - Show memory database
   - End with outcomes verification

3. **Duration**: Aim for 8-10 minutes total

4. **Tools**: 
   - OBS Studio (free, cross-platform)
   - QuickTime (Mac)
   - Windows Game Bar (Windows)

5. **Audio**: Use clear microphone, minimize background noise

6. **Upload**: YouTube (unlisted) or Loom
