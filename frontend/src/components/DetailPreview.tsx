import { useEffect, useState } from "react";
import { assetBlob } from "../api/client";

export function DetailPreview({ html }: { html: string }) {
  const [preview, setPreview] = useState("");
  useEffect(() => {
    let disposed = false;
    const urls: string[] = [];
    const ids = [
      ...new Set(
        [...html.matchAll(/\/api\/assets\/([0-9a-f-]{36})/g)].map(
          (match) => match[1],
        ),
      ),
    ];
    Promise.all(
      ids.map(async (id) => {
        try {
          const url = await assetBlob(id);
          if (disposed) URL.revokeObjectURL(url);
          else urls.push(url);
          return [id, url] as const;
        } catch {
          return [id, ""] as const;
        }
      }),
    ).then((assets) => {
      if (disposed) return;
      let result = html;
      for (const [id, url] of assets)
        result = result.replaceAll(`/api/assets/${id}`, url);
      setPreview(
        `<style>body{font:15px sans-serif;line-height:1.8;padding:20px;color:#20334b}img{max-width:100%}h2{font-size:22px}</style>${result}`,
      );
    });
    return () => {
      disposed = true;
      urls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [html]);
  return (
    <iframe
      title="저장된 상세페이지 미리보기"
      sandbox=""
      className="detail-preview"
      srcDoc={preview}
    />
  );
}
