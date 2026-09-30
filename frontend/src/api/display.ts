export function money(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') return '미확인';
  const number = Number(value);
  return Number.isFinite(number) ? new Intl.NumberFormat('ko-KR').format(number) : '미확인';
}

export function statusLabel(value: string): string {
  const labels: Record<string, string> = {
    complete: '수집 완료', partial: '일부 누락', failed: '실패', queued: '대기', running: '진행 중',
    succeeded: '완료', interrupted: '중단', draft: '검토 중', confirmed: '확정', registered: '등록 완료',
    ready: '저장 완료', mock: '연습', live: '실연동', mixed: '혼합', unknown: '과금 확인 필요',
    settled: '정산 완료', reserved: '예약', released: '예약 해제',
  };
  return labels[value] || value;
}
