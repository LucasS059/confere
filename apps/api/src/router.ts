import { router } from "./index";
import { authModule } from "./modules/auth";
import { healthModule } from "./modules/health";
import { projectRouter } from "./modules/project";

export const appRouter = router({
  healthCheck: healthModule,
  privateData: authModule,
  project: projectRouter,
});

export type AppRouter = typeof appRouter;
