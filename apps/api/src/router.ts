import { protectedProcedure, publicProcedure, router } from "./index";
import { authModule } from "./modules/auth";
import { healthModule } from "./modules/health";

export const appRouter = router({
  healthCheck: healthModule,
  privateData: authModule,
});
export type AppRouter = typeof appRouter;
