// Hidden evaluation test: copied to test/hidden/ in a disposable copy by the benchmark harness.
import assert from 'node:assert/strict';
import { it } from 'node:test';
import type { RefundRecord } from '../../src/domain/types.ts';
import { seededApp } from '../helpers.ts';

it('[hidden] refund covers every unit of a multi-quantity line', async () => {
  const app = await seededApp();
  const order = await app.orderService.placeOrder({ customerId: 'c', items: [{ sku: 'SKU-CABLE', quantity: 3 }] });
  await app.orderService.transition(order.id, 'paid');
  const refund = await app.refundService.refund(order.id);
  assert.equal(refund.amount, 21.75);
  assert.equal(await app.inventory.available(app.db, 'SKU-CABLE'), 50);
});

it('[hidden] restocks three lines of the same SKU', async () => {
  const app = await seededApp({ 'SKU-MOUSE': 10 });
  const order = await app.orderService.placeOrder({
    customerId: 'c',
    items: [
      { sku: 'SKU-MOUSE', quantity: 1 },
      { sku: 'SKU-MOUSE', quantity: 1 },
      { sku: 'SKU-MOUSE', quantity: 2 },
    ],
  });
  await app.orderService.transition(order.id, 'paid');
  await app.refundService.refund(order.id);
  assert.equal(await app.inventory.available(app.db, 'SKU-MOUSE'), 10);
});

it('[hidden] persists the refund record with the order total', async () => {
  const app = await seededApp();
  const order = await app.orderService.placeOrder({
    customerId: 'c',
    items: [
      { sku: 'SKU-KEYBOARD', quantity: 2 },
      { sku: 'SKU-MOUSE', quantity: 1 },
    ],
  });
  await app.orderService.transition(order.id, 'paid');
  const refund = await app.refundService.refund(order.id);
  const stored = await app.db.get<RefundRecord>('refunds', refund.id);
  assert.equal(stored?.amount, order.total);
});
