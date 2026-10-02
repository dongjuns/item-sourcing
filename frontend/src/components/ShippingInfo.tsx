import type { Product } from "../api/client";
import { money } from "../api/display";

export function ShippingInfo({ shipping }: { shipping: Product["shipping"] }) {
  const dispatch =
    shipping?.dispatch_days === 0
      ? "당일출고"
      : shipping?.dispatch_days != null
        ? `${shipping.dispatch_days}일 이내 출고`
        : "출고일 미확인";
  const fee =
    shipping?.payment_method === "무료배송"
      ? "무료배송"
      : shipping?.fee != null
        ? `배송비 ${money(shipping.fee)}원`
        : "배송비 미확인";
  const bundle =
    shipping?.bundle_shipping === "allowed"
      ? "묶음배송 가능 (동일 출고지 상품)"
      : shipping?.bundle_shipping === "not_allowed"
        ? "묶음배송 불가능"
        : shipping?.bundle_shipping === "conditional"
          ? shipping.bundle_threshold != null
            ? `묶음배송 ${money(shipping.bundle_threshold)}원 이상 구매시 가능 (동일 출고지 상품)`
            : "묶음배송 조건부 가능 · 조건 확인 필요"
          : "묶음배송 여부 미확인";
  return (
    <div>
      <h3>배송정보</h3>
      <p>
        {dispatch} · {shipping?.method || "배송 방식 미확인"} / {fee}
        {shipping?.payment_method &&
          shipping.payment_method !== "무료배송" &&
          ` · ${shipping.payment_method}`}
      </p>
      <p>{bundle}</p>
      {shipping?.jeju_fee != null && (
        <p>제주 추가배송비 {money(shipping.jeju_fee)}원</p>
      )}
      {shipping?.remote_area_fee != null && (
        <p>도서산간 추가배송비 {money(shipping.remote_area_fee)}원</p>
      )}
    </div>
  );
}
