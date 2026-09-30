import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { post, request, waitJob, type GenerateRequest, type Listing, type Product, type Settings } from '../api/client';
import { statusLabel } from '../api/display';
import { ListingEditor } from '../components/ListingEditor';

export function Review({ settings }: { settings: Settings }) {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [listings, setListings] = useState<Listing[]>([]);
  const [channels, setChannels] = useState<('coupang' | 'smartstore')[]>(['coupang', 'smartstore']);
  const [selected, setSelected] = useState('coupang');
  const [permission, setPermission] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  useEffect(() => {
    let active = true;
    Promise.all([request<Product>(`/products/${id}`), request<Listing[]>(`/products/${id}/listings`)])
      .then(([value, content]) => { if (active) { setProduct(value); setListings(content); } })
      .catch((reason) => { if (active) setMessage((reason as Error).message); });
    return () => { active = false; };
  }, [id]);
  async function generate(scope: GenerateRequest['scope']) {
    setBusy(true); setMessage("생성 요청 중");
    try {
      const body: GenerateRequest = { channels, scope, image_usage_confirmed: permission, expected_versions: Object.fromEntries(listings.map((listing) => [listing.channel, listing.content_version])) };
      const accepted = await post<{ job_id: string }>(`/products/${id}/generate`, body);
      const job = await waitJob(accepted.job_id, (value) => setMessage(`생성 ${statusLabel(value.status)}`));
      setListings(await request<Listing[]>(`/products/${id}/listings`));
      const errors = Array.isArray(job.result.errors) ? job.result.errors.join(' / ') : '';
      setMessage(errors || '콘텐츠가 준비됐습니다. 원본과 비교해 검토하세요.');
    } catch (reason) { setMessage((reason as Error).message); }
    finally { setBusy(false); }
  }
  function update(value: Listing) { setListings((current) => current.map((item) => item.id === value.id ? value : item)); }
  if (!product) return <p>{message || '상품 정보를 불러오는 중입니다.'}</p>;
  const current = listings.find((listing) => listing.channel === selected);
  return <section><div className="page-heading"><div><div className="eyebrow">03 GENERATE & REVIEW</div><h1>AI 생성·검토</h1><p>{product.name}</p></div><Link to={`/products/${id}`}>수집 원본 보기</Link></div>
    {settings.status.ai_mode === 'mock' && <p className="notice">연습 생성 모드입니다. 실제 AI 결과가 아닙니다. 개발용 키·모델·비용 설정 후 실생성 모드로 전환하세요.</p>}
    <div className="panel"><h2>생성할 콘텐츠</h2><div className="actions">{(['coupang', 'smartstore'] as const).map((channel) => <label className="checkbox" key={channel}><input type="checkbox" checked={channels.includes(channel)} disabled={busy} onChange={(event) => setChannels((current) => event.target.checked ? [...current, channel] : current.filter((item) => item !== channel))} />{channel === 'coupang' ? '쿠팡' : '스마트스토어'}</label>)}</div>
      {product.image_usage_allowed !== true && <label className="checkbox"><input type="checkbox" checked={permission} onChange={(event) => setPermission(event.target.checked)} disabled={product.image_usage_allowed === false || busy} />상품 이미지 사용 조건을 확인했습니다.</label>}
      <div className="actions"><button disabled={busy || channels.length === 0 || product.image_usage_allowed === false} onClick={() => generate('all')}>상세페이지·썸네일 생성</button><button className="secondary" disabled={busy || channels.length === 0} onClick={() => generate('text')}>텍스트 다시 생성</button><button className="secondary" disabled={busy || channels.length === 0 || product.image_usage_allowed === false} onClick={() => generate('thumbnails')}>썸네일 다시 생성</button></div>
      <p className="muted">생성 전 설정된 비용 상한을 검사합니다. 생성과 확정만으로 상품이 등록되지 않습니다.</p>{message && <p role="status" className="notice">{message}</p>}</div>
    <div className="tabs">{listings.map((listing) => <button className={selected === listing.channel ? 'active' : 'secondary'} key={listing.id} onClick={() => setSelected(listing.channel)}>{listing.channel === 'coupang' ? '쿠팡' : '스마트스토어'} · {statusLabel(listing.status)}</button>)}</div>
    {current && <ListingEditor key={`${current.id}-${current.content_version}-${current.status}`} listing={current} onChange={update} disabled={busy} />}
  </section>;
}
