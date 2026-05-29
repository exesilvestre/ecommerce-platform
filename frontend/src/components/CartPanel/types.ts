import type { CartItem } from "@/lib/types";

export type CartPanelProps = {
  items: CartItem[];
  onRemove: (productId: number) => void;
  onQuantityChange: (productId: number, quantity: number) => void;
  onClear: () => void;
};