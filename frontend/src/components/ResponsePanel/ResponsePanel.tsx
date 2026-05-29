import type { ResponsePanelProps } from "./types";
import "./ResponsePanel.css";

function statusClass(status: number): string {
  if (status >= 200 && status < 300) return "response-panel__status--ok";
  if (status === 402) return "response-panel__status--warn";
  return "response-panel__status--error";
}

export default function ResponsePanel({ result, loading }: ResponsePanelProps) {
  return (
    <section className="response-panel">
      <div className="response-panel__title">Response</div>

      {loading && <p className="response-panel__empty">waiting...</p>}

      {!loading && !result && (
        <p className="response-panel__empty">submit an order to see response</p>
      )}

      {!loading && result && (
        <>
          <div className={`response-panel__status ${statusClass(result.status)}`}>
            HTTP {result.status}
          </div>
          <pre className="response-panel__body">
            {JSON.stringify(result.data, null, 2)}
          </pre>
        </>
      )}
    </section>
  );
}