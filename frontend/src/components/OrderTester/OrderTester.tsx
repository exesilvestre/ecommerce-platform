"use client";

import { useEffect, useState } from "react";
import AppHeader from "@/components/AppHeader";
import ProductGrid from "@/components/ProductGrid";
import CartPanel from "@/components/CartPanel";
import CheckoutForm from "@/components/CheckoutForm";
import ResponsePanel from "@/components/ResponsePanel";
import type { CheckoutFormValues } from "@/components/CheckoutForm";
import { checkHealth, createOrder } from "@/lib/api";
import type { ApiResult, CartItem, Product } from "@/lib/types";
import "./OrderTester.css";

const defaultCheckout: CheckoutFormValues = {
  customerId: 1,
  shippingAddress: "123 Main St, Austin, TX 78701, USA",
  payment: {
    credit_card_number: "4111111111111111",
    credit_card_expiration_date: "1228",
  },
};

export default function OrderTester() {
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [checkout, setCheckout] = useState(defaultCheckout);
  const [idempotencyKey, setIdempotencyKey] = useState(() =>
    crypto.randomUUID(),
  );
  const [reuseKey, setReuseKey] = useState(false);
  const [result, setResult] = useState<ApiResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkHealth().then(setHealthy);
  }, []);

  function addToCart(product: Product) {
    setCart((prev) => {
      const existing = prev.find((i) => i.product.id === product.id);
      if (existing) {
        return prev.map((i) =>
          i.product.id === product.id
            ? { ...i, quantity: i.quantity + 1 }
            : i,
        );
      }
      return [...prev, { product, quantity: 1 }];
    });
  }

  function removeFromCart(productId: number) {
    setCart((prev) => prev.filter((i) => i.product.id !== productId));
  }

  function changeQuantity(productId: number, quantity: number) {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart((prev) =>
      prev.map((i) =>
        i.product.id === productId ? { ...i, quantity } : i,
      ),
    );
  }

  async function handleSubmit() {
    setLoading(true);

    const key = reuseKey ? idempotencyKey : crypto.randomUUID();
    if (!reuseKey) setIdempotencyKey(key);

    const body = {
      customer_id: checkout.customerId,
      shipping_address: checkout.shippingAddress,
      items: cart.map((i) => ({
        product_id: i.product.id,
        quantity: i.quantity,
      })),
      payment: checkout.payment,
    };

    const response = await createOrder(body, key);
    setResult(response);
    setLoading(false);
  }

  return (
    <div className="order-tester">
      <AppHeader healthy={healthy} />
      <div className="order-tester__panels">
        <div className="order-tester__column">
          <ProductGrid onAdd={addToCart} />
        </div>
        <div className="order-tester__column">
          <CartPanel
            items={cart}
            onRemove={removeFromCart}
            onQuantityChange={changeQuantity}
            onClear={() => setCart([])}
          />
        </div>
        <div className="order-tester__column order-tester__column--checkout">
          <CheckoutForm
            values={checkout}
            idempotencyKey={idempotencyKey}
            reuseKey={reuseKey}
            loading={loading}
            disabled={cart.length === 0}
            onChange={setCheckout}
            onReuseKeyChange={setReuseKey}
            onNewKey={() => setIdempotencyKey(crypto.randomUUID())}
            onSubmit={handleSubmit}
          />
          <ResponsePanel result={result} loading={loading} />
        </div>
      </div>
    </div>
  );
}
