import { randomUUID } from 'node:crypto';
import type { InMemoryDatabase } from '../db/database.ts';
import { assertTransition } from '../domain/status.ts';
import type { RefundRecord } from '../domain/types.ts';
import type { InventoryRepository } from '../repositories/inventoryRepository.ts';
import type { OrderRepository } from '../repositories/orderRepository.ts';

export class RefundService {
  private readonly db: InMemoryDatabase;
  private readonly orders: OrderRepository;
  private readonly inventory: InventoryRepository;

  constructor(db: InMemoryDatabase, orders: OrderRepository, inventory: InventoryRepository) {
    this.db = db;
    this.orders = orders;
    this.inventory = inventory;
  }

  /** Refunds a paid order in full and returns every line item to stock. */
  async refund(orderId: string): Promise<RefundRecord> {
    const order = await this.orders.get(this.db, orderId);
    assertTransition(order.status, 'refunded');
    const amount = order.items.reduce((sum, item) => sum + item.unitPrice, 0);
    await Promise.all(order.items.map((item) => this.inventory.release(this.db, item.sku, item.quantity)));
    const record: RefundRecord = { id: randomUUID(), orderId, amount, createdAt: new Date().toISOString() };
    await this.db.put('refunds', record.id, { ...record });
    order.status = 'refunded';
    order.version += 1;
    await this.orders.update(this.db, order);
    return record;
  }
}
