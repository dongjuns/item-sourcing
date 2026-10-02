import type { Settings } from "./client";

function object(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

export function readPricing(settings: Settings, kind: "text" | "image") {
  const row = object(object(settings.values.ai_pricing)[kind]);
  return {
    model: typeof row.model === "string" ? row.model : "",
    call_limit_krw:
      row.call_limit_krw == null ? "" : String(row.call_limit_krw),
    source_url: typeof row.source_url === "string" ? row.source_url : "",
    verified_at: typeof row.verified_at === "string" ? row.verified_at : "",
  };
}

export function generationReservation(
  settings: Settings,
  channels: number,
): number | null {
  if (settings.status.ai_mode === "mock") return 0;
  const text = readPricing(settings, "text");
  const image = readPricing(settings, "image");
  const textCost = Number(text.call_limit_krw);
  const imageCost = Number(image.call_limit_krw);
  if (
    !text.call_limit_krw ||
    !image.call_limit_krw ||
    !Number.isFinite(textCost) ||
    !Number.isFinite(imageCost) ||
    textCost <= 0 ||
    imageCost <= 0 ||
    text.model !== settings.status.ai_text_model ||
    image.model !== settings.status.ai_image_model
  )
    return null;
  return textCost * channels + imageCost;
}
