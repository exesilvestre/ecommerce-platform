import type { Product } from "@/lib/types";

export type ProductGridProps = {
  onAdd: (product: Product) => void;
};