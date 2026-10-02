import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { request, type Asset, type Product } from "../api/client";
import { money, statusLabel } from "../api/display";
import { AssetImage } from "../components/AssetImage";
import { ProductAmounts } from "../components/ProductAmounts";
import { ShippingInfo } from "../components/ShippingInfo";

export function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    Promise.all([
      request<Product>(`/products/${id}`),
      request<Asset[]>(`/products/${id}/assets`),
    ])
      .then(([value, images]) => {
        if (active) {
          setProduct(value);
          setAssets(images);
        }
      })
      .catch((reason) => {
        if (active) setError((reason as Error).message);
      });
    return () => {
      active = false;
    };
  }, [id]);
  if (error) return <p className="error">{error}</p>;
  if (!product) return <p>상품을 불러오는 중입니다.</p>;
  const reusable =
    product.image_usage_allowed === true
      ? "사용 허용"
      : product.image_usage_allowed === false
        ? "재사용 불가"
        : "사용 조건 확인 필요";
  return (
    <section>
      <div className="page-heading">
        <div>
          <div className="eyebrow">02 SOURCE DATA</div>
          <h1>{product.name || "수집 실패 상품"}</h1>
        </div>
        <button disabled>AI 생성 보류</button>
      </div>
      <div className="summary-grid">
        <div className="stat">
          <span>도매가</span>
          <strong>{money(product.wholesale_price)}</strong>
          <small>통화 {product.currency || "확인 필요"}</small>
        </div>
        <div className="stat">
          <span>재고</span>
          <strong>{product.stock_quantity ?? "미확인"}</strong>
        </div>
        <div className="stat">
          <span>최소 주문</span>
          <strong>{product.minimum_order_quantity ?? "미확인"}</strong>
        </div>
        <div className="stat">
          <span>수집 상태</span>
          <strong>{statusLabel(product.collection_status)}</strong>
        </div>
      </div>
      <ProductAmounts key={product.id} product={product} />
      <div className="panel">
        <div className="actions">
          <span className="badge">{statusLabel(product.acquisition_mode)}</span>
          <a href={product.source_url} target="_blank" rel="noreferrer">
            원본 상세페이지
          </a>
          <span>{new Date(product.fetched_at).toLocaleString("ko-KR")}</span>
        </div>
        <h2>대표·본문 사진</h2>
        <p>이미지 사용 조건: {reusable}</p>
        <div className="image-grid">
          {assets
            .filter((asset) => asset.kind === "source")
            .map((asset) => (
              <div key={asset.id}>
                {asset.status === "ready" ? (
                  <AssetImage id={asset.id} alt="수집한 상품 이미지" />
                ) : (
                  <p className="error">{asset.error}</p>
                )}
              </div>
            ))}
        </div>
        {assets.length === 0 && <p>저장된 이미지가 없습니다.</p>}
      </div>
      <div className="panel">
        <h2>옵션과 배송</h2>
        {product.options?.map((option, index) => (
          <p key={option.source_option_id || index}>
            {option.label || "이름 미확인"} · 재고{" "}
            {option.stock_quantity ?? "미확인"} · 단가{" "}
            {money(option.wholesale_price)}
          </p>
        ))}
        {!product.options && <p>옵션 정보 확인 필요</p>}
        <ShippingInfo shipping={product.shipping} />
      </div>
      {!!product.issues?.length && (
        <div className="panel notice">
          <h2>확인할 항목</h2>
          <ul>
            {product.issues.map((issue, index) => (
              <li key={index}>{issue.message}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="panel">
        <h2>상품 설명 텍스트</h2>
        <pre className="source-text">
          {product.detail_text ||
            "본문에 추출 가능한 텍스트가 없습니다. 이미지 안의 글자는 OCR이 필요합니다."}
        </pre>
        <details>
          <summary>본문 HTML 원문 보기</summary>
          <pre className="source-text">{product.detail_html || "미수집"}</pre>
        </details>
        <details>
          <summary>수집 응답 원본 보기</summary>
          <pre>{JSON.stringify(product.raw, null, 2)}</pre>
        </details>
      </div>
    </section>
  );
}
