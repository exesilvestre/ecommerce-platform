import type { Product } from "@/lib/types";

export type ProductCardProps = {
  product: Product;
  onAdd: (product: Product) => void;
};