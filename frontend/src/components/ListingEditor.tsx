import { useState } from "react";
import { post, request, type Listing, type ListingPatch } from "../api/client";
import { statusLabel } from "../api/display";
import { AssetImage } from "./AssetImage";
import { DetailPreview } from "./DetailPreview";

export function ListingEditor({
  listing,
  onChange,
  disabled,
}: {
  listing: Listing;
  onChange: (value: Listing) => void;
  disabled: boolean;
}) {
  const [title, setTitle] = useState(listing.title || "");
  const [html, setHtml] = useState(listing.detail_html || "");
  const [price, setPrice] = useState(String(listing.sale_price ?? ""));
  const [thumbnail, setThumbnail] = useState(
    listing.selected_thumbnail_id || "",
  );
  const [category, setCategory] = useState(listing.category_code || "");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const dirty =
    title !== (listing.title || "") ||
    html !== (listing.detail_html || "") ||
    price !== String(listing.sale_price ?? "") ||
    thumbnail !== (listing.selected_thumbnail_id || "") ||
    category !== (listing.category_code || "");
  async function save() {
    setBusy(true);
    setError("");
    const body: ListingPatch = {
      expected_version: listing.content_version,
      title,
      detail_html: html,
      sale_price: price ? Number(price) : null,
      selected_thumbnail_id: thumbnail || null,
      category_code: category || null,
    };
    try {
      onChange(
        await request<Listing>(`/listings/${listing.id}`, {
          method: "PATCH",
          body: JSON.stringify(body),
        }),
      );
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function confirm() {
    setBusy(true);
    setError("");
    try {
      onChange(
        await post<Listing>(`/listings/${listing.id}/confirm`, {
          expected_version: listing.content_version,
        }),
      );
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const blocked = disabled || busy || listing.status === "registered";
  return (
    <div className="panel">
      <div className="actions">
        <h2>
          {listing.channel === "coupang" ? "쿠팡" : "스마트스토어"} 콘텐츠
        </h2>
        <span className="badge">
          {statusLabel(listing.status)} · 버전 {listing.content_version}
        </span>
        <span className="badge">{statusLabel(listing.content_mode)}</span>
      </div>
      <div className="editor-grid">
        <div>
          <label>
            상품 제목
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              disabled={blocked}
            />
          </label>
          <div className="form-grid">
            <label>
              판매가
              <input
                type="number"
                min="0"
                value={price}
                onChange={(event) => setPrice(event.target.value)}
                disabled={blocked}
              />
            </label>
            <label>
              카테고리 코드
              <input
                value={category}
                onChange={(event) => setCategory(event.target.value)}
                disabled={blocked}
              />
            </label>
          </div>
          <label>
            상세페이지 HTML
            <textarea
              rows={14}
              value={html}
              onChange={(event) => setHtml(event.target.value)}
              disabled={blocked}
            />
          </label>
          <small>
            미리보기는 저장된 콘텐츠를 표시합니다. 수정·저장하면 재확정이
            필요합니다.
          </small>
          <h3>썸네일 선택</h3>
          <div className="image-grid">
            {listing.thumbnail_ids.map((id) => (
              <button
                type="button"
                key={id}
                aria-label={`썸네일 ${listing.thumbnail_ids.indexOf(id) + 1} 선택`}
                aria-pressed={thumbnail === id}
                className={`image-choice ${thumbnail === id ? "selected" : ""}`}
                onClick={() => setThumbnail(id)}
                disabled={blocked}
              >
                <AssetImage id={id} alt="썸네일 후보" />
              </button>
            ))}
          </div>
          <div className="actions">
            <button onClick={save} disabled={blocked || !dirty}>
              수정 저장
            </button>
            <button
              className="secondary"
              onClick={confirm}
              disabled={blocked || dirty || listing.status === "confirmed"}
            >
              검토 확정
            </button>
          </div>
          {dirty && (
            <p className="notice">
              저장하지 않은 수정이 있습니다. 저장 후 확정하세요.
            </p>
          )}
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
        </div>
        <div>
          <h3>저장된 상세페이지</h3>
          <DetailPreview html={listing.detail_html || ""} />
        </div>
      </div>
      {listing.status === "confirmed" && (
        <p className="success">
          검토 확정 완료. 판매 채널 등록은 후속 단계입니다.
        </p>
      )}
    </div>
  );
}
