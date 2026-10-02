import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ShippingInfo } from "./ShippingInfo";

describe("배송정보 표시", () => {
  it("무료배송과 3일 이내 출고 및 묶음배송 불가를 표시한다", () => {
    const html = renderToStaticMarkup(
      <ShippingInfo
        shipping={{
          method: "택배",
          dispatch_days: 3,
          payment_method: "무료배송",
          fee: "0",
          fee_calculation: "fixed",
          bundle_shipping: "not_allowed",
        }}
      />,
    );
    expect(html).toContain("3일 이내 출고");
    expect(html).toContain("택배 / 무료배송");
    expect(html).toContain("묶음배송 불가능");
    expect(html).not.toContain("미확인");
  });
  it("당일출고와 묶음배송 기준금액을 무료배송 조건으로 바꾸지 않는다", () => {
    const html = renderToStaticMarkup(
      <ShippingInfo
        shipping={{
          method: "택배",
          dispatch_days: 0,
          payment_method: "선결제",
          fee: "2750",
          fee_calculation: "fixed",
          bundle_shipping: "conditional",
          bundle_threshold: "300000",
        }}
      />,
    );
    expect(html).toContain("당일출고");
    expect(html).toContain("배송비 2,750원");
    expect(html).toContain("묶음배송 300,000원 이상 구매시 가능");
    expect(html).not.toContain("무료배송");
  });
  it("과거 저장 데이터에 없는 조건을 추정하지 않는다", () => {
    const html = renderToStaticMarkup(
      <ShippingInfo
        shipping={{ fee_calculation: "unknown", bundle_shipping: "unknown" }}
      />,
    );
    expect(html).toContain("출고일 미확인");
    expect(html).toContain("배송비 미확인");
    expect(html).toContain("묶음배송 여부 미확인");
  });
});
