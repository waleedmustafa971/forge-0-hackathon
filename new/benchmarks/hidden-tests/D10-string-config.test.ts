// Hidden evaluation test: copied to test/hidden/ in a disposable copy by the benchmark harness.
import assert from 'node:assert/strict';
import { it } from 'node:test';
import { loadFees } from '../../src/config/fees.ts';
import { seededApp } from '../helpers.ts';

it('[hidden] gift wrapping is added to orders above the free-handling threshold', async () => {
  const app = await seededApp();
  const quote = await app.quoteService.quote([{ sku: 'SKU-MONITOR', quantity: 1 }], { giftWrap: true });
  assert.equal(quote.total, 193);
});

it('[hidden] small gift-wrapped orders pay handling and gift wrapping', async () => {
  const app = await seededApp();
  const quote = await app.quoteService.quote([{ sku: 'SKU-MOUSE', quantity: 1 }], { giftWrap: true });
  assert.equal(quote.total, 26.49);
});

it('[hidden] every loaded fee is a number', () => {
  const fees = loadFees();
  for (const value of Object.values(fees)) assert.equal(typeof value, 'number');
});
