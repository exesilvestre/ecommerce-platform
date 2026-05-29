export function formatPrice(amount: string | number): string {
  const value = typeof amount === "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

export function maskCardNumber(cardNumber: string): string {
  const lastFour = cardNumber.slice(-4);
  return lastFour ? `•••• ${lastFour}` : "••••";
}

export function cartTotal(items: { product: { price: string }; quantity: number }[]): number {
  return items.reduce(
    (sum, item) => sum + parseFloat(item.product.price) * item.quantity,
    0,
  );
}
