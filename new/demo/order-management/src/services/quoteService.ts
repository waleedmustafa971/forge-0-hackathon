import type { Fees } from '../config/fees.ts';
import { ValidationError } from '../domain/types.ts';
import type { PricingClient } from '../gateways/pricing.ts';
import { computeTotal, type NewOrderItem } from './orderService.ts';

export interface QuoteOptions {
  giftWrap?: boolean;
}

export interface Quote {
  merchandise: number;
  handling: number;
  giftWrap: number;
  total: number;
}

/** Prices a prospective order, including the operational fees, before anything is reserved. */
export class QuoteService {
  private readonly pricing: PricingClient;
  private readonly fees: Fees;

  constructor(pricing: PricingClient, fees: Fees) {
    this.pricing = pricing;
    this.fees = fees;
  }

  async quote(items: NewOrderItem[], options: QuoteOptions = {}): Promise<Quote> {
    if (items.length === 0) throw new ValidationError('A quote needs at least one item');
    const priced = [];
    for (const item of items) {
      priced.push({ ...item, unitPrice: await this.pricing.priceFor(item.sku) });
    }
    const merchandise = computeTotal(priced);
    const handling = merchandise >= this.fees.freeHandlingThreshold ? 0 : this.fees.handlingFee;
    const giftWrap = options.giftWrap ? this.fees.giftWrapFee : 0;
    const total = Math.round((merchandise + handling + giftWrap) * 100) / 100;
    return { merchandise, handling, giftWrap, total };
  }
}
