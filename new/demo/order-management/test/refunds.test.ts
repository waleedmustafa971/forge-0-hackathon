import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { InvalidTransitionError } from '../src/domain/types.ts';
import { seededApp } from './helpers.ts';

describe('refunds', () => {
  it('refuses to refund an unpaid order', async () => {
    const app = await seededApp();
    const order = await app.orderService.placeOrder({
      customerId: 'cust-1',
      items: [{ sku: 'SKU-MOUSE', quantity: 1 }],
    });
    await assert.rejects(app.refundService.refund(order.id), InvalidTransitionError);
    assert.equal(await app.inventory.available(app.db, 'SKU-MOUSE'), 9);
  });

  it('refunds a single-item order and restocks it', async () => {
    const app = await seededApp();
    const order = await app.orderService.placeOrder({
      customerId: 'cust-1',
      items: [{ sku: 'SKU-MONITOR', quantity: 1 }],
    });
    await app.orderService.transition(order.id, 'paid');
    const refund = await app.refundService.refund(order.id);
    assert.equal(refund.amount, 189);
    assert.equal(await app.inventory.available(app.db, 'SKU-MONITOR'), 5);
    assert.equal((await app.orderService.getOrder(order.id)).status, 'refunded');
  });

  it('refunds the full amount and restocks every line of the order', async () => {
    const app = await seededApp({ 'SKU-KEYBOARD': 10, 'SKU-CABLE': 50 });
    const order = await app.orderService.placeOrder({
      customerId: 'cust-1',
      items: [
        { sku: 'SKU-KEYBOARD', quantity: 1 },
        { sku: 'SKU-CABLE', quantity: 4 },
        { sku: 'SKU-KEYBOARD', quantity: 2 },
      ],
    });
    await app.orderService.transition(order.id, 'paid');
    const refund = await app.refundService.refund(order.id);
    assert.equal(refund.amount, order.total, 'the refund must cover the whole order');
    assert.equal(await app.inventory.available(app.db, 'SKU-KEYBOARD'), 10);
    assert.equal(await app.inventory.available(app.db, 'SKU-CABLE'), 50);
    assert.equal((await app.orderService.getOrder(order.id)).status, 'refunded');
  });
});
