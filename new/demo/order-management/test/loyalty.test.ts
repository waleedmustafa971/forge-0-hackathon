import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { ValidationError } from '../src/domain/types.ts';
import { seededApp } from './helpers.ts';

describe('loyalty points', () => {
  it('awards one point per whole unit spent', async () => {
    const app = await seededApp();
    assert.equal(await app.loyaltyService.award('cust-1', 49.5), 49);
    assert.equal(await app.loyaltyService.award('cust-1', 19.99), 68);
    assert.equal(await app.loyaltyService.points('cust-1'), 68);
  });

  it('rejects negative amounts', async () => {
    const app = await seededApp();
    await assert.rejects(app.loyaltyService.award('cust-2', -5), ValidationError);
  });

  it('starts every new account at zero points', async () => {
    const app = await seededApp();
    assert.equal(await app.loyaltyService.points('cust-1'), 0);
    assert.equal(await app.loyaltyService.award('cust-1', 10), 10);
  });
});
