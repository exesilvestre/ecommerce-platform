import type { CartPanelProps } from "./types";
import "./CartPanel.css";

export default function CartPanel({
  items,
  onRemove,
  onQuantityChange,
  onClear,
}: CartPanelProps) {
  return (
    <section className="cart-panel">
      <div className="cart-panel__header">
        <span className="cart-panel__title">Cart</span>
        {items.length > 0 && (
          <button type="button" className="cart-panel__clear" onClick={onClear}>
            clear
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <p className="cart-panel__empty">empty</p>
      ) : (
        items.map(({ product, quantity }) => (
          <div key={product.id} className="cart-panel__row">
            <span>{product.name}</span>
            <div className="cart-panel__qty">
              <button
                type="button"
                onClick={() => onQuantityChange(product.id, quantity - 1)}
              >
                −
              </button>
              <span>{quantity}</span>
              <button
                type="button"
                onClick={() => onQuantityChange(product.id, quantity + 1)}
              >
                +
              </button>
              <button
                type="button"
                className="cart-panel__remove"
                onClick={() => onRemove(product.id)}
              >
                ×
              </button>
            </div>
          </div>
        ))
      )}
    </section>
  );
}