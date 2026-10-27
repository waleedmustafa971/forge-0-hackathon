import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { ValidationError } from '../src/domain/types.ts';
import { seededApp } from './helpers.ts';

describe('order quotes', () => {
  it('adds the handling fee to small orders', async () => {
    const app = await seededApp();
    const quote = await app.quoteService.quote([{ sku: 'SKU-MOUSE', quantity: 1 }]);
    assert.equal(quote.merchandise, 19.99);
    assert.equal(quote.total, 22.49);
  });

  it('waives handling at the free-handling threshold', async () => {
    const app = await seededApp();
    const quote = await app.quoteService.quote([{ sku: 'SKU-MONITOR', quantity: 1 }]);
    assert.equal(quote.handling, 0);
    assert.equal(quote.total, 189);
  });

  it('rejects an empty quote', async () => {
    const app = await seededApp();
    await assert.rejects(app.quoteService.quote([]), ValidationError);
  });
});
