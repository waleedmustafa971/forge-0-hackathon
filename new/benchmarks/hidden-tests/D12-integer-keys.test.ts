// Hidden evaluation test: copied to test/hidden/ in a disposable copy by the benchmark harness.
import assert from 'node:assert/strict';
import { it } from 'node:test';
import { seededApp } from '../helpers.ts';

it('[hidden] checkout lists order items in cart order', async () => {
  const app = await seededApp();
  for (const sku of ['SKU-MONITOR', 'SKU-CABLE', 'SKU-KEYBOARD']) app.cartService.add('cust-hidden-12a', sku);
  const order = await app.orderService.placeOrder({
    customerId: 'cust-hidden-12a',
    items: app.cartService.toOrderItems('cust-hidden-12a'),
  });
  assert.deepEqual(order.items.map((item) => item.sku), ['SKU-MONITOR', 'SKU-CABLE', 'SKU-KEYBOARD']);
});

it('[hidden] adding more of a product keeps its original position', async () => {
  const app = await seededApp();
  app.cartService.add('cust-hidden-12b', 'SKU-MOUSE');
  app.cartService.add('cust-hidden-12b', 'SKU-CABLE');
  const lines = app.cartService.add('cust-hidden-12b', 'SKU-MOUSE', 2);
  assert.deepEqual(lines.map((line) => [line.sku, line.quantity]), [['SKU-MOUSE', 3], ['SKU-CABLE', 1]]);
});

it('[hidden] removing and re-adding a product moves it to the end', async () => {
  const app = await seededApp();
  for (const sku of ['SKU-KEYBOARD', 'SKU-CABLE']) app.cartService.add('cust-hidden-12c', sku);
  app.cartService.remove('cust-hidden-12c', 'SKU-KEYBOARD');
  app.cartService.add('cust-hidden-12c', 'SKU-KEYBOARD');
  assert.deepEqual(app.cartService.lines('cust-hidden-12c').map((line) => line.sku), ['SKU-CABLE', 'SKU-KEYBOARD']);
});
