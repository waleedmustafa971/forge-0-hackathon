// Hidden evaluation test: copied to test/hidden/ in a disposable copy by the benchmark harness.
import assert from 'node:assert/strict';
import { it } from 'node:test';
import { seededApp } from '../helpers.ts';

async function completeOrders(customerId: string, skus: string[]) {
  const app = await seededApp();
  const orders = [];
  for (const sku of skus) {
    const order = await app.orderService.placeOrder({ customerId, items: [{ sku, quantity: 1 }] });
    await app.checkoutService.complete(order);
    orders.push(order);
  }
  return { app, orders };
}

it('[hidden] sends exactly one receipt per completed order', async () => {
  const { app, orders } = await completeOrders('cust-hidden-11a', ['SKU-KEYBOARD', 'SKU-MOUSE', 'SKU-CABLE']);
  assert.deepEqual(
    app.receiptService.sent.map((receipt) => receipt.orderId),
    orders.map((order) => order.id),
  );
});

it('[hidden] the subscriber list does not grow with every checkout', async () => {
  const app = await seededApp();
  const counts = [];
  for (const sku of ['SKU-KEYBOARD', 'SKU-MOUSE', 'SKU-CABLE']) {
    const order = await app.orderService.placeOrder({ customerId: 'cust-hidden-11b', items: [{ sku, quantity: 1 }] });
    await app.checkoutService.complete(order);
    counts.push(app.bus.listenerCount('order.paid'));
  }
  assert.equal(counts[2], counts[0]);
});

it('[hidden] points accumulate once per order over several checkouts', async () => {
  const { app } = await completeOrders('cust-hidden-11c', ['SKU-KEYBOARD', 'SKU-MOUSE', 'SKU-CABLE']);
  assert.equal(await app.loyaltyService.points('cust-hidden-11c'), 49 + 19 + 7);
});
