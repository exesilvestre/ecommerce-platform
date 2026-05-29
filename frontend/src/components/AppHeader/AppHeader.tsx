import type { AppHeaderProps } from "./types";
import "./AppHeader.css";
export default function AppHeader({ healthy }: AppHeaderProps) {
  const status =
    healthy === null ? "checking..." : healthy ? "api online" : "api offline";
  const statusClass =
    healthy === null
      ? ""
      : healthy
        ? "app-header__status--ok"
        : "app-header__status--down";
  return (
    <header className="app-header">
      <span className="app-header__title">Checkout</span>
      <span className={`app-header__status ${statusClass}`}>{status}</span>
    </header>
  );
}