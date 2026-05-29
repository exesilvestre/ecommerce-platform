"use client";

import { useEffect, useState } from "react";
import { getProducts } from "@/lib/api";
import type { Product } from "@/lib/types";
import ProductCard from "@/components/ProductCard";
import type { ProductGridProps } from "./types";
import "./ProductGrid.css";

export default function ProductGrid({ onAdd }: ProductGridProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((e) => setError(e instanceof Error ? e.message : "failed"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="product-grid">
      <div className="product-grid__title">Products</div>

      {loading && <p className="product-grid__state">loading...</p>}
      {error && <p className="product-grid__state product-grid__state--error">{error}</p>}
      {!loading && !error && products.length === 0 && (
        <p className="product-grid__state">no products</p>
      )}

      {!loading &&
        !error &&
        products.map((product) => (
          <ProductCard key={product.id} product={product} onAdd={onAdd} />
        ))}
    </section>
  );
}