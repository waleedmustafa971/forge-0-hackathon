// Hidden evaluation test: copied to test/hidden/ in a disposable copy by the benchmark harness.
import assert from 'node:assert/strict';
import { it } from 'node:test';
import { seededApp } from '../helpers.ts';

it('[hidden] every price change is visible to the next quote', async () => {
  const app = await seededApp();
  await app.catalogService.quote(['SKU-CABLE']);
  await app.catalogService.updatePrice('SKU-CABLE', 8);
  assert.deepEqual(await app.catalogService.quote(['SKU-CABLE']), { 'SKU-CABLE': 8 });
  await app.catalogService.updatePrice('SKU-CABLE', 6.5);
  assert.deepEqual(await app.catalogService.quote(['SKU-CABLE']), { 'SKU-CABLE': 6.5 });
});

it('[hidden] unchanged SKUs stay cached after another SKU changes price', async () => {
  const app = await seededApp();
  await app.catalogService.quote(['SKU-KEYBOARD', 'SKU-MOUSE']);
  await app.catalogService.updatePrice('SKU-MOUSE', 17.5);
  for (let i = 0; i < 2; i++) {
    assert.deepEqual(await app.catalogService.quote(['SKU-KEYBOARD', 'SKU-MOUSE']), {
      'SKU-KEYBOARD': 49.5,
      'SKU-MOUSE': 17.5,
    });
  }
  assert.equal(app.priceBook.lookups, 3);
});

it('[hidden] a price set before the first quote is used', async () => {
  const app = await seededApp();
  await app.catalogService.updatePrice('SKU-MONITOR', 150);
  assert.deepEqual(await app.catalogService.quote(['SKU-MONITOR']), { 'SKU-MONITOR': 150 });
  assert.equal(app.priceBook.lookups, 1);
});
