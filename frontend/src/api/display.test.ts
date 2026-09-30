import { describe, expect, it } from "vitest";
import { money, statusLabel } from "./display";

describe("금액과 상태 표시", () => {
  it("미확인 금액과 0원을 구분한다", () => {
    expect(money(null)).toBe("미확인");
    expect(money(undefined)).toBe("미확인");
    expect(money("0")).toBe("0");
    expect(money("37750")).toBe("37,750");
  });
  it("연습 상태를 실제 상태와 구분한다", () => {
    expect(statusLabel("mock")).not.toBe(statusLabel("live"));
    expect(statusLabel("partial")).not.toBe(statusLabel("succeeded"));
  });
});
