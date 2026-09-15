import { protectedProcedure } from "../../index";
import { AuthService } from "./service";

export const authModule = protectedProcedure.query(({ ctx }) =>
  AuthService.privateData(ctx),
);
