import { ValidationError } from '../domain/types.ts';
import type { NewOrderItem } from './orderService.ts';

/** Catalogue product ids, as used by the storefront. */
export const PRODUCT_IDS: Record<string, number> = {
  'SKU-KEYBOARD': 3104,
  'SKU-MOUSE': 2207,
  'SKU-MONITOR': 518,
  'SKU-CABLE': 87,
};

export interface CartLine {
  productId: number;
  sku: string;
  quantity: number;
}

/** Shopping carts, one per customer. Lines keep the order in which products were first added. */
export class CartService {
  /** customerId -> productId -> line */
  private readonly carts = new Map<string, Record<number, CartLine>>();

  add(customerId: string, sku: string, quantity = 1): CartLine[] {
    const productId = PRODUCT_IDS[sku];
    if (productId === undefined) throw new ValidationError(`Unknown product ${sku}`);
    if (!Number.isInteger(quantity) || quantity <= 0) {
      throw new ValidationError(`Invalid quantity for ${sku}: ${quantity}`);
    }
    const cart = this.carts.get(customerId) ?? {};
    const line = cart[productId];
    if (line) line.quantity += quantity;
    else cart[productId] = { productId, sku, quantity };
    this.carts.set(customerId, cart);
    return this.lines(customerId);
  }

  remove(customerId: string, sku: string): CartLine[] {
    const cart = this.carts.get(customerId);
    if (cart) delete cart[PRODUCT_IDS[sku]];
    return this.lines(customerId);
  }

  /** The cart as the storefront shows it. */
  lines(customerId: string): CartLine[] {
    return Object.values(this.carts.get(customerId) ?? {}).map((line) => ({ ...line }));
  }

  /** Order items for checkout, in cart order (the order confirmation lists them that way). */
  toOrderItems(customerId: string): NewOrderItem[] {
    const cart = this.carts.get(customerId) ?? {};
    return Object.keys(cart).map((id) => ({ sku: cart[Number(id)].sku, quantity: cart[Number(id)].quantity }));
  }
}
