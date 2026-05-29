import type { PaymentInput } from "@/lib/types";

export type CheckoutFormValues = {
  customerId: number;
  shippingAddress: string;
  payment: PaymentInput;
};

export type CheckoutFormProps = {
  values: CheckoutFormValues;
  loading: boolean;
  disabled: boolean;
  onChange: (values: CheckoutFormValues) => void;
  onReview: () => void;
};
