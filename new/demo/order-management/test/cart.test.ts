import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { ValidationError } from '../src/domain/types.ts';
import { seededApp } from './helpers.ts';

describe('shopping cart', () => {
  it('merges repeated additions of the same product', async () => {
    const app = await seededApp();
    app.cartService.add('cust-cart-1', 'SKU-MOUSE');
    const lines = app.cartService.add('cust-cart-1', 'SKU-MOUSE', 2);
    assert.deepEqual(lines, [{ productId: 2207, sku: 'SKU-MOUSE', quantity: 3 }]);
  });

  it('removes a product from the cart', async () => {
    const app = await seededApp();
    app.cartService.add('cust-cart-2', 'SKU-MONITOR');
    assert.deepEqual(app.cartService.remove('cust-cart-2', 'SKU-MONITOR'), []);
  });

  it('rejects unknown products', async () => {
    const app = await seededApp();
    assert.throws(() => app.cartService.add('cust-cart-3', 'SKU-NOPE'), ValidationError);
  });

  it('lists lines in the order they were added', async () => {
    const app = await seededApp();
    app.cartService.add('cust-cart-4', 'SKU-KEYBOARD');
    app.cartService.add('cust-cart-4', 'SKU-CABLE');
    app.cartService.add('cust-cart-4', 'SKU-MOUSE');
    assert.deepEqual(
      app.cartService.lines('cust-cart-4').map((line) => line.sku),
      ['SKU-KEYBOARD', 'SKU-CABLE', 'SKU-MOUSE'],
    );
  });
});
