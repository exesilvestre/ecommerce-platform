import type { ApiResult, OrderCreateResponse } from "@/lib/types";
import { formatPrice } from "@/lib/format";
import type { ResponsePanelProps } from "./types";
import "./ResponsePanel.css";

function isOrderResponse(data: unknown): data is OrderCreateResponse {
  return (
    typeof data === "object" &&
    data !== null &&
    "order_id" in data &&
    "warehouse_id" in data
  );
}

function errorMessage(data: unknown): string {
  if (typeof data === "object" && data !== null && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
  }
  return "Something went wrong. Please try again.";
}

export default function ResponsePanel({ result, loading }: ResponsePanelProps) {
  return (
    <section className="response-panel">
      <div className="response-panel__title">Order status</div>

      {loading && (
        <p className="response-panel__empty">Placing your order...</p>
      )}

      {!loading && !result && (
        <p className="response-panel__empty">
          Your order summary will appear here after checkout.
        </p>
      )}

      {!loading && result?.status === 201 && isOrderResponse(result.data) && (
        <div className="response-panel__success">
          <p className="response-panel__headline">Order confirmed</p>
          <dl className="response-panel__details">
            <div>
              <dt>Order</dt>
              <dd>#{result.data.order_id}</dd>
            </div>
            <div>
              <dt>Warehouse</dt>
              <dd>#{result.data.warehouse_id}</dd>
            </div>
            <div>
              <dt>Total</dt>
              <dd>{formatPrice(result.data.total_amount)}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{result.data.status}</dd>
            </div>
          </dl>
        </div>
      )}

      {!loading && result && result.status === 402 && (
        <div className="response-panel__error">
          <p className="response-panel__headline">Payment declined</p>
          <p className="response-panel__message">
            Payment could not be processed. Please try a different card.
          </p>
        </div>
      )}

      {!loading &&
        result &&
        result.status !== 201 &&
        result.status !== 402 && (
          <div className="response-panel__error">
            <p className="response-panel__headline">Order not placed</p>
            <p className="response-panel__message">{errorMessage(result.data)}</p>
          </div>
        )}
    </section>
  );
}
