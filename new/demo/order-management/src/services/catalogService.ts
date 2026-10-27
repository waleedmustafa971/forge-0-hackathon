import { ValidationError } from '../domain/types.ts';
import type { PriceBook } from '../gateways/priceBook.ts';
import type { PricingClient } from '../gateways/pricing.ts';

export class CatalogService {
  private readonly priceBook: PriceBook;
  private readonly pricing: PricingClient;

  constructor(priceBook: PriceBook, pricing: PricingClient) {
    this.priceBook = priceBook;
    this.pricing = pricing;
  }

  /** Changes the list price of `sku`; every later quote uses the new price. */
  async updatePrice(sku: string, price: number): Promise<void> {
    if (!Number.isFinite(price) || price <= 0) throw new ValidationError(`Invalid price for ${sku}: ${price}`);
    await this.priceBook.setPrice(sku, price);
  }

  /** Quotes the current list price of every SKU in `skus`. */
  async quote(skus: string[]): Promise<Record<string, number>> {
    const quote: Record<string, number> = {};
    for (const sku of skus) quote[sku] = await this.pricing.priceFor(sku);
    return quote;
  }
}
