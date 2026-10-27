import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { seededApp } from './helpers.ts';

// The pricing backend is rate-limited: repeated quotes must be served from the cache.
describe('pricing cache', () => {
  it('looks each SKU up at most once across repeated quotes', async () => {
    const app = await seededApp();
    for (let i = 0; i < 3; i++) {
      await app.catalogService.quote(['SKU-KEYBOARD', 'SKU-MOUSE']);
    }
    assert.equal(app.priceBook.lookups, 2);
  });

  it('does not look up SKUs that were never quoted', async () => {
    const app = await seededApp();
    await app.catalogService.quote(['SKU-CABLE']);
    assert.equal(app.priceBook.lookups, 1);
  });
});
