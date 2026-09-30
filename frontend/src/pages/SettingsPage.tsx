import { useState, type FormEvent } from "react";
import { request, type Settings } from "../api/client";

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
