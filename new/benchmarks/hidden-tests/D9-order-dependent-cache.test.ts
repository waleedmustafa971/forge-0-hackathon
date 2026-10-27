// Hidden evaluation test: copied to test/hidden/ in a disposable copy by the benchmark harness.
import assert from 'node:assert/strict';
import { it } from 'node:test';
import { seededApp } from '../helpers.ts';

it('[hidden] separate apps never share loyalty balances', async () => {
  const first = await seededApp();
  const second = await seededApp();
  await first.loyaltyService.award('cust-9', 120);
  assert.equal(await second.loyaltyService.points('cust-9'), 0);
  assert.equal(await second.loyaltyService.award('cust-9', 5), 5);
  assert.equal(await first.loyaltyService.points('cust-9'), 120);
});

it('[hidden] balances accumulate within one app', async () => {
  const app = await seededApp();
  await app.loyaltyService.award('cust-3', 10.9);
  await app.loyaltyService.award('cust-3', 20.1);
  assert.equal(await app.loyaltyService.points('cust-3'), 30);
});

it('[hidden] a fresh app reads balances persisted in its own database', async () => {
  const app = await seededApp();
  await app.db.put('loyalty', 'cust-4', { customerId: 'cust-4', points: 7 });
  assert.equal(await app.loyaltyService.points('cust-4'), 7);
});
