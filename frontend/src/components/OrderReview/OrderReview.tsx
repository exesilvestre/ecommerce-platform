import { cartTotal, formatPrice, maskCardNumber } from "@/lib/format";
import type { OrderReviewProps } from "./types";
import "./OrderReview.css";

export default function OrderReview({
  items,
  checkout,
  loading,
  onBack,
  onConfirm,
}: OrderReviewProps) {
  const total = cartTotal(items);

  return (
    <section className="order-review">
      <div className="order-review__title">Review your order</div>

      <div className="order-review__section">
        <div className="order-review__label">Items</div>
        <ul className="order-review__list">
          {items.map(({ product, quantity }) => (
            <li key={product.id} className="order-review__row">
              <span>
                {product.name} × {quantity}
              </span>
              <span>{formatPrice(parseFloat(product.price) * quantity)}</span>
            </li>
          ))}
        </ul>
        <div className="order-review__total">
          <span>Total</span>
          <span>{formatPrice(total)}</span>
        </div>
      </div>

      <div className="order-review__section">
        <div className="order-review__label">Shipping</div>
        <p className="order-review__text">{checkout.shippingAddress}</p>
      </div>

      <div className="order-review__section">
        <div className="order-review__label">Payment</div>
        <p className="order-review__text">
          {maskCardNumber(checkout.payment.credit_card_number)}
        </p>
      </div>

      <div className="order-review__actions">
        <button
          type="button"
          className="order-review__back"
          onClick={onBack}
          disabled={loading}
        >
          Back
        </button>
        <button
          type="button"
          className="order-review__confirm"
          onClick={onConfirm}
          disabled={loading}
        >
          {loading ? "Placing order..." : "Confirm purchase"}
        </button>
      </div>
    </section>
  );
}
