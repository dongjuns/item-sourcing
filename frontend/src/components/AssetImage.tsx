import { useEffect, useState } from 'react';
import { assetBlob } from '../api/client';

export function AssetImage({ id, alt }: { id: string; alt: string }) {
  const [url, setUrl] = useState('');
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let disposed = false;
    let ownedUrl = '';
    assetBlob(id).then((value) => {
      if (disposed) { URL.revokeObjectURL(value); return; }
      ownedUrl = value;
      setUrl(value);
    }).catch(() => { if (!disposed) setFailed(true); });
    return () => { disposed = true; if (ownedUrl) URL.revokeObjectURL(ownedUrl); };
  }, [id]);
  if (failed) return <div className="image-placeholder">이미지 조회 실패</div>;
  return url ? <img className="asset-image" src={url} alt={alt} /> : <div className="image-placeholder">불러오는 중</div>;
}
