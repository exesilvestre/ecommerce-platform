import type { ApiResult } from "@/lib/types";

export type ResponsePanelProps = {
  result: ApiResult | null;
  loading: boolean;
};