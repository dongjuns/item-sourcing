import { describe, expect, it } from "vitest";
import type { Settings } from "./client";
import { generationReservation, readPricing } from "./pricing";

function settings(): Settings {
  return {
    status: {
      ai_mode: "live",
      source_mode: "live",
      ai_key_configured: true,
      domeggook_key_configured: true,
      sources: ["domeggook"],
      ai_text_model: "text-model",
      ai_image_model: "image-model",
      registration_enabled: false,
    },
    values: {
      ai_pricing: {
        text: { model: "text-model", call_limit_krw: "100" },
        image: { model: "image-model", call_limit_krw: "500" },
      },
    },
  };
}

describe("유료 생성 예약 비용", () => {
  it("채널별 텍스트와 공통 썸네일 3장 호출을 합산한다", () => {
    const value = settings();
    expect(generationReservation(value, 2)).toBe(700);
    expect(generationReservation(value, 1)).toBe(600);
  });
  it("미설정 비용과 변경된 모델을 무료로 표시하지 않는다", () => {
    const value = settings();
    value.values.ai_pricing = null;
    expect(generationReservation(value, 2)).toBeNull();
    value.values.ai_pricing = [];
    expect(readPricing(value, "text").call_limit_krw).toBe("");
    const changed = settings();
    changed.status.ai_text_model = "other-model";
    expect(generationReservation(changed, 2)).toBeNull();
  });
  it("연습 호출만 비용 0으로 표시한다", () => {
    const value = settings();
    value.status.ai_mode = "mock";
    value.values.ai_pricing = null;
    expect(generationReservation(value, 2)).toBe(0);
  });
});
