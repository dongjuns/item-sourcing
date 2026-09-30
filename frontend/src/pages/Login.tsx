import { useState, type FormEvent } from "react";
import {
  clearCredentials,
  request,
  setCredentials,
  type Settings,
} from "../api/client";

export function Login({ onLogin }: { onLogin: (settings: Settings) => void }) {
  const [username, setUsername] = useState("owner");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setCredentials(username, password);
    try {
      onLogin(await request<Settings>("/settings"));
      setPassword("");
    } catch (reason) {
      clearCredentials();
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <div className="eyebrow">ITEM SOURCING</div>
        <h1>상품 소싱 검토</h1>
        <p>상품 URL에서 수집하고, 생성 콘텐츠를 검토하세요.</p>
        <label>
          사용자 이름
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
          />
        </label>
        <label>
          비밀번호
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <button disabled={busy}>{busy ? "확인 중" : "시작하기"}</button>
        <small>
          로컬 실행 비밀번호는 .env의 BASIC_AUTH_PASSWORD 설정을 사용합니다.
        </small>
      </form>
    </main>
  );
}
