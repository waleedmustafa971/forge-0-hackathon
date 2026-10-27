import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { ValidationError } from '../src/domain/types.ts';
import { seededApp } from './helpers.ts';

describe('catalog prices', () => {
  it('quotes the list price of several SKUs', async () => {
    const app = await seededApp();
    const quote = await app.catalogService.quote(['SKU-KEYBOARD', 'SKU-CABLE']);
    assert.deepEqual(quote, { 'SKU-KEYBOARD': 49.5, 'SKU-CABLE': 7.25 });
  });

  it('rejects non-positive prices', async () => {
    const app = await seededApp();
    await assert.rejects(app.catalogService.updatePrice('SKU-MOUSE', 0), ValidationError);
    assert.deepEqual(await app.catalogService.quote(['SKU-MOUSE']), { 'SKU-MOUSE': 19.99 });
  });

  it('quotes the new price after a price change', async () => {
    const app = await seededApp();
    assert.deepEqual(await app.catalogService.quote(['SKU-MOUSE']), { 'SKU-MOUSE': 19.99 });
    await app.catalogService.updatePrice('SKU-MOUSE', 17.5);
    assert.deepEqual(await app.catalogService.quote(['SKU-MOUSE']), { 'SKU-MOUSE': 17.5 });
  });
});
