import type { Order } from '../domain/types.ts';
import type { EventBus } from '../lib/events.ts';
import type { LoyaltyService } from './loyaltyService.ts';
import type { PaymentService } from './paymentService.ts';

export interface OrderPaid {
  orderId: string;
  customerId: string;
  amount: number;
}

export interface Receipt {
  orderId: string;
  customerId: string;
  amount: number;
}

/** Sends one receipt per paid order (an outbox in tests). */
export class ReceiptService {
  readonly sent: Receipt[] = [];

  async onPaid(event: OrderPaid): Promise<void> {
    this.sent.push({ orderId: event.orderId, customerId: event.customerId, amount: event.amount });
  }
}

/** Awards loyalty points when an order is paid. */
export class RewardsService {
  private readonly loyalty: LoyaltyService;

  constructor(loyalty: LoyaltyService) {
    this.loyalty = loyalty;
  }

  async onPaid(event: OrderPaid): Promise<void> {
    await this.loyalty.award(event.customerId, event.amount);
  }
}

/** Takes payment for an order and announces it to the rest of the system. */
export class CheckoutService {
  private readonly payments: PaymentService;
  private readonly bus: EventBus;
  private readonly rewards: RewardsService;
  private readonly receipts: ReceiptService;

  constructor(payments: PaymentService, bus: EventBus, rewards: RewardsService, receipts: ReceiptService) {
    this.payments = payments;
    this.bus = bus;
    this.rewards = rewards;
    this.receipts = receipts;
  }

  async complete(order: Order): Promise<void> {
    // Subscribers are wired lazily on the first checkout; onUnique makes the repeat calls harmless.
    this.bus.onUnique<OrderPaid>('order.paid', (event) => this.rewards.onPaid(event));
    this.bus.onUnique<OrderPaid>('order.paid', (event) => this.receipts.onPaid(event));
    await this.payments.capturePayment(order.id, order.total);
    await this.bus.emit<OrderPaid>('order.paid', {
      orderId: order.id,
      customerId: order.customerId,
      amount: order.total,
    });
  }
}
