import { types as T, healthUtil } from "../deps.ts";

export const health: T.ExpectedExports.health = {
  async "api"(effects, duration) {
    return healthUtil
      .checkWebUrl("http://localhost:8000/health")(effects, duration)
      .catch(healthUtil.catchError(effects));
  },
};
