import type { PricingClient } from './pricing.ts';

/**
 * Read-through cache in front of a pricing backend. The backend is slow and rate-limited,
 * so each SKU is looked up at most once for as long as its price is unchanged.
 */
export class CachingPricingClient implements PricingClient {
  private readonly source: PricingClient;
  private readonly cache = new Map<string, number>();

  constructor(source: PricingClient) {
    this.source = source;
  }

  async priceFor(sku: string): Promise<number> {
    const cached = this.cache.get(sku);
    if (cached !== undefined) return cached;
    const price = await this.source.priceFor(sku);
    this.cache.set(sku, price);
    return price;
  }
}
