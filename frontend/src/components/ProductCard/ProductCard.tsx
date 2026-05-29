import type { ProductCardProps } from "./types";
import "./ProductCard.css";

export default function ProductCard({ product, onAdd }: ProductCardProps) {
  return (
    <div className="product-card">
      <div className="product-card__info">
        <div className="product-card__name">{product.name}</div>
        <div className="product-card__price">${product.price}</div>
      </div>
      <button
        type="button"
        className="product-card__btn"
        onClick={() => onAdd(product)}
      >
        add
      </button>
    </div>
  );
}