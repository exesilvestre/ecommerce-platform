import type { CheckoutFormValues } from "@/components/CheckoutForm";
import type { CartItem } from "@/lib/types";

export type OrderReviewProps = {
  items: CartItem[];
  checkout: CheckoutFormValues;
  loading: boolean;
  onBack: () => void;
  onConfirm: () => void;
};
