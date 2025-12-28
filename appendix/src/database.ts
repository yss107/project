import Database from 'better-sqlite3';
import * as path from 'path';
import {
  VendorMemory,
  CorrectionMemory,
  ResolutionMemory,
  DuplicateMemory
} from './types';

export class MemoryDatabase {
  private db: Database.Database;

  constructor(dbPath: string = path.join(__dirname, '../memory.db')) {
    this.db = new Database(dbPath);
    this.initializeSchema();
  }

  private initializeSchema(): void {
    // Vendor memory table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS vendor_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor TEXT NOT NULL,
        pattern TEXT NOT NULL,
        fieldMapping TEXT NOT NULL,
        confidence REAL NOT NULL,
        usageCount INTEGER DEFAULT 0,
        successCount INTEGER DEFAULT 0,
        lastUsed TEXT,
        created TEXT NOT NULL
      )
    `);

    // Correction memory table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS correction_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor TEXT NOT NULL,
        pattern TEXT NOT NULL,
        correctionType TEXT NOT NULL,
        correctionLogic TEXT NOT NULL,
        confidence REAL NOT NULL,
        usageCount INTEGER DEFAULT 0,
        successCount INTEGER DEFAULT 0,
        lastUsed TEXT,
        created TEXT NOT NULL
      )
    `);

    // Resolution memory table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS resolution_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor TEXT NOT NULL,
        invoiceNumber TEXT NOT NULL,
        decision TEXT NOT NULL,
        corrections TEXT NOT NULL,
        timestamp TEXT NOT NULL
      )
    `);

    // Duplicate memory table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS duplicate_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor TEXT NOT NULL,
        invoiceNumber TEXT NOT NULL,
        invoiceDate TEXT NOT NULL,
        invoiceId TEXT NOT NULL,
        timestamp TEXT NOT NULL
      )
    `);
  }

  // Vendor Memory operations
  saveVendorMemory(memory: VendorMemory): number {
    const stmt = this.db.prepare(`
      INSERT INTO vendor_memory (vendor, pattern, fieldMapping, confidence, usageCount, successCount, lastUsed, created)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      memory.vendor,
      memory.pattern,
      memory.fieldMapping,
      memory.confidence,
      memory.usageCount || 0,
      memory.successCount || 0,
      memory.lastUsed || null,
      memory.created
    );
    return result.lastInsertRowid as number;
  }

  getVendorMemories(vendor: string): VendorMemory[] {
    const stmt = this.db.prepare(`
      SELECT * FROM vendor_memory WHERE vendor = ? ORDER BY confidence DESC
    `);
    return stmt.all(vendor) as VendorMemory[];
  }

  updateVendorMemoryUsage(id: number, success: boolean): void {
    const memory = this.db.prepare('SELECT * FROM vendor_memory WHERE id = ?').get(id) as VendorMemory;
    if (!memory) return;

    const newUsageCount = memory.usageCount + 1;
    const newSuccessCount = success ? memory.successCount + 1 : memory.successCount;
    const newConfidence = newSuccessCount / newUsageCount;

    this.db.prepare(`
      UPDATE vendor_memory
      SET usageCount = ?, successCount = ?, confidence = ?, lastUsed = ?
      WHERE id = ?
    `).run(newUsageCount, newSuccessCount, newConfidence, new Date().toISOString(), id);
  }

  // Correction Memory operations
  saveCorrectionMemory(memory: CorrectionMemory): number {
    const stmt = this.db.prepare(`
      INSERT INTO correction_memory (vendor, pattern, correctionType, correctionLogic, confidence, usageCount, successCount, lastUsed, created)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      memory.vendor,
      memory.pattern,
      memory.correctionType,
      memory.correctionLogic,
      memory.confidence,
      memory.usageCount || 0,
      memory.successCount || 0,
      memory.lastUsed || null,
      memory.created
    );
    return result.lastInsertRowid as number;
  }

  getCorrectionMemories(vendor: string): CorrectionMemory[] {
    const stmt = this.db.prepare(`
      SELECT * FROM correction_memory WHERE vendor = ? ORDER BY confidence DESC
    `);
    return stmt.all(vendor) as CorrectionMemory[];
  }

  updateCorrectionMemoryUsage(id: number, success: boolean): void {
    const memory = this.db.prepare('SELECT * FROM correction_memory WHERE id = ?').get(id) as CorrectionMemory;
    if (!memory) return;

    const newUsageCount = memory.usageCount + 1;
    const newSuccessCount = success ? memory.successCount + 1 : memory.successCount;
    const newConfidence = newSuccessCount / newUsageCount;

    this.db.prepare(`
      UPDATE correction_memory
      SET usageCount = ?, successCount = ?, confidence = ?, lastUsed = ?
      WHERE id = ?
    `).run(newUsageCount, newSuccessCount, newConfidence, new Date().toISOString(), id);
  }

  // Resolution Memory operations
  saveResolutionMemory(memory: ResolutionMemory): number {
    const stmt = this.db.prepare(`
      INSERT INTO resolution_memory (vendor, invoiceNumber, decision, corrections, timestamp)
      VALUES (?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      memory.vendor,
      memory.invoiceNumber,
      memory.decision,
      memory.corrections,
      memory.timestamp
    );
    return result.lastInsertRowid as number;
  }

  getResolutionMemories(vendor: string): ResolutionMemory[] {
    const stmt = this.db.prepare(`
      SELECT * FROM resolution_memory WHERE vendor = ? ORDER BY timestamp DESC
    `);
    return stmt.all(vendor) as ResolutionMemory[];
  }

  // Duplicate Memory operations
  saveDuplicateMemory(memory: DuplicateMemory): number {
    const stmt = this.db.prepare(`
      INSERT INTO duplicate_memory (vendor, invoiceNumber, invoiceDate, invoiceId, timestamp)
      VALUES (?, ?, ?, ?, ?)
    `);
    const result = stmt.run(
      memory.vendor,
      memory.invoiceNumber,
      memory.invoiceDate,
      memory.invoiceId,
      memory.timestamp
    );
    return result.lastInsertRowid as number;
  }

  findDuplicates(vendor: string, invoiceNumber: string, invoiceDate: string): DuplicateMemory[] {
    const stmt = this.db.prepare(`
      SELECT * FROM duplicate_memory 
      WHERE vendor = ? AND invoiceNumber = ?
    `);
    const duplicates = stmt.all(vendor, invoiceNumber) as DuplicateMemory[];
    
    // Helper function to parse various date formats
    const parseDate = (dateStr: string): Date | null => {
      // Try DD.MM.YYYY format
      const ddmmyyyyMatch = dateStr.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
      if (ddmmyyyyMatch) {
        const [, day, month, year] = ddmmyyyyMatch;
        return new Date(`${year}-${month}-${day}`);
      }
      
      // Try DD-MM-YYYY format
      const ddmmyyyyDashMatch = dateStr.match(/^(\d{2})-(\d{2})-(\d{4})$/);
      if (ddmmyyyyDashMatch) {
        const [, day, month, year] = ddmmyyyyDashMatch;
        return new Date(`${year}-${month}-${day}`);
      }
      
      // Try standard formats
      const date = new Date(dateStr);
      return isNaN(date.getTime()) ? null : date;
    };
    
    const currentDate = parseDate(invoiceDate);
    if (!currentDate) {
      // If we can't parse the date, just return exact matches
      return duplicates;
    }
    
    // Also check for dates within 7 days
    return duplicates.filter(dup => {
      const dupDate = parseDate(dup.invoiceDate);
      if (!dupDate) return true; // Include if we can't parse (exact match on invoice number)
      
      const diffDays = Math.abs((currentDate.getTime() - dupDate.getTime()) / (1000 * 60 * 60 * 24));
      return diffDays <= 7;
    });
  }

  close(): void {
    this.db.close();
  }
}
