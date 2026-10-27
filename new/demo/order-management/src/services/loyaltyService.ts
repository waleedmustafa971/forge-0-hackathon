import type { InMemoryDatabase } from '../db/database.ts';
import { ValidationError } from '../domain/types.ts';

const TABLE = 'loyalty';

/** Point balances already read, so repeated look-ups skip the database. */
const balances = new Map<string, number>();

export class LoyaltyService {
  private readonly db: InMemoryDatabase;

  constructor(db: InMemoryDatabase) {
    this.db = db;
  }

  /** Awards one point per whole currency unit spent and returns the new balance. */
  async award(customerId: string, amountSpent: number): Promise<number> {
    if (!Number.isFinite(amountSpent) || amountSpent < 0) {
      throw new ValidationError(`Invalid amount for loyalty points: ${amountSpent}`);
    }
    const next = (await this.points(customerId)) + Math.floor(amountSpent);
    await this.db.put(TABLE, customerId, { customerId, points: next });
    balances.set(customerId, next);
    return next;
  }

  async points(customerId: string): Promise<number> {
    const cached = balances.get(customerId);
    if (cached !== undefined) return cached;
    const row = await this.db.get<{ points: number }>(TABLE, customerId);
    const points = row?.points ?? 0;
    balances.set(customerId, points);
    return points;
  }
}
