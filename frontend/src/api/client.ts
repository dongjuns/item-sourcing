import type { components } from './schema';

export type Product = components['schemas']['ProductRead'];
export type Listing = components['schemas']['ListingRead'];
export type Asset = components['schemas']['AssetRead'];
export type Job = components['schemas']['JobRead'];
export type Settings = components['schemas']['SettingsRead'];
export type GenerateRequest = components['schemas']['GenerateRequest'];
export type ListingPatch = components['schemas']['ListingPatch'];

let authorization = '';

export function setCredentials(username: string, password: string) {
  const bytes = new TextEncoder().encode(`${username}:${password}`);
  authorization = `Basic ${btoa(String.fromCharCode(...bytes))}`;
}

export function clearCredentials() { authorization = ''; }

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', Authorization: authorization, ...init.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === 'string' ? body.detail : '요청을 처리할 수 없습니다.');
  }
  return response.json() as Promise<T>;
}

export async function assetBlob(id: string): Promise<string> {
  const response = await fetch(`/api/assets/${id}`, { headers: { Authorization: authorization } });
  if (!response.ok) throw new Error('이미지를 불러올 수 없습니다.');
  return URL.createObjectURL(await response.blob());
}

export async function waitJob(id: string, onUpdate?: (job: Job) => void): Promise<Job> {
  for (;;) {
    const job = await request<Job>(`/jobs/${id}`);
    onUpdate?.(job);
    if (!['queued', 'running'].includes(job.status)) return job;
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
}

export function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: 'POST', body: JSON.stringify(body) });
}
