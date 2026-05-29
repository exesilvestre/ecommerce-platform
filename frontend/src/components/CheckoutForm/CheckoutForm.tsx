import type { CheckoutFormProps } from "./types";
import "./CheckoutForm.css";

export default function CheckoutForm({
  values,
  loading,
  disabled,
  onChange,
  onReview,
}: CheckoutFormProps) {
  return (
    <form
      className="checkout-form"
      onSubmit={(e) => {
        e.preventDefault();
        onReview();
      }}
    >
      <div className="checkout-form__title">Checkout</div>

      <div className="checkout-form__field">
        <label className="checkout-form__label" htmlFor="customer-id">
          Customer
        </label>
        <input
          id="customer-id"
          className="checkout-form__input"
          type="number"
          value={values.customerId}
          onChange={(e) =>
            onChange({ ...values, customerId: Number(e.target.value) })
          }
        />
      </div>

      <div className="checkout-form__field">
        <label className="checkout-form__label" htmlFor="shipping-address">
          Shipping address
        </label>
        <input
          id="shipping-address"
          className="checkout-form__input"
          type="text"
          value={values.shippingAddress}
          onChange={(e) =>
            onChange({ ...values, shippingAddress: e.target.value })
          }
        />
      </div>

      <div className="checkout-form__field">
        <label className="checkout-form__label" htmlFor="card-number">
          Card number
        </label>
        <input
          id="card-number"
          className="checkout-form__input"
          type="text"
          maxLength={16}
          value={values.payment.credit_card_number}
          onChange={(e) =>
            onChange({
              ...values,
              payment: {
                ...values.payment,
                credit_card_number: e.target.value.replace(/\D/g, ""),
              },
            })
          }
        />
        <span className="checkout-form__hint">
          Cards ending in 0000 are declined (demo).
        </span>
      </div>

      <div className="checkout-form__field">
        <label className="checkout-form__label" htmlFor="card-expiry">
          Expiration (MM/YY)
        </label>
        <input
          id="card-expiry"
          className="checkout-form__input"
          type="text"
          maxLength={4}
          value={values.payment.credit_card_expiration_date}
          onChange={(e) =>
            onChange({
              ...values,
              payment: {
                ...values.payment,
                credit_card_expiration_date: e.target.value.replace(/\D/g, ""),
              },
            })
          }
        />
      </div>

      <button
        type="submit"
        className="checkout-form__submit"
        disabled={disabled || loading}
      >
        Review order
      </button>
    </form>
  );
}
