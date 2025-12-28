/**
 * SQLite persistence layer for memory storage
 */

import Database from 'better-sqlite3';
import { Memory, MemoryType } from '../types/memory';
import path from 'path';

export class MemoryStore {
  private db: Database.Database;

  constructor(dbPath: string = './memory.db') {
    const fullPath = path.resolve(dbPath);
    this.db = new Database(fullPath);
    this.initDatabase();
  }

  private initDatabase(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        vendor TEXT NOT NULL,
        pattern TEXT NOT NULL,
        action TEXT NOT NULL,
        confidence REAL NOT NULL,
        occurrences INTEGER NOT NULL DEFAULT 1,
        successCount INTEGER NOT NULL DEFAULT 0,
        failureCount INTEGER NOT NULL DEFAULT 0,
        createdAt TEXT NOT NULL,
        lastUsedAt TEXT NOT NULL,
        lastUpdatedAt TEXT NOT NULL,
        resolutionType TEXT,
        UNIQUE(type, vendor, pattern, action)
      );

      CREATE INDEX IF NOT EXISTS idx_vendor ON memories(vendor);
      CREATE INDEX IF NOT EXISTS idx_type ON memories(type);
      CREATE INDEX IF NOT EXISTS idx_pattern ON memories(pattern);
      CREATE INDEX IF NOT EXISTS idx_confidence ON memories(confidence);
    `);
  }

  /**
   * Store or update a memory entry
   */
  saveMemory(memory: Omit<Memory, 'id'>): number {
    const now = new Date().toISOString();
    
    const stmt = this.db.prepare(`
      INSERT INTO memories (
        type, vendor, pattern, action, confidence, occurrences,
        successCount, failureCount, createdAt, lastUsedAt, lastUpdatedAt, resolutionType
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(type, vendor, pattern, action) DO UPDATE SET
        confidence = excluded.confidence,
        occurrences = occurrences + 1,
        successCount = excluded.successCount,
        failureCount = excluded.failureCount,
        lastUpdatedAt = excluded.lastUpdatedAt
      RETURNING id
    `);

    const resolutionType = memory.type === 'resolution' 
      ? (memory as any).resolutionType 
      : null;

    const result = stmt.get(
      memory.type,
      memory.vendor,
      memory.pattern,
      memory.action,
      memory.confidence,
      memory.occurrences,
      memory.successCount,
      memory.failureCount,
      now,
      now,
      now,
      resolutionType
    ) as { id: number };

    return result.id;
  }

  /**
   * Retrieve memories for a specific vendor and type
   */
  getMemories(vendor: string, type?: MemoryType): Memory[] {
    let query = `SELECT * FROM memories WHERE vendor = ?`;
    const params: any[] = [vendor];

    if (type) {
      query += ` AND type = ?`;
      params.push(type);
    }

    query += ` ORDER BY confidence DESC, occurrences DESC`;

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as Memory[];
  }

  /**
   * Find memories by pattern
   */
  findByPattern(pattern: string, vendor?: string): Memory[] {
    let query = `SELECT * FROM memories WHERE pattern LIKE ?`;
    const params: any[] = [`%${pattern}%`];

    if (vendor) {
      query += ` AND vendor = ?`;
      params.push(vendor);
    }

    query += ` ORDER BY confidence DESC`;

    const stmt = this.db.prepare(query);
    return stmt.all(...params) as Memory[];
  }

  /**
   * Update memory confidence and statistics
   */
  updateMemory(id: number, updates: Partial<Memory>): void {
    const fields: string[] = [];
    const values: any[] = [];

    if (updates.confidence !== undefined) {
      fields.push('confidence = ?');
      values.push(updates.confidence);
    }

    if (updates.successCount !== undefined) {
      fields.push('successCount = ?');
      values.push(updates.successCount);
    }

    if (updates.failureCount !== undefined) {
      fields.push('failureCount = ?');
      values.push(updates.failureCount);
    }

    if (updates.occurrences !== undefined) {
      fields.push('occurrences = ?');
      values.push(updates.occurrences);
    }

    if (fields.length === 0) return;

    fields.push('lastUpdatedAt = ?');
    values.push(new Date().toISOString());

    values.push(id);

    const query = `UPDATE memories SET ${fields.join(', ')} WHERE id = ?`;
    const stmt = this.db.prepare(query);
    stmt.run(...values);
  }

  /**
   * Mark memory as used
   */
  markUsed(id: number): void {
    const stmt = this.db.prepare(`
      UPDATE memories 
      SET lastUsedAt = ?, occurrences = occurrences + 1
      WHERE id = ?
    `);
    stmt.run(new Date().toISOString(), id);
  }

  /**
   * Get memory by ID
   */
  getById(id: number): Memory | null {
    const stmt = this.db.prepare(`SELECT * FROM memories WHERE id = ?`);
    return stmt.get(id) as Memory | null;
  }

  /**
   * Get all memories (for debugging/inspection)
   */
  getAllMemories(): Memory[] {
    const stmt = this.db.prepare(`SELECT * FROM memories ORDER BY createdAt DESC`);
    return stmt.all() as Memory[];
  }

  /**
   * Clear all memories (for testing)
   */
  clearMemories(): void {
    this.db.prepare(`DELETE FROM memories`).run();
  }

  /**
   * Close database connection
   */
  close(): void {
    this.db.close();
  }
}
