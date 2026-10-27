export type Handler<T> = (payload: T) => void | Promise<void>;

/** Minimal in-process event bus. Handlers run in registration order and are awaited one by one. */
export class EventBus {
  private readonly handlers = new Map<string, Handler<unknown>[]>();

  on<T>(event: string, handler: Handler<T>): void {
    const list = this.handlers.get(event) ?? [];
    list.push(handler as Handler<unknown>);
    this.handlers.set(event, list);
  }

  /**
   * Registers `handler` unless it is already registered for `event`, so code that may run more
   * than once (lazy wiring, retries) can call it without registering duplicates.
   */
  onUnique<T>(event: string, handler: Handler<T>): void {
    if ((this.handlers.get(event) ?? []).includes(handler as Handler<unknown>)) return;
    this.on(event, handler);
  }

  async emit<T>(event: string, payload: T): Promise<void> {
    for (const handler of [...(this.handlers.get(event) ?? [])]) await handler(payload);
  }

  listenerCount(event: string): number {
    return this.handlers.get(event)?.length ?? 0;
  }
}
