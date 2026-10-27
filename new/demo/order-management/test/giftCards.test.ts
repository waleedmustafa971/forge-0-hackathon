import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { InvalidGiftCardError } from '../src/domain/types.ts';
import { seededApp } from './helpers.ts';

describe('gift cards', () => {
  it('issues a card with the requested balance', async () => {
    const app = await seededApp();
    const card = await app.giftCardService.issue(50);
    assert.match(card.code, /^GC-0001-[0-9A-Z]{4}$/);
    assert.equal(card.balance, 50);
  });

  it('rejects malformed codes', async () => {
    const app = await seededApp();
    await assert.rejects(app.giftCardService.redeem('not-a-card', 5), InvalidGiftCardError);
  });

  it('redeems part of a card balance', async () => {
    const app = await seededApp();
    const card = await app.giftCardService.issue(40);
    assert.equal(await app.giftCardService.redeem(card.code, 15), 25);
  });
});
