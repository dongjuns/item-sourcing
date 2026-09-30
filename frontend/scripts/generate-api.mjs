import { spawnSync } from "node:child_process";
import { writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import openapiTS, { astToString } from "openapi-typescript";

const backend = fileURLToPath(new URL("../../backend/", import.meta.url));
const python = fileURLToPath(
  new URL("../../backend/.venv/bin/python", import.meta.url),
);
const result = spawnSync(python, ["-m", "scripts.export_openapi"], {
  cwd: backend,
  encoding: "utf8",
  maxBuffer: 10_000_000,
});
if (result.status !== 0) {
  throw new Error("API 타입 생성 실패. 백엔드 의존성과 스키마를 확인하세요.");
}
const schema = JSON.parse(result.stdout);
const ast = await openapiTS(schema);
await writeFile(
  new URL("../src/api/schema.d.ts", import.meta.url),
  astToString(ast),
);
console.log("백엔드 OpenAPI에서 API 타입을 생성했습니다.");
