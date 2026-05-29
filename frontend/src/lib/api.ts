import type { OrderCreateRequest, Users, OrderCreateResponse, Product } from "./types";

const BASE = "/api";

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function getProducts(): Promise<Product[]> {
  const res = await fetch(`${BASE}/products`);
  if (!res.ok) throw new Error(`Products failed (${res.status})`);
  return res.json();
}

export async function createOrder(
  body: OrderCreateRequest,
  idempotencyKey: string,
) {
  const res = await fetch(`${BASE}/orders`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json().catch(() => null);

  return {
    status: res.status,
    data,
    idempotencyKey,
  };
}