import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { request, type Product } from '../api/client';
import { money, statusLabel } from '../api/display';

export function ProductList() {
  const [products, setProducts] = useState<Product[]>([]);
  const [source, setSource] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    const params = new URLSearchParams({ page: String(page), source, status });
    request<Product[]>(`/products?${params}`).then((value) => { if (active) setProducts(value); })
      .catch((reason) => { if (active) setError((reason as Error).message); });
    return () => { active = false; };
  }, [source, status, page]);
  return <section><div className="page-heading"><div><div className="eyebrow">PRODUCTS</div><h1>수집한 상품</h1></div><Link className="button" to="/products/new">상품 수집</Link></div>
    <div className="filters"><label>소싱처<select value={source} onChange={(event) => { setSource(event.target.value); setPage(1); }}><option value="">전체</option><option value="domeggook">도매꾹</option><option value="mock">연습</option></select></label>
      <label>수집 상태<select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }}><option value="">전체</option><option value="complete">완료</option><option value="partial">일부 누락</option><option value="failed">실패</option></select></label></div>
    {error && <p className="error">{error}</p>}
    <div className="panel table-wrap"><table><thead><tr><th>상품명</th><th>소싱처</th><th>도매가</th><th>상태</th><th>수집 시각</th></tr></thead><tbody>
      {products.map((product) => <tr key={product.id}><td><Link to={`/products/${product.id}`}>{product.name || '수집 실패 상품'}</Link>{product.acquisition_mode === 'mock' && <span className="badge">연습</span>}</td><td>{product.source}</td><td>{money(product.wholesale_price)}</td><td>{statusLabel(product.collection_status)}</td><td>{new Date(product.fetched_at).toLocaleString('ko-KR')}</td></tr>)}
    </tbody></table>{products.length === 0 && <p className="empty">아직 수집한 상품이 없습니다.</p>}</div>
    <div className="actions"><button className="secondary" disabled={page === 1} onClick={() => setPage(page - 1)}>이전</button><span>{page} 페이지</span><button className="secondary" disabled={products.length < 20} onClick={() => setPage(page + 1)}>다음</button></div>
  </section>;
}
