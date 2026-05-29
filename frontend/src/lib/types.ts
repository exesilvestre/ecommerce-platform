export type Product = {
    id: number;
    name: string;
    description: string | null;
    price: string;
  };
  
  export type CartItem = {
    product: Product;
    quantity: number;
  };
  
  export type PaymentInput = {
    credit_card_number: string;
    credit_card_expiration_date: string;
  };
  
  export type OrderCreateRequest = {
    customer_id: number;
    shipping_address: string;
    items: { product_id: number; quantity: number }[];
    payment: PaymentInput;
  };
  
  export type OrderCreateResponse = {
    order_id: number;
    warehouse_id: number;
    total_amount: string;
    status: string;
    payment_status: string;
  };
  
  export type ApiResult<T = unknown> = {
    status: number;
    data: T;
    idempotencyKey: string;
  };