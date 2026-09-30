import { useState } from 'react';
import { BrowserRouter, NavLink, Navigate, Route, Routes } from 'react-router-dom';
import { clearCredentials, type Settings } from './api/client';
import { Login } from './pages/Login';
import { ProductDetail } from './pages/ProductDetail';
import { ProductInput } from './pages/ProductInput';
import { ProductList } from './pages/ProductList';
import { Review } from './pages/Review';
import { SettingsPage } from './pages/SettingsPage';

export default function App() {
  const [settings, setSettings] = useState<Settings | null>(null);
  if (!settings) return <Login onLogin={setSettings} />;
  return <BrowserRouter><div className="app-shell"><aside className="sidebar"><div className="brand">ITEM SOURCING<small>상품 수집부터 검토까지</small></div>
    <nav><NavLink to="/products" end>수집한 상품</NavLink><NavLink to="/products/new">상품 URL 입력</NavLink><NavLink to="/settings">설정</NavLink></nav>
    <div className="sidebar-footer"><span>검토·확정까지 구현</span><button className="secondary" onClick={() => { clearCredentials(); setSettings(null); }}>로그아웃</button></div></aside>
    <main className="main-content"><Routes><Route path="/products" element={<ProductList />} /><Route path="/products/new" element={<ProductInput settings={settings} />} /><Route path="/products/:id" element={<ProductDetail />} /><Route path="/products/:id/review" element={<Review settings={settings} />} /><Route path="/settings" element={<SettingsPage settings={settings} onChange={setSettings} />} /><Route path="*" element={<Navigate to="/products" replace />} /></Routes></main>
  </div></BrowserRouter>;
}
