import { tick } from '../lib/async.ts';
import type { PricingClient } from './pricing.ts';

/** Authoritative list prices, standing in for a slow, rate-limited pricing backend. */
export class PriceBook implements PricingClient {
  private readonly prices: Record<string, number>;
  /** Number of price lookups served, for monitoring the backend's rate limit. */
  lookups = 0;

  constructor(prices: Record<string, number>) {
    this.prices = { ...prices };
  }

  async priceFor(sku: string): Promise<number> {
    await tick(2);
    this.lookups++;
    const price = this.prices[sku];
    if (price === undefined) throw new Error(`No price for ${sku}`);
    return price;
  }

  async setPrice(sku: string, price: number): Promise<void> {
    await tick();
    this.prices[sku] = price;
  }
}
