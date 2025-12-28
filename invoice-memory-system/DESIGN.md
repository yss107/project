# System Design & Architecture

## Overview

The Invoice Memory Learning System is designed as a **memory-driven learning layer** that sits on top of invoice extraction systems. It learns from past corrections and applies insights to future invoices to improve automation rates.

## Core Design Principles

1. **Learning without ML**: Uses heuristics and confidence tracking instead of ML training
2. **Explainability**: Every decision includes reasoning and audit trail
3. **Safety First**: Low-confidence patterns don't auto-apply
4. **Continuous Improvement**: Confidence adjusts based on success/failure
5. **Persistence**: All memories survive system restarts (SQLite)

## Architecture Components

### 1. Invoice Processor (Orchestrator)
**File**: `src/invoice-processor.ts`

Main entry point that orchestrates the complete pipeline:

```
Input: Invoice + Context (POs, DNs) 
  ↓
Recall → Apply → Decide → Learn
  ↓
Output: Processing Result
```

**Responsibilities:**
- Coordinates all subsystems
- Manages the processing flow
- Provides high-level API

### 2. Memory Store (Persistence Layer)
**File**: `src/persistence/memory-store.ts`

SQLite-based persistent storage for memories.

**Schema Design:**
- **Unique constraint**: (type, vendor, pattern, action)
- **Indexes**: vendor, type, pattern, confidence
- **Audit fields**: createdAt, lastUsedAt, lastUpdatedAt

**Key Operations:**
- `saveMemory()`: Upsert with conflict resolution
- `getMemories()`: Retrieve by vendor/type
- `findByPattern()`: Search by pattern
- `updateMemory()`: Adjust confidence/statistics
- `markUsed()`: Track usage for decay

**Design Decision**: SQLite chosen for:
- Zero configuration
- ACID compliance
- File-based portability
- No server required

### 3. Memory Recall Module
**File**: `src/memory/recall.ts`

Retrieves relevant memories for an invoice.

**Algorithm:**
```
1. Get all memories for vendor
2. Filter by relevance:
   - Pattern appears in rawText?
   - Contextually relevant?
   - Confidence threshold met (≥0.3)?
3. Sort by confidence (descending)
4. Return relevant memories
```

**Relevance Logic:**
- **Vendor memories**: Always relevant for same vendor
- **Correction memories**: Contextual (e.g., missing_po_number only if PO is missing)
- **Resolution memories**: Generally relevant for similar scenarios

**Design Decision**: Conservative filtering prevents irrelevant memories from causing issues.

### 4. Memory Apply Module
**File**: `src/memory/apply.ts`

Applies memories to generate corrections.

**Two-Stage Process:**
1. **Generate corrections**: Each memory proposes corrections
2. **Auto-apply high-confidence**: Corrections ≥70% confidence applied automatically

**Pattern Application Examples:**

**Vendor Memory - Leistungsdatum:**
```typescript
Pattern: "Leistungsdatum"
Action: "extract_service_date"
Logic: Extract date from rawText using regex patterns
```

**Vendor Memory - VAT Inclusion:**
```typescript
Pattern: "MwSt. inkl."
Action: "recalculate_vat"
Logic: Back-calculate net from gross: net = gross / (1 + rate)
```

**Correction Memory - Qty Mismatch:**
```typescript
Pattern: "qty_mismatch"
Action: "adjust_to_delivery_note"
Logic: Compare invoice qty to delivery note qty
```

**Design Decision**: Separate generation from application allows human review before auto-applying.

### 5. Decision Engine
**File**: `src/decision/decision-engine.ts`

Decides whether to auto-accept, auto-correct, or escalate.

**Decision Matrix:**

| Confidence | Corrections | Critical Issues | Decision |
|------------|-------------|----------------|----------|
| ≥85% | 0 | No | **Auto-Accept** |
| ≥70% | All ≥70% | No | **Auto-Correct** |
| <70% | Any | No | **Escalate** |
| Any | Any | Yes | **Escalate** |

**Critical Issues:**
- Missing currency
- Potential duplicate
- Large discrepancies (>20%)
- Very low extraction confidence (<50%)

**Confidence Calculation:**
```
Base = Invoice extraction confidence
Boost = +0.1 for each high-confidence memory (max 3)
Adjust = Weight corrections: (base * 0.6) + (avg_correction_conf * 0.4)
Final = Clamp to [0, 1]
```

**Design Decision**: Multi-factor confidence prevents over-reliance on any single metric.

### 6. Learning Engine
**File**: `src/memory/learning.ts`

Learns from human corrections and updates memories.

**Learning Mechanisms:**

**1. Create New Memory:**
- Initial confidence: 0.6 (approved) or 0.4 (rejected)
- Extract pattern, type, and action from correction
- Store with full audit trail

**2. Reinforce Success:**
```
New confidence = Current + (0.05 * (1 - Current))
Success count += 1
```
- Diminishing returns prevent overconfidence
- Max confidence capped at 0.95

**3. Weaken Failure:**
```
New confidence = Current - 0.10
Failure count += 1
```
- Min confidence floored at 0.1
- Prevents complete elimination (allows recovery)

**4. Apply Decay:**
```
If unused for 30 days:
  New confidence = Current - 0.02
```
- Gradual weakening of unused patterns
- Prevents outdated patterns from dominating

**Pattern Extraction Logic:**

**Service Date:**
```
Keyword: "Leistungsdatum", "service date"
Type: vendor
Pattern: "Leistungsdatum"
Action: "extract_service_date"
```

**VAT Inclusion:**
```
Keyword: "inkl", "incl", "included"
Type: vendor
Pattern: "MwSt. inkl."
Action: "recalculate_vat"
```

**PO Number:**
```
Field: "poNumber"
Type: correction
Pattern: "missing_po_number"
Action: "match_by_items_and_vendor"
```

**Design Decision**: Heuristic pattern extraction allows immediate learning without training data.

## Data Flow

### Processing Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. INPUT                                                 │
│    - Extracted Invoice (with rawText)                   │
│    - Purchase Orders                                     │
│    - Delivery Notes                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. RECALL                                                │
│    - Query memories for vendor                          │
│    - Filter by relevance                                │
│    - Apply confidence threshold                         │
│    Output: Relevant memories                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. APPLY                                                 │
│    - Each memory generates corrections                  │
│    - Auto-apply high-confidence corrections             │
│    Output: Corrections + Normalized invoice             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. DECIDE                                                │
│    - Calculate overall confidence                       │
│    - Check for critical issues                          │
│    - Apply decision matrix                              │
│    Output: Decision + Reasoning                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 5. OUTPUT                                                │
│    - Normalized Invoice                                 │
│    - Proposed Corrections                               │
│    - Requires Human Review (bool)                       │
│    - Reasoning (string)                                 │
│    - Confidence Score (0-1)                             │
│    - Memory Updates                                      │
│    - Audit Trail                                         │
└─────────────────────────────────────────────────────────┘
```

### Learning Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. HUMAN CORRECTION INPUT                                │
│    - Invoice ID                                          │
│    - Vendor                                              │
│    - Corrections (field, from, to, reason)              │
│    - Final Decision (approved/rejected)                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. EXTRACT PATTERN                                       │
│    - Analyze correction reason                          │
│    - Determine memory type                              │
│    - Extract pattern and action                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. CHECK EXISTING                                        │
│    - Query for similar memory                           │
│    - Match on (type, vendor, pattern, action)           │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴────────┐
         │                 │
         ▼                 ▼
┌────────────────┐  ┌────────────────┐
│ EXISTS         │  │ NEW            │
│ - Reinforce    │  │ - Create       │
│ - Update stats │  │ - Set initial  │
└────────────────┘  └────────────────┘
         │                 │
         └───────┬─────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 4. PERSIST                                               │
│    - Save to database                                    │
│    - Update timestamps                                   │
│    - Return memory ID                                    │
└─────────────────────────────────────────────────────────┘
```

## Memory Types Deep Dive

### Vendor Memory
**Purpose**: Capture vendor-specific patterns

**Examples:**
- German vendors use "Leistungsdatum" for service date
- Some vendors include VAT in stated totals
- Vendor-specific SKU mappings from descriptions
- Discount term formats

**Lifecycle:**
1. Created from first occurrence
2. Reinforced by repeated success
3. Applied to future invoices from same vendor
4. Decays if vendor patterns change

### Correction Memory
**Purpose**: Learn recurring correction patterns

**Examples:**
- Quantity mismatches → check delivery note
- Missing PO numbers → match by line items
- Missing currency → extract from text

**Lifecycle:**
1. Created when correction applied
2. Generalized across vendors
3. Applied when similar issue detected
4. Weakened if correction fails

### Resolution Memory
**Purpose**: Track how discrepancies were resolved

**Examples:**
- Human approved vs rejected
- Helps avoid repeating failed suggestions

**Lifecycle:**
1. Created for each human decision
2. Influences confidence of related memories
3. Used in decision-making process

## Confidence System

### Confidence Scoring Philosophy

**Goal**: Reflect reliability without overconfidence

**Ranges:**
- 0.0 - 0.3: **Low** - Do not auto-apply
- 0.3 - 0.5: **Medium-Low** - Suggest with caution
- 0.5 - 0.7: **Medium** - Reliable suggestion
- 0.7 - 0.85: **High** - Auto-apply
- 0.85 - 1.0: **Very High** - Fully trusted

**Evolution:**
```
Initial: 0.6 (approved) or 0.4 (rejected)
  ↓
Success: +5% per success (diminishing returns)
  ↓
Failure: -10% per failure
  ↓
Decay: -2% per month if unused
  ↓
Bounds: [0.1, 0.95]
```

**Design Decision**: 
- 0.95 cap prevents blind trust
- 0.1 floor allows recovery from mistakes
- Diminishing returns prevent rapid confidence inflation

## Duplicate Detection

**Algorithm:**
```
For each existing invoice:
  If (same vendor AND 
      same invoice number AND 
      dates within 7 days):
    → Flag as duplicate
```

**Rationale:**
- Prevents processing same invoice twice
- Avoids contradictory memories
- 7-day window catches resubmissions

## Audit Trail

Every step logs:
- **Step**: recall, apply, decide, learn
- **Timestamp**: ISO 8601 format
- **Details**: Human-readable description

**Purpose:**
- Debugging and troubleshooting
- Compliance and auditability
- Understanding system decisions

## Scalability Considerations

### Current Design
- Single SQLite database
- In-process execution
- File-based storage

### Production Enhancements
- PostgreSQL for multi-user scenarios
- Redis for memory caching
- Message queue for async processing
- Horizontal scaling with shared database

## Security Considerations

### Preventing Bad Learnings

1. **Confidence thresholds**: Block low-confidence auto-apply
2. **Human review gates**: Critical issues always escalated
3. **Reinforcement learning**: Bad patterns naturally weaken
4. **Decay mechanism**: Outdated patterns fade away
5. **Audit trail**: All decisions traceable

### Data Integrity

- ACID transactions via SQLite
- Unique constraints prevent duplicates
- Timestamps track all changes

## Testing Strategy

### Heuristic Validation
- Pattern matching accuracy
- Confidence evolution correctness
- Decision logic coverage

### Integration Testing
- End-to-end invoice processing
- Learning from corrections
- Memory recall accuracy

### Demo as Test
- Verifies all expected outcomes
- Demonstrates learning over time
- Validates duplicate detection

## Future Enhancements

### Short Term
- ✅ Memory visualization UI
- ✅ Confidence decay scheduling
- ✅ Export/import memories

### Medium Term
- 🔄 ML-based pattern recognition
- 🌍 Multi-language support
- 📊 Analytics dashboard

### Long Term
- 🤖 Active learning suggestions
- 🌐 Multi-tenant support
- 🔗 Integration with popular ERPs

## Conclusion

This design prioritizes:
1. **Explainability** over black-box ML
2. **Safety** over aggressive automation
3. **Continuous improvement** over one-time training
4. **Production readiness** over proof-of-concept

The result is a practical, maintainable system that delivers real value while remaining understandable and auditable.
