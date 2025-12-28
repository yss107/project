# Quick Start Guide

## Installation & Setup

1. **Navigate to the project directory:**
   ```bash
   cd invoice-memory-system
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the demo:**
   ```bash
   npm run demo
   ```

## What the Demo Shows

The demo demonstrates a complete learning cycle:

### Phase 1: Initial Learning (6 invoices)
- Processes invoices from 3 vendors (Supplier GmbH, Parts AG, Freight & Co)
- System flags issues and requires human review
- Human corrections are applied and stored as memories
- Learns vendor-specific patterns and correction strategies

### Phase 2: Applying Knowledge (3 invoices)
- Processes new invoices from same vendors
- Shows automatic field extraction based on learned patterns
- Demonstrates reduced human review requirements
- Displays confidence improvements

### Phase 3: Duplicate Detection (2 invoices)
- Flags INV-A-004 and INV-B-004 as potential duplicates
- Prevents contradictory memory creation
- Shows same vendor + invoice number + close dates detection

## Key Learnings Demonstrated

1. **Supplier GmbH:**
   - ✅ "Leistungsdatum" → service date extraction
   - ✅ PO matching for invoices without PO numbers

2. **Parts AG:**
   - ✅ "MwSt. inkl." → VAT recalculation
   - ✅ Currency extraction from rawText

3. **Freight & Co:**
   - ✅ Skonto/discount terms detection
   - ✅ Description to SKU mapping (Seefracht → FREIGHT)

## Expected Output

```
═══════════════════════════════════════════════════════════════
        INVOICE MEMORY LEARNING SYSTEM - DEMO
═══════════════════════════════════════════════════════════════

📊 PHASE 1: Initial Learning Phase
[Shows 6 invoices being processed and learned from]

📊 PHASE 2: Applying Learned Knowledge
[Shows improved automation on new invoices]

📊 PHASE 3: Duplicate Detection
[Shows duplicate detection working]

═══════════════════════════════════════════════════════════════
        DEMO COMPLETE - KEY LEARNINGS
═══════════════════════════════════════════════════════════════

✨ System Performance:
  📚 Total Memories Stored: 7
  🎯 High Confidence (≥70%): 0
  📈 Average Confidence: 60.3%
```

## Using as a Library

```typescript
import { InvoiceProcessor } from './invoice-processor';

// Initialize processor
const processor = new InvoiceProcessor('./memory.db');

// Process an invoice
const result = processor.processInvoice(
  invoice,
  purchaseOrders,
  deliveryNotes
);

// Check result
if (result.requiresHumanReview) {
  console.log('Review needed:', result.reasoning);
  console.log('Corrections:', result.proposedCorrections);
} else {
  console.log('Auto-processed successfully');
}

// Learn from human feedback
processor.learnFromHumanCorrection({
  invoiceId: "INV-001",
  vendor: "Acme Corp",
  corrections: [{
    field: "serviceDate",
    from: null,
    to: "2024-01-15",
    reason: "Found in rawText"
  }],
  finalDecision: "approved"
});

// Close when done
processor.close();
```

## Building for Production

```bash
# Build TypeScript to JavaScript
npm run build

# Output will be in ./dist directory
```

## Database Location

The memory database is stored in SQLite format:
- **Demo**: `./demo-memory.db` (recreated on each demo run)
- **Custom**: Pass path to `InvoiceProcessor` constructor

## Troubleshooting

### Demo doesn't run
- Ensure Node.js v16+ is installed
- Run `npm install` to install dependencies
- Check that all data files exist in `src/data/`

### Build fails
- Check TypeScript version: `npx tsc --version`
- Ensure strict mode is supported
- Verify all dependencies are installed

### Database errors
- Ensure write permissions in directory
- Delete existing `.db` file and retry
- Check disk space availability

## Next Steps

1. Review the complete README.md for architecture details
2. Explore the source code in `src/` directory
3. Modify `src/data/` files to test with your own data
4. Integrate into your invoice processing pipeline

## Support

For issues or questions:
- Check the main README.md for detailed documentation
- Review the source code comments
- Test with the provided sample data first
