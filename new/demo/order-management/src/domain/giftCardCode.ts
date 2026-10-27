/** Gift card codes look like GC-0001-7KQM: a prefix, a serial and a four-character check group. */
const GIFT_CARD_CODE = /^GC-[0-9]{4}-[0-9A-Z]{4}$/g;

export function normalizeGiftCardCode(code: string): string {
  return code.trim().toUpperCase();
}

export function isGiftCardCode(code: string): boolean {
  return GIFT_CARD_CODE.test(normalizeGiftCardCode(code));
}
