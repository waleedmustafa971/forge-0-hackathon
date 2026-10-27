import type { InMemoryDatabase } from '../db/database.ts';
import { isGiftCardCode, normalizeGiftCardCode } from '../domain/giftCardCode.ts';
import { InvalidGiftCardError, NotFoundError, ValidationError, type GiftCard } from '../domain/types.ts';

const TABLE = 'gift_cards';
const CHECK_ALPHABET = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

function checkGroup(serial: number): string {
  let value = (serial * 2654435761) >>> 0;
  let group = '';
  for (let i = 0; i < 4; i++) {
    group += CHECK_ALPHABET[value % CHECK_ALPHABET.length];
    value = Math.floor(value / CHECK_ALPHABET.length);
  }
  return group;
}

export class GiftCardService {
  private readonly db: InMemoryDatabase;
  private serial = 0;

  constructor(db: InMemoryDatabase) {
    this.db = db;
  }

  /** Issues a new gift card with `amount` of balance. */
  async issue(amount: number): Promise<GiftCard> {
    if (!Number.isFinite(amount) || amount <= 0) throw new ValidationError(`Invalid gift card amount: ${amount}`);
    this.serial += 1;
    const code = `GC-${String(this.serial).padStart(4, '0')}-${checkGroup(this.serial)}`;
    if (!isGiftCardCode(code)) throw new Error(`Generated an invalid gift card code: ${code}`);
    const card: GiftCard = { code, balance: amount };
    await this.db.put(TABLE, code, { ...card });
    return card;
  }

  async balance(code: string): Promise<number> {
    return (await this.find(code)).balance;
  }

  /** Spends `amount` from the card and returns the remaining balance. */
  async redeem(code: string, amount: number): Promise<number> {
    const card = await this.find(code);
    if (!(amount > 0) || amount > card.balance) {
      throw new ValidationError(`Cannot redeem ${amount} from a balance of ${card.balance}`);
    }
    card.balance = Math.round((card.balance - amount) * 100) / 100;
    await this.db.put(TABLE, card.code, { ...card });
    return card.balance;
  }

  private async find(code: string): Promise<GiftCard> {
    if (!isGiftCardCode(code)) throw new InvalidGiftCardError(`Malformed gift card code: ${code}`);
    const card = await this.db.get<GiftCard>(TABLE, normalizeGiftCardCode(code));
    if (!card) throw new NotFoundError(`Gift card ${code} not found`);
    return card;
  }
}
