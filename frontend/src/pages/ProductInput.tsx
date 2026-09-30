import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { post, waitJob, type Settings } from '../api/client';
import { statusLabel } from '../api/display';

export function ProductInput({ settings }: { settings: Settings }) {
  const [url, setUrl] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setMessage('수집 요청 중');
    try {
      const accepted = await post<{ job_id: string }>('/products/from-url', { url });
      const job = await waitJob(accepted.job_id, (value) => setMessage(`상품 수집 ${statusLabel(value.status)}`));
      if (typeof job.result.product_id === 'string') navigate(`/products/${job.result.product_id}`);
      else setMessage('수집에 실패했습니다. URL·키·계정 권한과 원본 사이트를 확인하세요.');
    } catch (reason) { setMessage((reason as Error).message); }
    finally { setBusy(false); }
  }
  const mock = settings.status.source_mode === 'mock';
  return <section><div className="page-heading"><div><div className="eyebrow">01 COLLECT</div><h1>상품 URL 입력</h1></div><span className="badge">{mock ? '연습 수집' : '도매꾹 조회'}</span></div>
    <div className="panel"><h2>도매꾹 상품 상세페이지에서 가져오기</h2>
      <p>상품명·가격·옵션·배송 정보와 이미지를 수집합니다. 도매꾹에는 상품을 등록하지 않습니다.</p>
      <form onSubmit={submit}><label>상품 상세페이지 URL<input type="url" placeholder={mock ? 'https://example.test/product/demo' : 'https://www.domeggook.com/상품번호'} value={url} onChange={(event) => setUrl(event.target.value)} required disabled={busy} /></label>
        <button disabled={busy}>{busy ? '수집 중' : '상품 정보 수집'}</button></form>
      {mock && <button className="secondary" onClick={() => setUrl('https://example.test/product/demo')}>연습 URL 채우기</button>}
      {message && <p role="status" className="notice">{message}</p>}
    </div><div className="workflow"><span>URL 입력</span><span>정보·이미지 수집</span><span>AI 생성</span><span>검토·확정</span></div>
  </section>;
}
