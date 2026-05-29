import type { PaymentInput } from "@/lib/types";

export type CheckoutFormValues = {
  customerId: number;
  shippingAddress: string;
  payment: PaymentInput;
};

export type CheckoutFormProps = {
  values: CheckoutFormValues;
  idempotencyKey: string;
  reuseKey: boolean;
  loading: boolean;
  disabled: boolean;
  onChange: (values: CheckoutFormValues) => void;
  onReuseKeyChange: (reuse: boolean) => void;
  onNewKey: () => void;
  onSubmit: () => void;
};