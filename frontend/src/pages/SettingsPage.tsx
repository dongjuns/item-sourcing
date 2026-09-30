import { useState, type FormEvent } from "react";
import { request, type Settings } from "../api/client";
import { readPricing } from "../api/pricing";

export function SettingsPage({
  settings,
  onChange,
}: {
  settings: Settings;
  onChange: (settings: Settings) => void;
}) {
  const [daily, setDaily] = useState(
    String(settings.values.daily_ai_limit ?? ""),
  );
  const [monthly, setMonthly] = useState(
    String(settings.values.monthly_ai_limit ?? ""),
  );
  const [tone, setTone] = useState(String(settings.values.default_tone ?? ""));
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [textLimit, setTextLimit] = useState(
    readPricing(settings, "text").call_limit_krw,
  );
  const [imageLimit, setImageLimit] = useState(
    readPricing(settings, "image").call_limit_krw,
  );
  const [pricingUrl, setPricingUrl] = useState(
    readPricing(settings, "text").source_url || "",
  );
  const [verifiedAt, setVerifiedAt] = useState(
    readPricing(settings, "text").verified_at || "",
  );
  async function save(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const updated = await request<Settings>("/settings", {
        method: "PATCH",
        body: JSON.stringify({
          values: {
            daily_ai_limit: daily || null,
            monthly_ai_limit: monthly || null,
            default_tone: tone,
            ...(textLimit || imageLimit
              ? {
                  ai_pricing: {
                    text: {
                      model: settings.status.ai_text_model,
                      call_limit_krw: textLimit,
                      source_url: pricingUrl,
                      verified_at: verifiedAt,
                    },
                    image: {
                      model: settings.status.ai_image_model,
                      call_limit_krw: imageLimit,
                      source_url: pricingUrl,
                      verified_at: verifiedAt,
                    },
                  },
                }
              : {}),
          },
        }),
      });
      onChange(updated);
      setMessage("설정을 저장했습니다.");
    } catch (reason) {
      setMessage((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section>
      <div className="page-heading">
        <div>
          <div className="eyebrow">SETTINGS</div>
          <h1>설정</h1>
        </div>
      </div>
      <div className="panel">
        <h2>연동 상태</h2>
        <p>
          도매꾹 키:{" "}
          {settings.status.domeggook_key_configured ? "설정됨" : "미설정"} ·
          수집 모드:{" "}
          {settings.status.source_mode === "live" ? "실조회" : "연습"}
        </p>
        <p>
          개발용 AI 키:{" "}
          {settings.status.ai_key_configured ? "설정됨" : "미설정"} · 생성 모드:{" "}
          {settings.status.ai_mode === "live" ? "실생성" : "연습"}
        </p>
        <p>
          계정을 교체할 때는 서버 환경설정의 키만 바꿉니다. 기존 키 값은
          화면에서 조회하지 않습니다.
        </p>
      </div>
      <form className="panel" onSubmit={save}>
        <p>
          텍스트 모델: {settings.status.ai_text_model || "미설정"} · 이미지
          모델: {settings.status.ai_image_model || "미설정"}
        </p>
        <div className="form-grid">
          <label>
            텍스트 호출 1회 예약 상한 원
            <input
              type="number"
              min="1"
              value={textLimit}
              onChange={(event) => setTextLimit(event.target.value)}
            />
          </label>
          <label>
            썸네일 3장 호출 1회 예약 상한 원
            <input
              type="number"
              min="1"
              value={imageLimit}
              onChange={(event) => setImageLimit(event.target.value)}
            />
          </label>
          <label>
            가격 확인 근거 URL
            <input
              type="url"
              value={pricingUrl}
              onChange={(event) => setPricingUrl(event.target.value)}
            />
          </label>
          <label>
            가격 확인일
            <input
              type="date"
              value={verifiedAt}
              onChange={(event) => setVerifiedAt(event.target.value)}
            />
          </label>
        </div>
        <h2>생성 비용과 기본 톤</h2>
        <div className="form-grid">
          <label>
            일일 AI 비용 한도 원
            <input
              type="number"
              min="0"
              value={daily}
              onChange={(event) => setDaily(event.target.value)}
            />
          </label>
          <label>
            월간 AI 비용 한도 원
            <input
              type="number"
              min="0"
              value={monthly}
              onChange={(event) => setMonthly(event.target.value)}
            />
          </label>
        </div>
        <label>
          기본 톤
          <input
            value={tone}
            onChange={(event) => setTone(event.target.value)}
            maxLength={200}
          />
        </label>
        <button disabled={busy}>설정 저장</button>
        {message && (
          <p role="status" className="notice">
            {message}
          </p>
        )}
        <p className="muted">
          실제 생성에는 키·모델·가격 확인 근거가 있는 호출별 예약 상한도
          필요합니다. 유료 호출은 미설정 상태에서 차단됩니다.
        </p>
      </form>
      <div className="panel">
        <h2>판매 채널 등록</h2>
        <p>
          현재 목표는 검토·확정까지입니다. 등록 기능은 후속 단계에서 연결합니다.
        </p>
      </div>
    </section>
  );
}
