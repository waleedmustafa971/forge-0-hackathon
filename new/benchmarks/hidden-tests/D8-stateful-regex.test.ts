// Hidden evaluation test: copied to test/hidden/ in a disposable copy by the benchmark harness.
import assert from 'node:assert/strict';
import { it } from 'node:test';
import { isGiftCardCode } from '../../src/domain/giftCardCode.ts';
import { seededApp } from '../helpers.ts';

it('[hidden] a valid code is accepted every time it is checked', () => {
  const results = [1, 2, 3, 4, 5].map(() => isGiftCardCode('GC-0042-7KQM'));
  assert.deepEqual(results, [true, true, true, true, true]);
  assert.equal(isGiftCardCode('GC-42-7KQM'), false);
});

it('[hidden] issue, balance and redeem all accept the same code', async () => {
  const app = await seededApp();
  const first = await app.giftCardService.issue(30);
  const second = await app.giftCardService.issue(20);
  assert.equal(await app.giftCardService.balance(first.code), 30);
  assert.equal(await app.giftCardService.balance(second.code), 20);
  assert.equal(await app.giftCardService.redeem(second.code, 5), 15);
  assert.equal(await app.giftCardService.balance(second.code), 15);
  assert.equal(await app.giftCardService.redeem(first.code, 10), 20);
});

it('[hidden] lower-case input is normalised and accepted', async () => {
  const app = await seededApp();
  const card = await app.giftCardService.issue(12);
  assert.equal(await app.giftCardService.balance(card.code.toLowerCase()), 12);
  assert.equal(await app.giftCardService.balance(` ${card.code} `), 12);
});
