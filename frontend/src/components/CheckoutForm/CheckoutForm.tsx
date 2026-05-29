import type { CheckoutFormProps } from "./types";
import "./CheckoutForm.css";

export default function CheckoutForm({
  values,
  idempotencyKey,
  reuseKey,
  loading,
  disabled,
  onChange,
  onReuseKeyChange,
  onNewKey,
  onSubmit,
}: CheckoutFormProps) {
  return (
    <form
      className="checkout-form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <div className="checkout-form__title">Checkout</div>

      <div className="checkout-form__field">
        <label className="checkout-form__label" htmlFor="customer-id">
          customer_id
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
          shipping_address
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
          credit_card_number
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
      </div>

      <div className="checkout-form__field">
        <label className="checkout-form__label" htmlFor="card-expiry">
          expiration (MMYY)
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

      <div className="checkout-form__idempotency">
        <span className="checkout-form__label">Idempotency-Key</span>
        <span className="checkout-form__key">{idempotencyKey}</span>
        <div className="checkout-form__idempotency-actions">
          <label className="checkout-form__checkbox-label">
            <input
              type="checkbox"
              checked={reuseKey}
              onChange={(e) => onReuseKeyChange(e.target.checked)}
            />
            reuse key on submit
          </label>
          <button type="button" className="checkout-form__link" onClick={onNewKey}>
            new key
          </button>
        </div>
      </div>

      <button
        type="submit"
        className="checkout-form__submit"
        disabled={disabled || loading}
      >
        {loading ? "submitting..." : "submit order"}
      </button>
    </form>
  );
}