import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { seededApp } from './helpers.ts';

async function order(app: Awaited<ReturnType<typeof seededApp>>, customerId: string, sku: string) {
  return app.orderService.placeOrder({ customerId, items: [{ sku, quantity: 1 }] });
}

describe('checkout events', () => {
  it('sends a receipt for a completed order', async () => {
    const app = await seededApp();
    const placed = await order(app, 'cust-events-1', 'SKU-KEYBOARD');
    await app.checkoutService.complete(placed);
    assert.deepEqual(app.receiptService.sent, [
      { orderId: placed.id, customerId: 'cust-events-1', amount: 49.5 },
    ]);
  });

  it('captures the order total', async () => {
    const app = await seededApp();
    const placed = await order(app, 'cust-events-2', 'SKU-MOUSE');
    await app.checkoutService.complete(placed);
    assert.deepEqual(
      app.paymentGateway.charges.map((c) => c.amount),
      [19.99],
    );
  });

  it('awards loyalty points once per completed order', async () => {
    const app = await seededApp();
    await app.checkoutService.complete(await order(app, 'cust-events-3', 'SKU-KEYBOARD'));
    await app.checkoutService.complete(await order(app, 'cust-events-3', 'SKU-MOUSE'));
    assert.equal(await app.loyaltyService.points('cust-events-3'), 49 + 19);
  });
});
