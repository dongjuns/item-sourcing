import { useCallback, useEffect, useState } from "react";
import {
  BrowserRouter,
  NavLink,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import { request, type Settings } from "./api/client";
import { ProductDetail } from "./pages/ProductDetail";
import { ProductInput } from "./pages/ProductInput";
import { ProductList } from "./pages/ProductList";
import { SettingsPage } from "./pages/SettingsPage";

export default function App() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [error, setError] = useState("");
  const loadSettings = useCallback(() => {
    setError("");
    request<Settings>("/settings")
      .then(setSettings)
      .catch((reason) => setError((reason as Error).message));
  }, []);
  useEffect(loadSettings, [loadSettings]);
  if (!settings)
    return (
      <main className="main-content">
        <p role="status">{error || "상품 화면을 준비하는 중입니다."}</p>
        {error && <button onClick={loadSettings}>연결 다시 확인</button>}
      </main>
    );
  return (
    <BrowserRouter>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            ITEM SOURCING<small>상품 URL에서 정보 수집</small>
          </div>
          <nav>
            <NavLink to="/products" end>
              수집한 상품
            </NavLink>
            <NavLink to="/products/new">상품 URL 입력</NavLink>
            <NavLink to="/settings">설정</NavLink>
          </nav>
          <div className="sidebar-footer">
            <span>상품 정보·사진 수집</span>
          </div>
        </aside>
        <main className="main-content">
          <Routes>
            <Route path="/products" element={<ProductList />} />
            <Route
              path="/products/new"
              element={<ProductInput settings={settings} />}
            />
            <Route path="/products/:id" element={<ProductDetail />} />
            <Route
              path="/settings"
              element={
                <SettingsPage settings={settings} onChange={setSettings} />
              }
            />
            <Route path="*" element={<Navigate to="/products" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
