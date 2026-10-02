import { useEffect, useState } from "react";
import { request, type Product, type ProductQuote } from "../api/client";
import { money } from "../api/display";

export function ProductAmounts({ product }: { product: Product }) {
  const minimum = Math.max(product.minimum_order_quantity ?? 1, 1);
  const unit = product.purchase_unit ?? 1;
  const [quantity, setQuantity] = useState(Math.ceil(minimum / unit) * unit);
  const [option, setOption] = useState("");
  const [quote, setQuote] = useState<ProductQuote | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setQuote(null);
    setError("");
    if (!Number.isInteger(quantity) || quantity < 1) return;
    const params = new URLSearchParams({ quantity: String(quantity) });
    if (option) params.set("option_id", option);
    request<ProductQuote>(`/products/${product.id}/quote?${params}`)
      .then((value) => {
        if (active) setQuote(value);
      })
      .catch((reason) => {
        if (active) setError((reason as Error).message);
      });
    return () => {
      active = false;
    };
  }, [product.id, quantity, option]);
  return (
    <div className="panel">
      <h2>수량별 상품금액</h2>
      <div className="actions">
        <label>
          수량{" "}
          <input
            aria-label="수량"
            type="number"
            min={1}
            step={unit}
            value={quantity || ""}
            onChange={(event) => setQuantity(Number(event.target.value))}
          />
        </label>
        {!!product.options?.length && (
          <label>
            옵션{" "}
            <select
              value={option}
              onChange={(event) => setOption(event.target.value)}
            >
              <option value="">옵션을 선택하세요</option>
              {product.options.map((row) => (
                <option
                  key={row.source_option_id}
                  value={row.source_option_id || ""}
                >
                  {row.label || "옵션명 미확인"}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
      <p>
        최소 {minimum}개 · 구매 단위 {unit}개
        {product.maximum_order_quantity
          ? ` · 최대 ${product.maximum_order_quantity}개`
          : ""}
      </p>
      {(!Number.isInteger(quantity) || quantity < 1) && (
        <p className="error">수량은 1 이상의 정수로 입력하세요.</p>
      )}
      {error && <p className="error">{error}</p>}
      <div className="summary-grid">
        <div className="stat">
          <span>적용 단가</span>
          <strong>{money(quote?.unit_price)}</strong>
        </div>
        <div className="stat">
          <span>상품금액 ({quantity || 0}개)</span>
          <strong>{money(quote?.product_amount)}</strong>
        </div>
        <div className="stat">
          <span>기본 배송비</span>
          <strong>{money(quote?.shipping_fee)}</strong>
        </div>
        <div className="stat">
          <span>배송비 포함 금액</span>
          <strong>{money(quote?.total_amount)}</strong>
        </div>
      </div>
      {quote?.issues?.map((issue, index) => (
        <p key={index} className="muted">
          {issue.message}
        </p>
      ))}
    </div>
  );
}
